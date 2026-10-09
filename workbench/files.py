"""User-provided files and run artifacts, separate from the generated-code sandbox."""
import base64
import json
import mimetypes
import re
import threading
import uuid
from pathlib import Path
from .model import RunError

MAX_FILE = 10 * 1024 * 1024
TEXT_TYPES = {'.txt', '.md', '.csv', '.json', '.tsv', '.log'}

class FileVault:
    def __init__(self, directory):
        self.root = (directory / 'files').resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.lock = threading.RLock()

    def put(self, name, content, *, run_id=None, source='upload'):
        if not isinstance(name, str) or not 1 <= len(name) <= 180 or Path(name).name != name or any(c in name for c in '\\/:\r\n\0'):
            raise RunError('Use a plain file name, without a directory.')
        if not isinstance(content, bytes) or not 0 < len(content) <= MAX_FILE:
            raise RunError('Files must be between 1 byte and 10 MB.')
        ident = uuid.uuid4().hex
        folder = self.root / ident
        folder.mkdir(mode=0o700)
        path = folder / 'content'
        path.write_bytes(content); path.chmod(0o600)
        meta = {'id': ident, 'name': name, 'size': len(content), 'mime': mimetypes.guess_type(name)[0] or 'application/octet-stream', 'run_id': run_id, 'source': source}
        (folder / 'meta.json').write_text(json.dumps(meta))
        return meta

    def upload(self, body):
        try:
            raw = base64.b64decode(body.get('base64', ''), validate=True)
        except (ValueError, TypeError):
            raise RunError('Invalid file encoding.') from None
        return self.put(body.get('name'), raw)

    def get(self, ident):
        if not isinstance(ident, str) or not re.fullmatch('[a-f0-9]{32}', ident):
            raise RunError('Invalid file identifier.')
        folder = self.root / ident
        try:
            meta = json.loads((folder / 'meta.json').read_text())
        except (OSError, ValueError):
            raise RunError('This file is no longer available.') from None
        return meta, folder / 'content'

    def input_files(self, inputs):
        """Only explicit attachments grant upload permission; paths never reach the model."""
        if not isinstance(inputs, dict): return inputs, {}
        result = dict(inputs); entries = []; paths = {}; total = 0
        for item in inputs.get('files', []):
            if not isinstance(item, dict): raise RunError('Invalid attachment.')
            if not item.get('id'):
                entries.append(item); continue  # Legacy text-only attachment.
            meta, path = self.get(item['id']); total += meta['size']
            if total > 20 * 1024 * 1024: raise RunError('Keep attachments under 20 MB per task.')
            entry = {k: meta[k] for k in ('id', 'name', 'size', 'mime')}
            if Path(meta['name']).suffix.lower() in TEXT_TYPES:
                if meta['size'] > 120000: raise RunError('Text attachments sent to the model must be under 120 KB.')
                try: entry['content'] = path.read_text(encoding='utf-8-sig')
                except UnicodeError: raise RunError('Use UTF-8 for text attachments.') from None
            paths[meta['id']] = str(path)
            entries.append(entry)
        result['files'] = entries
        return result, paths
