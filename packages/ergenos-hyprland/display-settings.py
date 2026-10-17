#!/usr/bin/env python3
"""Bridge nwg-displays' saved Lua files to the ErgenOS configuration."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def fingerprint(paths):
    result = []
    for path in paths:
        try:
            result.append(hashlib.sha256(path.read_bytes()).hexdigest())
        except FileNotFoundError:
            result.append(None)
    return tuple(result)


def main():
    config = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
    directory = config / 'ergenos-hyprland' / 'displays'
    directory.mkdir(parents=True, exist_ok=True)
    # nwg-displays checks this directory before processing its explicit paths.
    (config / 'hypr').mkdir(exist_ok=True)
    import fcntl
    runtime = Path(os.environ['XDG_RUNTIME_DIR'])
    with (runtime / 'ergenos-display-settings.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        paths = [directory / 'monitors.lua', directory / 'workspaces.lua']
        # A real initial Lua snapshot lets nwg-displays restore the previous
        # layout when its confirmation timer expires, including on the first use.
        if not paths[0].exists():
            monitors = json.loads(subprocess.check_output(['hyprctl', '-j', 'monitors'], text=True))
            rules = []
            for monitor in monitors:
                rule = {'output': monitor['name'],
                        'mode': f"{monitor['width']}x{monitor['height']}@{monitor['refreshRate']:.6f}",
                        'position': f"{monitor['x']}x{monitor['y']}",
                        'scale': monitor['scale'], 'transform': monitor['transform']}
                fields = ', '.join(f"{key} = {json.dumps(value, ensure_ascii=False)}" for key, value in rule.items())
                rules.append('hl.monitor({ ' + fields + ' })')
            paths[0].write_text('\n'.join(rules) + '\n')
        if not paths[1].exists():
            paths[1].write_text('-- No workspace overrides.\n')
        good_files = {path: path.read_bytes() for path in paths}
        previous = fingerprint(paths)
        child = subprocess.Popen(['nwg-displays', '--monitors_path', str(directory / 'monitors.conf'),
                                  '--workspaces_path', str(directory / 'workspaces.conf')])
        pending = None
        changed_at = 0
        while True:
            current = fingerprint(paths)
            if current != previous:
                if current != pending:
                    pending, changed_at = current, time.monotonic()
                elif time.monotonic() - changed_at >= .35:
                    # Validate all configuration before replacing the active layout.
                    try:
                        # Missing files must not silently erase a saved layout.
                        candidate = {path: path.read_bytes() for path in paths}
                        check = subprocess.run(['Hyprland', '--verify-config', '--config',
                                                '/usr/share/ergenos-hyprland/hyprland.lua'],
                                               capture_output=True, text=True, timeout=10)
                        if check.returncode:
                            raise RuntimeError(check.stdout + check.stderr)
                        subprocess.run(['hyprctl', 'reload'], check=True, capture_output=True, timeout=10)
                        good_files = candidate
                    except (OSError, subprocess.SubprocessError, RuntimeError) as error:
                        subprocess.run(['notify-send', '-u', 'critical', 'Display settings',
                                        'Configuration could not be applied. Restoring saved Lua files.'], check=False)
                        print(str(error), file=sys.stderr)
                        stamp = time.time_ns()
                        for path in paths:
                            if path.exists():
                                path.with_suffix(f'.rejected-{stamp}.lua').write_bytes(path.read_bytes())
                            path.write_bytes(good_files[path])
                    previous, pending = fingerprint(paths), None
            if child.poll() is not None and (pending is None or time.monotonic() - changed_at >= 1):
                break
            time.sleep(.15)
        return child.wait()


if __name__ == '__main__':
    raise SystemExit(main())
