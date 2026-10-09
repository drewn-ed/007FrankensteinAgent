import json,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from unittest.mock import patch
from workbench.browser_control import BrowserControl
from workbench.model import Budget

# Fault injection for a real validation boundary: "1 registered" is a substring of "11 registered".
b=BrowserControl(); b.cached={"origin":"https://workspace.demo","url":"https://workspace.demo/","text":"11 registered", "elements":[{"name":"Name","tag":"input","ref":"e1"}]}
plan={"origin":b.cached["origin"],"steps":[{"action":"fill","target":{"name":"Name","tag":"input"},"value":"Test"}],"expected_text":["1 registered"]}
with patch.object(b,"request"),patch.object(b,"act"):
 result=b.run_plan(plan,Budget(),lambda *a,**kw:None)
print(json.dumps({"check":"wrong_count_substring","observed_page":"11 registered","expected":"1 registered","accepted":result["observed"]}),flush=True)
b.close()

hits=[]
class Other(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  hits.append(self.path);self.send_response(200);self.end_headers();self.wfile.write(b"synthetic")
other=ThreadingHTTPServer(("127.0.0.1",0),Other)
class Allowed(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  if self.path=="/redirect":
   self.send_response(302);self.send_header("Location",f"http://127.0.0.1:{other.server_port}/cross-origin-probe");self.end_headers()
  else:
   self.send_response(200);self.send_header("Content-Type","text/html");self.end_headers();self.wfile.write(b'<html><body><h1>Allowed synthetic page</h1><img src="/redirect"></body></html>')
allowed=ThreadingHTTPServer(("127.0.0.1",0),Allowed)
for server in (allowed,other):threading.Thread(target=server.serve_forever,daemon=True).start()
browser=BrowserControl()
try:
 browser.connect(f"http://127.0.0.1:{allowed.server_port}/",headless=True)
 print(json.dumps({"check":"redirect_origin_scope","allowed_origin":browser.cached["origin"],"other_origin_request_count":len(hits),"paths":hits}),flush=True)
finally:
 browser.close()
 for server in (allowed,other):server.shutdown();server.server_close()
