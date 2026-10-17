"""Check late D-Bus activation without touching the real user manager."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parent

class NotificationTests(unittest.TestCase):
    def check(self, desktop, active):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command = root / 'systemctl'
            command.write_text('#!/bin/sh\nprintf "%s\\n" "$*" > "$TEST_CALL"\nexit "$TEST_STATUS"\n')
            command.chmod(0o755)
            env = dict(os.environ, PATH=str(root)+':'+os.environ['PATH'],
                       XDG_CURRENT_DESKTOP=desktop, TEST_STATUS=str(0 if active else 3),
                       TEST_CALL=str(root/'call'))
            result = subprocess.run(['bash', str(SOURCE/'notification-session-check')], env=env)
            return result.returncode, (root/'call').read_text() if (root/'call').exists() else ''

    def test_active_hyprland_allows_activation(self):
        status, call = self.check('Hyprland', True)
        self.assertEqual(status, 0)
        self.assertIn('--user --quiet is-active ergenos-hyprland-session.target', call)

    def test_stopped_hyprland_skips_without_failed_condition(self):
        status, _ = self.check('Hyprland', False)
        self.assertTrue(1 <= status <= 254)  # systemd ExecCondition skips, not fails.

    def test_colon_separated_desktops(self):
        self.assertNotEqual(self.check('other:Hyprland', False)[0], 0)

    def test_gnome_is_unchanged(self):
        self.assertEqual(self.check('GNOME', False), (0, ''))

    def test_unknown_desktop_is_unchanged(self):
        self.assertEqual(self.check('', False), (0, ''))

if __name__ == '__main__':
    unittest.main()
