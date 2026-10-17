import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('ergenos-hyprland-clipboard')

class ClipboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.env = os.environ | {'ERGENOS_HYPRLAND_RUNTIME': str(self.root), 'PATH': str(self.bin) + ':' + os.environ['PATH']}
        self.cli = ['cliphist', '-config-path', '/dev/null', '-db-path', str(self.root / 'clipboard.db')]

    def tearDown(self):
        self.temp.cleanup()

    def run_helper(self, mode, data=b'', state='data'):
        return subprocess.run([sys.executable, str(SCRIPT), mode], input=data,
                              env=self.env | {'CLIPBOARD_STATE': state}, capture_output=True, check=True)

    def stub(self, name, body):
        path = self.bin / name
        path.write_text('#!/bin/sh\n' + body + '\n')
        path.chmod(0o755)

    def test_text_and_binary_are_preserved(self):
        for data in (b'  first line\nsecond line\n', b'\x89PNG\r\n\x1a\n\x00\xff\x00sample'):
            self.run_helper('store', data)
            self.assertEqual((self.root / 'clipboard.db').stat().st_mode & 0o777, 0o600)
            listing = subprocess.check_output(self.cli + ['list'])
            self.assertEqual(subprocess.check_output(self.cli + ['decode'], input=listing.splitlines()[0]), data)

    def test_sensitive_and_oversized_data_are_not_stored(self):
        for state in ('sensitive', 'nil', 'clear', 'unknown'):
            self.run_helper('store', b'secret', state)
        self.run_helper('store', b'x' * (2 * 1024 * 1024 + 1))
        self.assertFalse((self.root / 'clipboard.db').exists())

    def test_cancel_does_not_replace_clipboard(self):
        self.run_helper('store', b'example')
        self.stub('fuzzel', 'exit 1')
        self.stub('wl-copy', 'touch "' + str(self.root / 'unexpected') + '"')
        self.run_helper('show')
        self.assertFalse((self.root / 'unexpected').exists())

    def test_picker_restores_exact_data(self):
        data = b'  example\nsecond line\n'
        self.run_helper('store', data)
        self.stub('fuzzel', 'head -n 1')
        self.stub('wl-copy', 'cat > "' + str(self.root / 'copied') + '"')
        self.run_helper('show')
        self.assertEqual((self.root / 'copied').read_bytes(), data)

if __name__ == '__main__':
    unittest.main()
