#!/usr/bin/env python3
"""Own hypridle and optional lid handling for this Hyprland session only."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import gi
from gi.repository import Gio, GLib, GLibUnix
from power_config import load, render, DEFAULTS


def proxy(name, path, interface):
    return Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SYSTEM, Gio.DBusProxyFlags.NONE,
                                         None, name, path, interface, None)

def on_battery(upower):
    value = upower.get_cached_property('OnBattery')
    if value is None:
        raise RuntimeError('Power source unavailable')
    return value.unpack()

def main():
    upower = proxy('org.freedesktop.UPower', '/org/freedesktop/UPower', 'org.freedesktop.UPower')
    if len(sys.argv) == 3 and sys.argv[1] == 'idle-suspend':
        if ('battery' if on_battery(upower) else 'ac') == sys.argv[2]:
            subprocess.run(['systemctl', 'suspend'], check=True)
        return
    runtime = Path(os.environ['ERGENOS_HYPRLAND_RUNTIME'])
    config = runtime / 'hypridle.conf'
    child = None
    inhibitor = None
    previous = None
    last_error = None
    closed = bool(upower.get_cached_property('LidIsClosed').unpack())
    loop = GLib.MainLoop()

    def tick():
        nonlocal child, inhibitor, previous, closed, last_error
        try:
            try:
                settings = load()
            except (OSError, ValueError) as error:
                message = f'Unable to read power settings: {error}'
                if message != last_error:
                    subprocess.Popen(['notify-send', 'ErgenOS Power', 'Invalid power settings. Keeping the last working settings.'])
                    print(message, file=sys.stderr, flush=True)
                    last_error = message
                settings = previous or DEFAULTS.copy()
            else:
                last_error = None
            if settings != previous or child is None or child.poll() is not None:
                config.write_text(render(settings))
                if child and child.poll() is None:
                    child.terminate()
                    child.wait(timeout=5)
                child = subprocess.Popen(['hypridle', '--config', str(config)])
                previous = settings
            action = settings['lid_battery' if on_battery(upower) else 'lid_ac']
            if action != 'system' and inhibitor is None:
                bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
                result, fds = bus.call_with_unix_fd_list_sync(
                    'org.freedesktop.login1', '/org/freedesktop/login1', 'org.freedesktop.login1.Manager',
                    'Inhibit', GLib.Variant('(ssss)', ('handle-lid-switch', 'ErgenOS Hyprland',
                    'Session power preferences', 'block')), GLib.VariantType.new('(h)'),
                    Gio.DBusCallFlags.NONE, 5000, None, None)
                inhibitor = fds.get(result.unpack()[0])
            elif action == 'system' and inhibitor is not None:
                os.close(inhibitor)
                inhibitor = None
            now_closed = bool(upower.get_cached_property('LidIsClosed').unpack())
            just_closed = now_closed and not closed
            closed = now_closed
            if just_closed and action in ('lock', 'suspend') and inhibitor is not None:
                docked = False
                if settings['dock_guard']:
                    monitors = json.loads(subprocess.check_output(['hyprctl', '-j', 'monitors'], text=True, timeout=3))
                    docked = any(not m['name'].startswith(('eDP', 'LVDS', 'DSI')) for m in monitors)
                if not docked:
                    subprocess.Popen(['loginctl', 'lock-session'] if action == 'lock' else ['systemctl', 'suspend'])
        except Exception as error:
            print(f'Power settings: {error}', file=sys.stderr, flush=True)
        return GLib.SOURCE_CONTINUE

    def stop():
        loop.quit()
        return GLib.SOURCE_REMOVE
    GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, stop)
    GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, stop)
    tick()
    GLib.timeout_add_seconds(1, tick)
    try:
        loop.run()
    finally:
        if child and child.poll() is None:
            child.terminate()
            child.wait(timeout=5)
        if inhibitor is not None:
            os.close(inhibitor)
        config.unlink(missing_ok=True)

if __name__ == '__main__':
    main()
