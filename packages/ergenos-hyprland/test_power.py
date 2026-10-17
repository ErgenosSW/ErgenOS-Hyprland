import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from power_config import DEFAULTS, load, save, render, validate

class PowerTests(unittest.TestCase):
    def test_defaults_do_not_suspend_or_override_lid(self):
        self.assertNotIn('idle-suspend', render(DEFAULTS))
        self.assertEqual(DEFAULTS['lid_ac'], 'system')
        self.assertEqual(DEFAULTS['lid_battery'], 'system')
        self.assertIn('before_sleep_cmd = loginctl lock-session', render(DEFAULTS))

    def test_invalid_input_cannot_generate_commands(self):
        for data in ({'lock': True}, {'display': -1}, {'lid_ac': 'suspend; reboot'},
                     {'dock_guard': 1}, {'unknown': 123}, {'suspend_ac': 42}):
            with self.assertRaises(ValueError):
                validate(data)

    def test_each_power_source_has_its_own_suspend_condition(self):
        text = render(DEFAULTS | {'suspend_ac': 1800, 'suspend_battery': 900, 'lock': 0})
        self.assertIn('idle-suspend ac', text)
        self.assertIn('idle-suspend battery', text)
        self.assertNotIn('on-timeout = loginctl lock-session', text)

    def test_atomic_round_trip_and_corrupt_file(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, XDG_CONFIG_HOME=folder):
            self.assertEqual(load(), DEFAULTS)
            data = DEFAULTS | {'lock': 900, 'lid_battery': 'lock'}
            save(data)
            self.assertEqual(load(), data)
            path = Path(folder) / 'ergenos-hyprland/power.json'
            self.assertFalse(path.with_suffix('.tmp').exists())
            path.write_text('{bad')
            with self.assertRaises(ValueError):
                load()

if __name__ == '__main__':
    unittest.main()
