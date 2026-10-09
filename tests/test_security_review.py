"""Focused security regressions: synthetic keys and loopback fixtures only."""
import http.client
import tempfile
import threading
import unittest
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import Mock
from urllib.error import HTTPError
from urllib.request import Request
from workbench.model import provider_open
from workbench.server import WorkspaceHTTPServer, handler_for
from workbench.store import Store
from workbench.browser_control import BrowserControl
from workbench.model import Budget, RunError

class SecurityReview(unittest.TestCase):
    def test_external_navigation_waits_for_operator_and_decline_does_not_navigate(self):
        browser=BrowserControl();browser.cached={'connected':True,'origin':'https://external.example'}
        browser.request=Mock()
        def event(kind,message,**data):
            self.assertEqual(kind,'approval');browser.approve(False)
        with self.assertRaisesRegex(RunError,'declined'):
            browser.act({'action':'navigate','value':'https://external.example/change'},Budget(),event)
        browser.request.assert_not_called()
        self.assertIsNone(browser.pending)

    def test_existing_workspace_and_database_become_owner_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);root.chmod(0o755)
            db=root/'workbench.sqlite';db.touch();db.chmod(0o644)
            store=Store(root)
            try:
                self.assertEqual(root.stat().st_mode & 0o777,0o700)
                self.assertEqual(db.stat().st_mode & 0o777,0o600)
            finally:store.close()

    def test_provider_redirect_never_delivers_key_to_second_server(self):
        received=[]
        class Sink(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):
                received.append(self.headers.get('x-goog-api-key'));self.send_response(200);self.end_headers()
            do_POST=do_GET
        sink=ThreadingHTTPServer(('127.0.0.1',0),Sink)
        class Redirect(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_POST(self):
                self.send_response(302);self.send_header('Location',f'http://127.0.0.1:{sink.server_port}/capture');self.end_headers()
        redirect=ThreadingHTTPServer(('127.0.0.1',0),Redirect)
        threads=[]
        try:
            for server in (sink,redirect):
                thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();threads.append(thread)
            request=Request(f'http://127.0.0.1:{redirect.server_port}/model',data=b'{}',headers={'x-goog-api-key':'synthetic-security-canary'})
            with self.assertRaises(HTTPError) as error:provider_open(request,timeout=2)
            self.assertEqual(error.exception.code,302);self.assertEqual(received,[])
        finally:
            for server in (redirect,sink):server.shutdown();server.server_close()
            for thread in threads:thread.join()

    def test_untrusted_browser_origin_and_host_cannot_change_blackout(self):
        app=Mock();server=WorkspaceHTTPServer(('127.0.0.1',0),handler_for(app,0))
        port=server.server_port;server.RequestHandlerClass=handler_for(app,port)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            for headers in ({'Host':f'127.0.0.1:{port}','Origin':'https://attacker.invalid'},
                            {'Host':f'attacker.invalid:{port}'},
                            {'Host':f'127.0.0.1:{port}','Origin':'null'}):
                conn=http.client.HTTPConnection('127.0.0.1',port,timeout=2)
                try:
                    conn.request('POST','/api/blackout',body='{"paused":false}',headers={**headers,'Content-Type':'application/json'})
                    reply=conn.getresponse();self.assertEqual(reply.status,403);reply.read()
                finally:conn.close()
            app.set_blackout.assert_not_called()
        finally:server.shutdown();server.server_close();thread.join()
