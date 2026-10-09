"""Synthetic auth/transport fixtures. Never use real account credentials."""
import io
import json
import tempfile
import time
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit, parse_qs

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from workbench.chatgpt_auth import ChatGPTAuth, ISSUER, PLAN_SCOPE, validate_identity
from workbench.config import Config
from workbench.model import Budget, RunError
from workbench.providers import ChatGPTModel, response_usage, safe_error


class AuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(cls.key.public_key()))
        cls.jwk.update(kid="test", alg="RS256")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.auth = ChatGPTAuth(Path(self.temp.name) / "credentials")

    def tearDown(self):
        self.temp.cleanup()

    def token(self, **overrides):
        claims = {"iss": ISSUER, "aud": "oaiapp_test", "sub": "synthetic-subject",
                  "iat": int(time.time()), "exp": int(time.time()) + 600, "nonce": "test-nonce"}
        return jwt.encode({**claims, **overrides}, self.key, algorithm="RS256", headers={"kid": "test"})

    def test_oidc_checks_signature_issuer_audience_expiry_and_nonce(self):
        with patch('workbench.chatgpt_auth.request_json', return_value={"keys": [self.jwk]}):
            self.assertEqual(validate_identity(self.token(), 'oaiapp_test', 'test-nonce')["sub"], "synthetic-subject")
            for claims in [{"iss": "https://wrong.test"}, {"aud": "wrong"}, {"exp": 1}, {"nonce": "wrong"}]:
                with self.assertRaises(RunError):
                    validate_identity(self.token(**claims), 'oaiapp_test', 'test-nonce')
            with self.assertRaises(RunError):
                validate_identity(jwt.encode({"sub":"fake"}, 'synthetic-secret-for-negative-test-only', algorithm='HS256'), 'oaiapp_test')

    def test_new_registration_uses_issued_client_private_storage_and_one_time_state(self):
        query = {k:v[0] for k,v in parse_qs(urlsplit(self.auth.begin('http://127.0.0.1:8767/auth/callback')).query).items()}
        tokens = {"access_token": "synthetic-access", "refresh_token": "synthetic-refresh",
                  "id_token": self.token(nonce=query['nonce']), "scope": PLAN_SCOPE, "token_type": "Bearer", "expires_in": 600}
        def reply(url, **kwargs):
            if url.endswith('jwks.json'):
                return {"keys": [self.jwk]}
            self.assertEqual(kwargs['form']['client_id'], 'oaiapp_test')
            self.assertNotEqual(kwargs['form']['client_id'], 'dynamic_agent_client')
            self.assertEqual(kwargs['form']['redirect_uri'], query['redirect_uri'])
            return tokens
        callback = {"state": query['state'], "code": "synthetic-code", "client_id": "oaiapp_test"}
        with patch('workbench.chatgpt_auth.request_json', side_effect=reply):
            result = self.auth.finish(callback)
        self.assertTrue(result['connected'])
        self.assertNotIn('synthetic-access', json.dumps(result))
        self.assertEqual(self.auth.path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.auth.access_token(), 'synthetic-access')
        with self.assertRaises(RunError):
            self.auth.finish(callback)
        again = parse_qs(urlsplit(self.auth.begin(query['redirect_uri'], result['active'])).query)
        self.assertEqual(again['client_id'], ['oaiapp_test'])
        self.assertEqual(again['ext_agent_host_id'], [query['ext_agent_host_id']])
        self.assertNotIn('agent_name_hint', again)

    def test_unverified_or_denied_callback_never_exchanges_code(self):
        q = parse_qs(urlsplit(self.auth.begin('http://127.0.0.1:8767/auth/callback')).query)
        with patch('workbench.chatgpt_auth.request_json') as request:
            for callback in [{"state": "wrong", "code": "x"}, {"state": q['state'][0], "error": "access_denied"}]:
                with self.assertRaises(RunError):
                    self.auth.finish(callback)
            request.assert_not_called()
        self.assertFalse(self.auth.status()['connected'])

    def test_identity_alone_cannot_enable_plan_usage(self):
        q = parse_qs(urlsplit(self.auth.begin('http://127.0.0.1:8767/auth/callback')).query)
        tokens = {"id_token": self.token(nonce=q['nonce'][0]), "access_token":"synthetic", "scope":"openid", "token_type":"Bearer"}
        with patch('workbench.chatgpt_auth.request_json', side_effect=[tokens, {"keys":[self.jwk]}]):
            with self.assertRaisesRegex(RunError, 'not granted'):
                self.auth.finish({"state": q['state'][0], "code":"x", "client_id":"oaiapp_test"})
        self.assertFalse(self.auth.status()['connected'])


class TransportTests(unittest.TestCase):
    def model(self):
        class AuthFixture:
            def status(self): return {"connected": True}
            def access_token(self): return 'synthetic-token'
        return ChatGPTModel(replace(Config(), provider='chatgpt', model='fixture-model', spend_policy='existing_plan'), AuthFixture())

    def event_stream(self, *events):
        return io.BytesIO(''.join('data: ' + json.dumps(e) + '\n\n' for e in events).encode())

    def test_completion_records_usage_without_double_counting_reasoning(self):
        usage = {"input_tokens": 10, "output_tokens": 8, "total_tokens": 18,
                 "input_tokens_details":{"cached_tokens":2}, "output_tokens_details":{"reasoning_tokens":3}}
        event = {"type":"response.completed", "response":{"status":"completed", "usage":usage,
                 "output":[{"type":"message", "content":[{"type":"output_text", "text":'{"ok":true}'}]}]}}
        with patch('workbench.providers.open_direct', return_value=self.event_stream(event)) as request:
            budget = Budget()
            self.assertEqual(self.model().ask('Return JSON', {}, budget), {"ok":True})
            body = json.loads(request.call_args.args[0].data)
            self.assertTrue(body['stream'])
            self.assertFalse(body['store'])
            self.assertIsInstance(body['input'], list)
            self.assertTrue(any(m['role'] == 'developer' and 'json' in m['content'].lower() for m in body['input']))
            self.assertEqual(json.loads(body['input'][-1]['content']), {})
            self.assertNotIn('max_output_tokens', body)
            self.assertNotIn('previous_response_id', body)
            self.assertEqual(budget.tokens, 18)
            self.assertEqual(budget.usage[0]['pricing']['tier'], 'chatgpt_plan')
            self.assertEqual(budget.usage[0]['usage']['output'], 5)

    def test_missing_terminal_event_and_subscription_failure_are_not_success(self):
        for event in [{"type":"response.output_text.delta", "delta":'{"ok":true}'},
                      {"type":"response.failed", "response":{"error":{"code":"subscription_sharing_usage_limit_exceeded"}}}]:
            with patch('workbench.providers.open_direct', return_value=self.event_stream(event)) as request:
                budget = Budget()
                with self.assertRaises(RunError): self.model().ask('Return JSON', {}, budget)
                self.assertEqual(request.call_count, 1)
                self.assertEqual(budget.usage[0]['status'], 'failed')

    def test_empty_terminal_output_uses_streamed_text_once_after_success(self):
        events = [
            {'type': 'response.output_text.delta', 'output_index': 0, 'content_index': 0, 'delta': '{"ok":'},
            {'type': 'response.output_text.delta', 'output_index': 0, 'content_index': 0, 'delta': 'true}'},
            {'type': 'response.output_text.done', 'output_index': 0, 'content_index': 0, 'text': '{"ok":true}'},
            {'type': 'response.completed', 'response': {'status': 'completed', 'output': []}},
        ]
        with patch('workbench.providers.open_direct', return_value=self.event_stream(*events)):
            self.assertEqual(self.model().ask('Return JSON', {}, Budget()), {'ok': True})
        events[-1] = {'type': 'response.failed', 'response': {'error': {'code': 'subscription_sharing_usage_limit_exceeded'}}}
        with patch('workbench.providers.open_direct', return_value=self.event_stream(*events)):
            with self.assertRaisesRegex(RunError, 'usage limit'):
                self.model().ask('Return JSON', {}, Budget())

    def test_invalid_usage_is_unpriced_and_call_limit_prevents_network(self):
        self.assertIsNone(response_usage({"input_tokens":10, "output_tokens":1, "total_tokens":999}))
        with patch('workbench.providers.open_direct') as request:
            with self.assertRaises(RunError): self.model().ask('JSON', {}, Budget(max_calls=0))
            request.assert_not_called()

    def test_invalid_request_retains_safe_type_and_field_without_echoing_content(self):
        error = {'code': None, 'type': 'invalid_request_error', 'param': 'input', 'message': 'sensitive fixture'}
        self.assertEqual(safe_error(error), 'OpenAI response failed: invalid_request_error (field: input)')
        self.assertNotIn('sensitive fixture', safe_error(error))


if __name__ == '__main__':
    unittest.main()
