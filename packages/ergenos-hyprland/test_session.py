"""Behavioral regression checks for the optional desktop session (no live UI)."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

SOURCE = Path(__file__).resolve().parent


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ergenos-session-check-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.runtime = self.root / "runtime"
        self.runtime.mkdir()
        self.env = os.environ.copy()
        self.env.pop("HYPRLAND_INSTANCE_SIGNATURE", None)
        self.env.update(PATH=str(self.bin) + ":" + self.env["PATH"],
                        XDG_RUNTIME_DIR=str(self.runtime),
                        TEST_ROOT=str(self.root))

    def stub(self, name, script):
        path = self.bin / name
        path.write_text("#!/usr/bin/env bash\n" + script)
        path.chmod(0o755)
        return path

    def run_script(self, name, *args):
        return subprocess.run(["bash", str(SOURCE / name), *args], env=self.env,
                              capture_output=True, text=True, timeout=10)

    def test_wrapper_preserves_status_and_cleans_runtime(self):
        self.stub("start-hyprland", '''
[[ $XDG_CURRENT_DESKTOP == Hyprland ]] || exit 51
[[ $1 == -- && $2 == --config ]] || exit 52
[[ -d $ERGENOS_HYPRLAND_RUNTIME ]] || exit 53
exit "${TEST_STATUS:-0}"
''')
        for code in (0, 42):
            self.env["TEST_STATUS"] = str(code)
            result = self.run_script("ergenos-hyprland-session")
            self.assertEqual(result.returncode, code, result.stderr)
            self.assertEqual(list(self.runtime.iterdir()), [])

    def test_nested_session_is_refused(self):
        self.env["HYPRLAND_INSTANCE_SIGNATURE"] = "existing"
        self.assertEqual(self.run_script("ergenos-hyprland-session").returncode, 1)

    def test_cancelled_screenshot_does_not_touch_clipboard(self):
        self.stub("slurp", "exit 1\n")
        for command in ("grim", "wl-copy", "notify-send"):
            self.stub(command, 'touch "$TEST_ROOT/unexpected"\n')
        self.assertEqual(self.run_script("ergenos-hyprland-screenshot").returncode, 0)
        self.assertFalse((self.root / "unexpected").exists())

    def test_restart_requires_explicit_confirmation(self):
        self.stub("fuzzel", '''
if [[ ! -e $TEST_ROOT/asked ]]; then
    touch "$TEST_ROOT/asked"
    printf 'Restart\n'
else
    printf 'Cancel\n'
fi
''')
        self.stub("systemctl", 'touch "$TEST_ROOT/restarted"\n')
        result = self.run_script("ergenos-hyprland-menu", "session")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / "restarted").exists())

    def test_services_are_single_instance_and_stop_all_children(self):
        stub = self.stub("test-service", '''
case ${0##*/} in
systemctl) printf '%s\n' "$*" >> "$TEST_ROOT/systemctl-calls"; exit 0;;
dbus-update-activation-environment|gdbus) exit 0;;
esac
printf '%s\n' "$$" >> "$TEST_ROOT/children"
exec sleep 300
''')
        names = ("dbus-update-activation-environment", "systemctl", "gdbus", "swaybg",
                 "swaync", "wl-paste", "polkit-test", "nm-applet", "python", "waybar", "blueman-applet")
        for name in names:
            (self.bin / name).symlink_to(stub)
        runner = self.root / "runner"
        runner.write_text((SOURCE / "session-services").read_text().replace(
            "/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1", "polkit-test").replace(
            "/usr/lib/ergenos-hyprland/waybar", "waybar"))
        self.env.update(ERGENOS_HYPRLAND_RUNTIME=str(self.runtime),
                        WAYLAND_DISPLAY="test", XDG_CURRENT_DESKTOP="Hyprland",
                        XDG_SESSION_TYPE="wayland", HYPRLAND_INSTANCE_SIGNATURE="test")
        process = subprocess.Popen(["bash", str(runner)], env=self.env)
        (self.runtime / "clipboard.db").write_bytes(b"session clipboard")
        expected = 8
        lock_inode = None
        try:
            for _ in range(150):
                path = self.root / "children"
                if path.exists() and len(path.read_text().splitlines()) == expected:
                    break
                time.sleep(.02)
            children = [int(pid) for pid in path.read_text().splitlines()]
            self.assertEqual(len(children), expected)
            subprocess.run(["bash", str(runner)], env=self.env, check=True, timeout=2)
            self.assertEqual(len(path.read_text().splitlines()), expected)
            lock_inode = (self.runtime / "services.lock").stat().st_ino
            process.terminate()
            process.wait(timeout=5)
            self.assertEqual((self.runtime / "services.lock").stat().st_ino, lock_inode)
            for pid in children:
                with self.assertRaises(ProcessLookupError):
                    os.kill(pid, 0)
            self.assertFalse((self.runtime / "services.pid").exists())
            self.assertFalse((self.runtime / "clipboard.db").exists())
            calls = (self.root / "systemctl-calls").read_text()
            self.assertIn("--user start ergenos-hyprland-session.target", calls)
            self.assertIn("--user stop ergenos-hyprland-session.target", calls)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()

    def test_panel_actions_are_declared(self):
        config = json.loads((SOURCE / "waybar.json").read_text())
        for section in ("modules-left", "modules-center", "modules-right"):
            for name in config[section]:
                self.assertIn(name, config)


if __name__ == "__main__":
    unittest.main()
