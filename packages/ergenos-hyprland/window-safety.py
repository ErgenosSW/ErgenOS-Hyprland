#!/usr/bin/env python3
"""Conservative size fallback for explicitly validated app classes, without zoom."""
import fcntl
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import time

DEFAULTS = {'discord': [940, 500], 'io.github.ergenossw.ergenctl': [360, 300],
            'io.github.ergenossw.ergenpac': [360, 300]}


def validate(data):
    if not isinstance(data, dict) or set(data) - {'enabled', 'profiles'}:
        raise ValueError('Expected enabled and/or profiles')
    enabled = data.get('enabled', True)
    if type(enabled) is not bool or not isinstance(data.get('profiles', {}), dict):
        raise ValueError('Invalid window safety settings')
    profiles = {key: value[:] for key, value in DEFAULTS.items()}
    for key, value in data.get('profiles', {}).items():
        if not isinstance(key, str) or not key:
            raise ValueError('Invalid application class')
        if value is False:
            profiles.pop(key.casefold(), None)
        elif (isinstance(value, list) and len(value) == 2 and
              all(type(n) is int and 120 <= n <= 8192 for n in value)):
            profiles[key.casefold()] = value
        else:
            raise ValueError('Expected [minimum width, minimum height] or false')
    return enabled, profiles


def plan(window, monitor, minimum):
    if (not window.get('mapped') or window.get('hidden') or window.get('floating') or
            window.get('fullscreen', 0) or window.get('grouped')):
        return None
    width, height = window['size']
    if width >= minimum[0] and height >= minimum[1]:
        return None
    scale = monitor['scale']
    mw, mh = monitor['width'], monitor['height']
    if monitor.get('transform', 0) in (1, 3, 5, 7):
        mw, mh = mh, mw
    left, top, right, bottom = monitor.get('reserved', [0, 0, 0, 0])
    available_w = math.floor(mw / scale - left - right)
    available_h = math.floor(mh / scale - top - bottom)
    if available_w - 8 < minimum[0] or available_h - 8 < minimum[1]:
        return ('maximize', False)
    return ('float', min(available_w - 8, max(width, minimum[0] + 32)),
            min(available_h - 8, max(height, minimum[1] + 32)))


def query(name):
    return json.loads(subprocess.check_output(['hyprctl', '-j', name], text=True, timeout=3))


def dispatch(command):
    result = subprocess.run(['hyprctl', 'dispatch', command], capture_output=True, text=True, timeout=3)
    if result.returncode or result.stdout.strip() != 'ok':
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def apply(window, action):
    address = window['address']
    if not re.fullmatch(r'0x[0-9a-fA-F]+', address):
        raise ValueError('Invalid window address')
    target = json.dumps('address:' + address)
    if action[0] == 'maximize':
        dispatch('hl.dsp.window.fullscreen({window=' + target + ', action="set", mode="maximized"})')
    else:
        dispatch('hl.dsp.window.float({window=' + target + ', action="set"})')
        dispatch('hl.dsp.window.resize({window=' + target + f', x={action[1]}, y={action[2]}, relative=false' + '})')
        dispatch('hl.dsp.window.center({window=' + target + '})')


class Guard:
    def __init__(self):
        self.pending = {}
        self.handled = set()

    def inspect(self, windows, monitors, profiles, now):
        live = {(w['address'], w['pid']) for w in windows}
        self.handled.intersection_update(live)
        self.pending = {k: v for k, v in self.pending.items() if k in live}
        outputs = {m['id']: m for m in monitors}
        actions = []
        for w in windows:
            key = (w['address'], w['pid'])
            minimum = profiles.get(w.get('class', '').casefold())
            monitor = outputs.get(w.get('monitor'))
            action = plan(w, monitor, minimum) if minimum and monitor else None
            if action is None or key in self.handled:
                self.pending.pop(key, None)
                continue
            signature = (tuple(w['size']), w['monitor'], action)
            previous = self.pending.get(key)
            if previous is None or previous[0] != signature:
                self.pending[key] = (signature, now)
            elif now - previous[1] >= 1.5:
                # One intervention per window lifetime. Explicit user retiling wins.
                self.handled.add(key)
                self.pending.pop(key, None)
                actions.append((w, action))
        return actions


def main():
    path = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))) / 'ergenos-hyprland/window-safety.json'
    runtime = Path(os.environ['ERGENOS_HYPRLAND_RUNTIME'])
    lock = (runtime / 'window-safety.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return
    guard = Guard()
    settings = validate({})
    previous_error = None
    running = True
    def stop(*_):
        nonlocal running
        running = False
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    failures = 0
    while running and runtime.is_dir():
        try:
            try:
                settings = validate(json.loads(path.read_text()))
            except FileNotFoundError:
                settings = validate({})
            except (OSError, ValueError) as error:
                # Keep the last valid policy and report once instead of spamming.
                if str(error) != previous_error:
                    print(f'Window safety settings: {error}', flush=True)
                    previous_error = str(error)
            else:
                previous_error = None
            enabled, profiles = settings
            if enabled:
                windows, monitors = query('clients'), query('monitors')
                failures = 0
                for w, action in guard.inspect(windows, monitors, profiles, time.monotonic()):
                    apply(w, action)
                    message = 'Window expanded to avoid clipped controls. Super+V can restore tiling.'
                    if action[0] == 'maximize':
                        message = 'Window maximized to avoid clipped controls. Super+Shift+F restores its layout.'
                        if not action[1]:
                            message += ' This display is smaller than the supported minimum; app zoom may still be needed.'
                    subprocess.Popen(['notify-send', 'Window size', message])
                    print(f"Window safety: {w['class']} {w['size']} -> {action}", flush=True)
        except (OSError, ValueError, KeyError, subprocess.SubprocessError, RuntimeError) as error:
            print(f'Window safety: {error}', flush=True)
            failures += 1
            if failures >= 5:
                break
        time.sleep(.5)


if __name__ == '__main__':
    main()
