"""Integration regressions for XDG startup and persistent display settings."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parent


class IntegrationTests(unittest.TestCase):
    def test_native_xdg_generator_honors_hidden_user_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            user, system = root / 'user', root / 'system'
            for folder in (user, system):
                (folder / 'autostart').mkdir(parents=True)
            (system / 'autostart/example.desktop').write_text('[Desktop Entry]\nType=Application\nName=Example\nExec=/bin/true\n')
            (user / 'autostart/example.desktop').write_text('[Desktop Entry]\nType=Application\nName=Disabled override\nHidden=true\n')
            (system / 'autostart/allowed.desktop').write_text('[Desktop Entry]\nType=Application\nName=Allowed\nExec=/bin/true\nOnlyShowIn=Hyprland;\n')
            output = [root / name for name in ('normal', 'early', 'late')]
            for directory in output:
                directory.mkdir()
            env = os.environ.copy()
            env.update(XDG_CONFIG_HOME=str(user), XDG_CONFIG_DIRS=str(system), XDG_CURRENT_DESKTOP='Hyprland')
            subprocess.run(['/usr/lib/systemd/user-generators/systemd-xdg-autostart-generator', *map(str, output)],
                           env=env, check=True, capture_output=True, timeout=10)
            generated = [p for directory in output for p in directory.rglob('*.service')]
            self.assertFalse(any('example' in p.name for p in generated))
            allowed = [p for p in generated if p.name == 'app-allowed@autostart.service']
            self.assertTrue(allowed)
            self.assertIn('systemd-xdg-autostart-condition', allowed[0].read_text())
            self.assertIn('Hyprland', allowed[0].read_text())

    def test_display_changes_reload_even_with_automatic_reload_disabled(self):
        self.run_display_bridge(False)

    def test_invalid_display_changes_restore_previous_files(self):
        self.run_display_bridge(True)

    def test_deleted_display_file_restores_previous_layout(self):
        self.run_display_bridge(False, deleted=True)

    def test_failed_reload_restores_previous_files(self):
        self.run_display_bridge(False, reload_failed=True)

    def run_display_bridge(self, invalid, deleted=False, reload_failed=False):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binary = root / 'bin'
            binary.mkdir()
            config = root / 'config'
            config.mkdir()
            def stub(name, body):
                path = binary / name
                path.write_text('#!/usr/bin/env python3\n' + body)
                path.chmod(0o755)
            stub('hyprctl', '''import sys,os,json
from pathlib import Path
if 'monitors' in sys.argv:
 print(json.dumps([{'name':'eDP-1','width':1920,'height':1200,'refreshRate':180,'x':0,'y':0,'scale':1.5,'transform':0}]))
else:
 if os.environ.get('TEST_RELOAD_FAILED') == '1': sys.exit(1)
 Path(os.environ['TEST_ROOT'],'reloaded').touch()
''')
            stub('Hyprland', 'import os,sys\nsys.exit(int(os.environ["TEST_INVALID"]))\n')
            stub('notify-send', 'pass\n')
            stub('nwg-displays', '''import sys,time,os
from pathlib import Path
monitor=Path(sys.argv[sys.argv.index('--monitors_path')+1]).with_suffix('.lua')
if os.environ.get('TEST_DELETE') == '1': monitor.unlink()
else: monitor.write_text('-- new saved monitor rules\\n')
time.sleep(1)
''')
            env = os.environ.copy()
            env.update(PATH=str(binary) + ':' + env['PATH'], XDG_CONFIG_HOME=str(config),
                       XDG_RUNTIME_DIR=str(root), TEST_ROOT=str(root), TEST_INVALID=str(int(invalid)), TEST_DELETE=str(int(deleted)),
                       TEST_RELOAD_FAILED=str(int(reload_failed)))
            subprocess.run(['python', str(SOURCE / 'display-settings.py')], env=env,
                           check=True, capture_output=True, timeout=10)
            folder = config / 'ergenos-hyprland/displays'
            if invalid or deleted or reload_failed:
                self.assertFalse((root / 'reloaded').exists())
                self.assertIn('eDP-1', (folder / 'monitors.lua').read_text())
                if not deleted:
                    self.assertTrue(list(folder.glob('monitors.rejected-*.lua')))
            else:
                self.assertTrue((root / 'reloaded').exists())
                self.assertEqual((folder / 'monitors.lua').read_text(), '-- new saved monitor rules\n')

    def test_autostart_configuration_precedence(self):
        spec = importlib.util.spec_from_file_location('autostart_settings', SOURCE / 'autostart-settings.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            user, system = root / 'user', root / 'system'
            for folder in (user, system):
                (folder / 'autostart').mkdir(parents=True)
                (folder / 'autostart/example.desktop').write_text('test')
            old = {name: os.environ.get(name) for name in ('XDG_CONFIG_HOME', 'XDG_CONFIG_DIRS')}
            try:
                os.environ['XDG_CONFIG_HOME'], os.environ['XDG_CONFIG_DIRS'] = str(user), str(system)
                self.assertEqual(module.entries()['example.desktop'], user / 'autostart/example.desktop')
            finally:
                for name, value in old.items():
                    if value is None:
                        os.environ.pop(name, None)
                    else:
                        os.environ[name] = value


if __name__ == '__main__':
    unittest.main()
