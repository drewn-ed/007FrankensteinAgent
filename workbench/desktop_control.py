"""Fixed Accessibility operations, scoped to one explicitly selected macOS app."""
import platform
import plistlib
import os
import subprocess
import time
from .browser_control import BrowserControl
from .config import ROOT
from .model import RunError

class DesktopControl(BrowserControl):
    kind = 'desktop'

    def command(self):
        if platform.system() != 'Darwin': raise RunError('Native desktop control currently supports macOS.')
        bundle = ROOT / '.runtime/Workspace Desktop Bridge.app'
        binary = bundle / 'Contents/MacOS/WorkspaceDesktop'
        plist = bundle / 'Contents/Info.plist'
        stamp = ROOT / '.runtime/bin/desktop-built'
        (bundle / 'Contents/.built').unlink(missing_ok=True)
        source = ROOT / 'workbench/desktop/bridge.swift'
        if not binary.exists() or not stamp.exists() or stamp.stat().st_mtime < source.stat().st_mtime:
            binary.parent.mkdir(parents=True, exist_ok=True)
            with plist.open('wb') as stream:
                plistlib.dump({'CFBundleIdentifier':'com.frankenstein.workspace.desktop','CFBundleName':'Workspace Desktop Bridge',
                              'CFBundleExecutable':'WorkspaceDesktop','CFBundlePackageType':'APPL','CFBundleVersion':'1','LSUIElement':True}, stream)
            try:
                result = subprocess.run(['swiftc', str(source), '-o', str(binary)], capture_output=True, timeout=90)
            except (OSError, subprocess.TimeoutExpired):
                raise RunError('Install Apple Command Line Tools to build the desktop connector.') from None
            if result.returncode: raise RunError('The native desktop connector did not compile.')
            stamp.parent.mkdir(parents=True, exist_ok=True)
            stamp.write_text('local trusted connector\n')
            # A synced workspace may attach Finder metadata as the bundle is written.
            # Remove only that non-security attribute from our own generated bundle.
            for attempt in range(2):
                subprocess.run(['/usr/bin/xattr', '-d', 'com.apple.FinderInfo', str(bundle)], capture_output=True, timeout=5)
                signed = subprocess.run(['/usr/bin/codesign','--force','--sign','-','--identifier','com.frankenstein.workspace.desktop',str(bundle)], capture_output=True, timeout=15)
                if signed.returncode == 0: break
            if signed.returncode:
                stamp.unlink(missing_ok=True)
                raise RunError('Could not sign the local desktop connector.')
        return [str(binary)]

    def reveal(self):
        self.command()
        subprocess.run(['/usr/bin/open', '-R', str(ROOT / '.runtime/Workspace Desktop Bridge.app')], check=True, timeout=10)
        return {'ok':True}

    def status(self):
        previous = self.cached
        try:
            result = self.request('status')
            self.cached = previous
            return {**result, 'connected': previous.get('connected', False)}
        except RunError as error: return {'available': False, 'connected': False, 'error': str(error)}

    def connect(self, bundle_id):
        return self.request('connect', {'bundle_id': bundle_id})

    def act(self, action, budget, event):
        operation = {key: action[key] for key in ('action', 'ref', 'value') if key in action}
        if operation.get('action') not in ('inspect', 'click', 'fill'): raise RunError('Unsupported desktop action.')
        budget.check()
        if operation['action'] != 'inspect':
            self.decision.clear()
            self.pending = {'operation': operation, 'reason': action.get('reason', 'Review this desktop step.'), 'approved': None}
            event('approval', 'A desktop action is waiting for your review.', operation=operation)
            try:
                while not self.decision.wait(0.2): budget.check()
                budget.check()
                if not self.pending['approved']: raise RunError('You declined the desktop action.')
            finally: self.pending = None
        self.request('act', operation)
        return self.observation()
