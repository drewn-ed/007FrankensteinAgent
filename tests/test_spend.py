"""Financial boundary tests; no provider request is sent by this suite."""
import unittest
from dataclasses import replace
from unittest.mock import Mock, patch
from workbench.config import Config
from workbench.model import Budget, Gemini, RunError
from workbench.providers import ChatGPTModel
from workbench.spend import SpendLedger, SpendError, policy_status


class SpendTests(unittest.TestCase):
    def test_application_blocks_tasks_corrections_and_schedules_before_dispatch(self):
        import threading
        from workbench.server import Application
        app = Application.__new__(Application)
        app.config = Config(provider='chatgpt')
        app.model = Mock(); app.model.ready.return_value = None
        app.store = Mock(); app.store.setting.return_value = False
        app.lock = threading.Lock(); app.future = None; app.pool = Mock()
        for kind in ('task', 'correction'):
            with self.assertRaisesRegex(ValueError, 'Financial limit blocked'):
                app.start('Synthetic task', {}, kind)
        with self.assertRaisesRegex(ValueError, 'Financial limit blocked'):
            app.start_scheduled('Synthetic task', {}, kind='task')
        app.pool.submit.assert_not_called()
        app.store.new_run.assert_not_called()

    def test_api_exposes_policy_and_run_reservations(self):
        import json, tempfile, threading
        from pathlib import Path
        from urllib.request import urlopen
        from workbench.server import Application, WorkspaceHTTPServer, handler_for
        with tempfile.TemporaryDirectory() as directory:
            app = Application(Config(data_dir=Path(directory), key='synthetic', free_confirmed=True))
            server = WorkspaceHTTPServer(('127.0.0.1', 0), handler_for(app, 0))
            # Handler validates Host against the actual port.
            server.RequestHandlerClass = handler_for(app, server.server_port)
            thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
            try:
                base = f'http://127.0.0.1:{server.server_port}'
                with urlopen(base+'/api/state') as response: state = json.load(response)
                self.assertTrue(state['model_ready'])
                self.assertTrue(state['spend_policy']['allowed'])
                self.assertEqual(state['limits']['max_usd'], '0')
                run = app.store.new_run('Synthetic cost record', {})
                ledger = SpendLedger(); ledger.authorize(app.config)
                run['spend_budget'] = ledger.snapshot(); app.store.save_run(run)
                with urlopen(base+'/api/usage/'+run['id']) as response: usage = json.load(response)
                self.assertEqual(usage['spend_budget']['policy'], 'strict')
                self.assertEqual(usage['spend_budget']['reserved_upper_bound_usd'], '0')
            finally:
                server.shutdown(); server.server_close(); thread.join()
                app.pool.shutdown(); app.scheduler.close(); app.browser.close(); app.desktop.close(); app.store.close()

    def test_policy_preview_does_not_disguise_unknown_or_invalid_config(self):
        self.assertTrue(policy_status(Config(free_confirmed=True))['allowed'])
        self.assertFalse(policy_status(Config(provider='chatgpt'))['allowed'])
        self.assertFalse(policy_status(Config(max_run_usd='NaN'))['allowed'])
        status = policy_status(Config(provider='chatgpt', spend_policy='existing_plan'))
        self.assertTrue(status['allowed'])
        self.assertFalse(status['usd_guarantee'])

    def test_reservation_blocks_before_exceeding_including_exact_decimal_boundary(self):
        ledger = SpendLedger("0.30")
        ledger.reserve("0.10", provider="fixed_price_fixture", basis="Synthetic contract")
        ledger.reserve("0.20", provider="fixed_price_fixture", basis="Synthetic contract")
        with self.assertRaisesRegex(SpendError, "exceed"):
            ledger.reserve("0.000000001", provider="fixed_price_fixture", basis="Synthetic contract")
        self.assertEqual(ledger.snapshot()['reserved_upper_bound_usd'], '0.30')
        self.assertEqual(len(ledger.snapshot()['blocked']), 1)

    def test_unknown_price_is_not_zero_and_fails_with_even_large_budget(self):
        ledger = SpendLedger("100")
        with self.assertRaisesRegex(SpendError, "no verified"):
            ledger.reserve(None, provider="chatgpt", basis="No quoted ceiling")
        self.assertEqual(ledger.reservations, [])
        self.assertIsNone(ledger.blocked[0]['upper_bound_usd'])

    def test_invalid_money_and_policy_fail_closed(self):
        for value in ('NaN', 'Infinity', '-0.01', '101', None, 'garbage', True):
            with self.subTest(value=value), self.assertRaises(SpendError):
                SpendLedger(value)
        with self.assertRaises(SpendError): SpendLedger('0', 'disable')

    def test_zero_cap_allows_only_operator_confirmed_free_allowlisted_route(self):
        config = Config(key='synthetic', free_confirmed=True)
        ledger = SpendLedger('0')
        self.assertTrue(ledger.authorize(config)['admitted'])
        self.assertEqual(ledger.snapshot()['reserved_upper_bound_usd'], '0')
        self.assertFalse(ledger.snapshot()['billing_verified'])
        for other in (replace(config, free_confirmed=False), replace(config, model='unknown'),
                      replace(config, provider='other')):
            with self.subTest(provider=other.provider, model=other.model), self.assertRaises(SpendError):
                ledger.authorize(other)

    def test_chatgpt_strict_blocks_before_token_refresh_and_network(self):
        auth = Mock()
        auth.status.return_value = {'connected': True}
        model = ChatGPTModel(Config(provider='chatgpt', model='any-model'), auth)
        budget = Budget()
        with patch('workbench.providers.open_direct') as request:
            with self.assertRaisesRegex(RunError, 'Financial limit blocked'):
                model.ask('JSON', {}, budget)
        auth.access_token.assert_not_called()
        request.assert_not_called()
        self.assertEqual(budget.calls, 0)
        self.assertEqual(len(budget.spend.blocked), 1)

    def test_explicit_plan_mode_never_claims_dollar_guarantee(self):
        ledger = SpendLedger('0', 'existing_plan')
        entry = ledger.authorize(Config(provider='chatgpt'))
        self.assertIsNone(entry['upper_bound_usd'])
        self.assertFalse(ledger.snapshot()['guaranteed'])
        with self.assertRaises(SpendError):
            ledger.reserve(None, provider='other', basis='Unknown billing')

    def test_failed_request_keeps_reservation_and_next_call_is_blocked(self):
        ledger = SpendLedger('0.01')
        ledger.reserve('0.01', provider='fixed_price_fixture', basis='Synthetic contract')
        # No settlement/refund after a timeout: uncertain usage remains reserved.
        with self.assertRaises(SpendError):
            ledger.reserve('0.01', provider='fixed_price_fixture', basis='Synthetic contract')
        self.assertEqual(ledger.snapshot()['reserved_upper_bound_usd'], '0.01')

    def test_gemini_failure_persists_admission_without_fallback(self):
        model = Gemini(Config(key='synthetic', free_confirmed=True))
        budget = Budget()
        with patch.object(model, '_request', side_effect=RunError('Synthetic timeout')) as request:
            with self.assertRaisesRegex(RunError, 'Synthetic timeout'):
                model.ask('JSON', {}, budget)
        self.assertEqual(request.call_count, 1)
        self.assertEqual(budget.calls, 1)
        self.assertTrue(budget.usage[0]['spend_admission']['admitted'])
        self.assertEqual(budget.usage[0]['status'], 'failed')
        self.assertEqual(len(budget.spend.reservations), 1)


if __name__ == '__main__':
    unittest.main()
