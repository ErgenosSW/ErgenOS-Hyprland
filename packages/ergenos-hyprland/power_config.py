"""Validated session-local power preferences and hypridle configuration."""
import json
import os
from pathlib import Path

DEFAULTS = dict(lock=300, display=600, suspend_ac=0, suspend_battery=0,
                lid_ac='system', lid_battery='system', dock_guard=True)
TIMES = [0, 60, 120, 300, 600, 900, 1200, 1800, 3600]
ACTIONS = ['system', 'suspend', 'lock', 'ignore']

def config_path():
    return Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))) / 'ergenos-hyprland/power.json'

def validate(data):
    if not isinstance(data, dict) or set(data) - DEFAULTS.keys():
        raise ValueError('Invalid power settings')
    result = DEFAULTS | data
    for key in ('lock', 'display', 'suspend_ac', 'suspend_battery'):
        if type(result[key]) is not int or result[key] not in TIMES:
            raise ValueError('Invalid timeout')
    for key in ('lid_ac', 'lid_battery'):
        if result[key] not in ACTIONS:
            raise ValueError('Invalid lid action')
    if type(result['dock_guard']) is not bool:
        raise ValueError('Invalid docking preference')
    return result

def load():
    try:
        return validate(json.loads(config_path().read_text()))
    except FileNotFoundError:
        return DEFAULTS.copy()

def save(data):
    data = validate(data)
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2) + '\n')
    temp.replace(path)

def render(data):
    data = validate(data)
    text = '''general {
    lock_cmd = pidof hyprlock || hyprlock --config /usr/share/ergenos-hyprland/hyprlock.conf
    before_sleep_cmd = loginctl lock-session
    after_sleep_cmd = hyprctl dispatch 'hl.dsp.dpms({ action = "enable" })'
    inhibit_sleep = 3
}
'''
    commands = {'lock': 'loginctl lock-session',
                'display': '''hyprctl dispatch 'hl.dsp.dpms({ action = "disable" })' ''',
                'suspend_ac': 'python /usr/share/ergenos-hyprland/power-manager.py idle-suspend ac',
                'suspend_battery': 'python /usr/share/ergenos-hyprland/power-manager.py idle-suspend battery'}
    for key, command in commands.items():
        if data[key]:
            text += f'listener {{\n    timeout = {data[key]}\n    on-timeout = {command}\n'
            if key == 'display':
                text += '''    on-resume = hyprctl dispatch 'hl.dsp.dpms({ action = "enable" })'\n'''
            text += '}\n'
    return text
