"""Real process/lock regression for shutdown ordering, without ending the session."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT = Path(__file__).with_name('ergenos-hyprland-exit')
SUPERVISOR = '''
import os,fcntl,signal,time
from pathlib import Path
root=Path(os.environ['ERGENOS_HYPRLAND_RUNTIME'])
f=(root/'services.lock').open('w');fcntl.flock(f,fcntl.LOCK_EX)
(root/'services.pid').write_text(str(os.getpid()))
def stop(*args):
 time.sleep(.2)
 (root/'stopped').touch()
 (root/'services.pid').unlink()
 (root/'services.lock').unlink()
 raise SystemExit(0)
signal.signal(signal.SIGTERM,stop)
while True:time.sleep(.05)
'''

class ExitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.env = os.environ | {'ERGENOS_HYPRLAND_RUNTIME': str(self.root), 'PATH': str(self.bin) + ':' + os.environ['PATH']}
        for command in ('hyprctl', 'systemctl'):
            file = self.bin / command
            file.write_text('''#!/usr/bin/env python3
import os,sys
from pathlib import Path
root=Path(os.environ['ERGENOS_HYPRLAND_RUNTIME'])
assert (root/'stopped').exists(), 'Shutdown called before services stopped'
with (root/'commands').open('a') as f:f.write(' '.join(sys.argv[1:])+'\\n')
if os.environ.get('REFUSE') and 'hl.dsp.exit()' in sys.argv:
 print('refused',file=sys.stderr);sys.exit(1)
print('ok')
''')
            file.chmod(0o755)
        file = self.bin / 'notify-send';file.write_text('#!/bin/sh\nexit 0\n');file.chmod(0o755)
        self.process = subprocess.Popen([sys.executable, '-c', SUPERVISOR, '/usr/lib/ergenos-hyprland/session-services'], env=self.env)
        self.addCleanup(self.cleanup_process)
        for _ in range(100):
            if (self.root / 'services.pid').exists():break
            time.sleep(.01)
        self.assertTrue((self.root / 'services.pid').exists())

    def cleanup_process(self):
        if self.process.poll() is None:self.process.terminate()
        self.process.wait(timeout=3)

    def run_exit(self, action):
        return subprocess.run([sys.executable, str(SCRIPT), action], env=self.env, capture_output=True, text=True, timeout=5)

    def test_logout_waits_for_runner_cleanup(self):
        result = self.run_exit('logout')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / 'commands').read_text().strip(), 'dispatch hl.dsp.exit()')
        self.process.wait(timeout=2)
        self.assertEqual(self.process.returncode, 0)

    def test_reboot_waits_for_runner_cleanup(self):
        result = self.run_exit('reboot')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / 'commands').read_text().strip(), 'reboot')

    def test_refused_exit_requests_service_recovery(self):
        self.env['REFUSE'] = '1'
        result = self.run_exit('logout')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('hl.dsp.exec_cmd', (self.root / 'commands').read_text())

    def test_missing_session_environment_is_reported_without_traceback(self):
        self.env.pop('ERGENOS_HYPRLAND_RUNTIME')
        result = self.run_exit('logout')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ErgenOS Hyprland session', result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertIsNone(self.process.poll())

    def test_wrong_pid_is_not_signalled(self):
        (self.root / 'services.pid').write_text(str(os.getpid()))
        result = self.run_exit('logout')
        self.assertNotEqual(result.returncode, 0)
        self.assertIsNone(self.process.poll())
        self.assertFalse((self.root / 'commands').exists())

if __name__ == '__main__':
    unittest.main()
