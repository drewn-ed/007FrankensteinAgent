"""Generated Python executes only inside a credential-free Docker container."""
import json
import os
import selectors
import subprocess
import time
import uuid
from .model import RunError

RUNNER = '''import sys,json,contextlib
payload=json.load(sys.stdin)
namespace={"__name__":"capability"}
with contextlib.redirect_stdout(sys.stderr):
    exec(compile(payload["code"],"<capability>","exec"),namespace)
    result=namespace["run"](payload["input"])
print(json.dumps(result,ensure_ascii=False,allow_nan=False))
'''


class Sandbox:
    def __init__(self, image="python:3.12-slim", timeout=8):
        self.image = image
        self.timeout = timeout

    def status(self):
        try:
            proc = subprocess.run(["docker", "image", "inspect", self.image],
                                  capture_output=True, timeout=3)
            return proc.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False

    def run(self, code, data, timeout=None):
        packet = json.dumps({"code": code, "input": data}, allow_nan=False).encode()
        if len(packet) > 180_000 or len(code) > 60_000:
            raise RunError("Vstup do sandboxu překročil limit velikosti.")
        name = "learning-" + uuid.uuid4().hex
        command = ["docker", "run", "--rm", "-i", "--pull=never", "--name", name,
                   "--network=none", "--read-only", "--cap-drop=ALL",
                   "--security-opt=no-new-privileges", "--user=65534:65534",
                   "--pids-limit=32", "--memory=128m", "--memory-swap=128m", "--cpus=0.5",
                   "--ulimit=cpu=4:4", "--ulimit=nofile=64:64", "--ulimit=fsize=1048576:1048576",
                   "--tmpfs=/tmp:rw,noexec,nosuid,size=16m", "--log-driver=none",
                   self.image, "python", "-I", "-B", "-c", RUNNER]
        proc = None
        started = time.monotonic()
        limit = min(self.timeout, timeout) if timeout is not None else self.timeout
        try:
            proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            for pipe in (proc.stdin, proc.stdout, proc.stderr):
                os.set_blocking(pipe.fileno(), False)
            out, err = bytearray(), bytearray()
            sent = 0
            with selectors.DefaultSelector() as sel:
                sel.register(proc.stdin, selectors.EVENT_WRITE, "in")
                sel.register(proc.stdout, selectors.EVENT_READ, "out")
                sel.register(proc.stderr, selectors.EVENT_READ, "err")
                while sel.get_map():
                    if time.monotonic() - started > limit:
                        raise RunError("Sandbox překročil časový limit.")
                    for key, _ in sel.select(0.05):
                        if key.data == "in":
                            try:
                                sent += os.write(key.fd, packet[sent:sent + 4096])
                            except BrokenPipeError:
                                sent = len(packet)
                            if sent == len(packet):
                                sel.unregister(key.fileobj)
                                key.fileobj.close()
                        else:
                            chunk = os.read(key.fd, 4096)
                            if not chunk:
                                sel.unregister(key.fileobj)
                                key.fileobj.close()
                            else:
                                (out if key.data == "out" else err).extend(chunk)
                                if len(out) + len(err) > 64_000:
                                    raise RunError("Sandbox překročil limit výstupu.")
                proc.wait(timeout=1)
            if proc.returncode:
                # Keep generated diagnostics separate from trusted status.
                raise RunError("Schopnost v sandboxu selhala: " + err.decode(errors="replace")[-1200:])
            try:
                return json.loads(out, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
            except ValueError:
                raise RunError("Schopnost nevrátila platný JSON.") from None
        except FileNotFoundError:
            raise RunError("Docker není dostupný; spuštění na hostiteli není dovoleno.") from None
        finally:
            if proc is not None:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait(timeout=3)
                for pipe in (proc.stdin, proc.stdout, proc.stderr):
                    if pipe and not pipe.closed:
                        pipe.close()
            try:
                subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=3)
            except (OSError, subprocess.TimeoutExpired):
                pass

