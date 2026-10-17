import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('window_safety', Path(__file__).with_name('window-safety.py'))
safety = importlib.util.module_from_spec(spec)
spec.loader.exec_module(safety)


def window(**changes):
    return dict(address='0xab', pid=100, mapped=True, hidden=False, floating=False,
                fullscreen=0, grouped=[], size=[616, 716], monitor=0, **changes)


def monitor(scale=1.5, **changes):
    return dict(id=0, width=1920, height=1200, scale=scale, reserved=[0, 52, 0, 0], **changes)


class SafetyTests(unittest.TestCase):
    def test_half_width_policy_at_four_scales(self):
        for scale in [1, 1.25, 1.5, 2]:
            w = window()
            w['size'] = [int(1920 / scale / 2 - 24), int(1200 / scale - 84)]
            action = safety.plan(w, monitor(scale), [940, 500])
            self.assertEqual(action[0], 'float')
        w = window(); w['size'] = [1248, 716]
        self.assertIsNone(safety.plan(w, monitor(), [940, 500]))

    def test_responsive_gtk_fits_half_and_quarter(self):
        for size in [[616, 716], [616, 350], [360, 300]]:
            w = window(); w['size'] = size
            self.assertIsNone(safety.plan(w, monitor(), [360, 300]))

    def test_float_fullscreen_hidden_grouped_not_changed(self):
        for key, value in [('floating', True), ('fullscreen', 1), ('hidden', True),
                           ('mapped', False), ('grouped', ['0xaa'])]:
            w = window(); w[key] = value
            self.assertIsNone(safety.plan(w, monitor(), [940, 500]))

    def test_unknown_apps_untouched_and_known_apps_debounced(self):
        guard = safety.Guard(); w = window(); w['class'] = 'Unknown'
        self.assertEqual(guard.inspect([w], [monitor()], safety.DEFAULTS, 0), [])
        w['class'] = 'Discord'
        self.assertEqual(guard.inspect([w], [monitor()], safety.DEFAULTS, 0), [])
        self.assertEqual(guard.inspect([w], [monitor()], safety.DEFAULTS, 1), [])
        self.assertEqual(len(guard.inspect([w], [monitor()], safety.DEFAULTS, 2)), 1)
        self.assertEqual(guard.inspect([w], [monitor()], safety.DEFAULTS, 10), [])
        guard.inspect([], [monitor()], safety.DEFAULTS, 11)
        guard.inspect([w], [monitor()], safety.DEFAULTS, 12)
        self.assertEqual(len(guard.inspect([w], [monitor()], safety.DEFAULTS, 14)), 1)

    def test_animations_reset_stabilization(self):
        guard = safety.Guard(); w = window(); w['class'] = 'discord'
        guard.inspect([w], [monitor()], safety.DEFAULTS, 0)
        w['size'] = [600, 700]
        self.assertEqual(guard.inspect([w], [monitor()], safety.DEFAULTS, 1.4), [])
        self.assertEqual(guard.inspect([w], [monitor()], safety.DEFAULTS, 2), [])
        self.assertEqual(len(guard.inspect([w], [monitor()], safety.DEFAULTS, 3)), 1)

    def test_display_too_small_is_explicit(self):
        self.assertEqual(safety.plan(window(), monitor(2.5), [940, 500]), ('maximize', False))

    def test_profiles_support_add_disable_and_validation(self):
        enabled, profiles = safety.validate({'profiles': {'Discord': False, 'custom': [800, 500]}})
        self.assertTrue(enabled); self.assertNotIn('discord', profiles)
        self.assertEqual(profiles['custom'], [800, 500])
        for data in [{'enabled': 'false'}, {'profiles': []}, {'profiles': {'x': [True, 300]}},
                     {'profiles': {'x': [0, 900]}}, {'unknown': 1}]:
            with self.assertRaises(ValueError): safety.validate(data)

    def test_target_validation_and_no_focus_or_global_commands(self):
        w = window()
        with patch.object(safety, 'dispatch') as dispatch:
            safety.apply(w, ('float', 1000, 600))
            self.assertEqual(dispatch.call_count, 3)
            for call in dispatch.call_args_list:
                self.assertIn('address:0xab', call.args[0])
                self.assertNotIn('focus', call.args[0])
            w['address'] = '0xab"}); bad()'
            with self.assertRaises(ValueError): safety.apply(w, ('float', 1000, 600))


if __name__ == '__main__':
    unittest.main()
