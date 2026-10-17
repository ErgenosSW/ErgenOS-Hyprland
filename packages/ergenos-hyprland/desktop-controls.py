#!/usr/bin/env python3
"""Small session-local brightness and battery controls."""
import subprocess
import sys
from pathlib import Path


def battery_details(root=Path('/sys/class/power_supply')):
    batteries = []
    def read(folder, name):
        try:
            return (folder / name).read_text().strip()
        except OSError:
            return ''
    for folder in sorted(root.iterdir()):
        if read(folder, 'type') != 'Battery':
            continue
        capacity = read(folder, 'capacity')
        status = read(folder, 'status')
        power = read(folder, 'power_now')
        details = []
        if power.isdigit():
            details.append(f'{int(power) / 1_000_000:.1f} W')
        full, design = read(folder, 'energy_full'), read(folder, 'energy_full_design')
        if not full or not design:
            full, design = read(folder, 'charge_full'), read(folder, 'charge_full_design')
        if full.isdigit() and design.isdigit() and int(design):
            details.append(f'Battery health: {int(full) / int(design):.0%}')
        translated = {'Charging': 'Charging', 'Discharging': 'Discharging',
                      'Full': 'Fully charged', 'Not charging': 'Plugged in, not charging',
                      'Unknown': 'Unknown status'}.get(status, status)
        batteries.append((capacity, translated, ' · '.join(details), status == 'Charging'))
    return batteries


def main():
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Adw, Gtk, Gio, GLib, Gdk
    GLib.set_prgname('io.github.ergenossw.HyprlandControls')
    GLib.set_application_name('ErgenOS')
    mode = sys.argv[1] if len(sys.argv) > 1 else 'battery'
    if mode not in ('brightness', 'battery'):
        raise SystemExit('Usage: desktop-controls.py [brightness|battery]')

    class Controls(Adw.Application):
        def __init__(self):
            super().__init__(application_id='io.github.ergenossw.HyprlandControls',
                             flags=Gio.ApplicationFlags.NON_UNIQUE)
            self.pending = None
            self.connect('activate', self.activate_window)

        def activate_window(self, app):
            Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.FORCE_DARK)
            css = Gtk.CssProvider()
            css.load_from_data(b'window.ergen-controls { background: #081424; color: #eaf3ff; } .ergen-controls headerbar { background: #081424; } .ergen-controls scale highlight { background: #0aa7ff; } .ergen-controls .accent { color: #54c3ff; }')
            Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            title = 'Screen brightness' if mode == 'brightness' else 'Battery and power'
            window = Adw.ApplicationWindow(application=self, title=title, default_width=400, default_height=300)
            window.add_css_class('ergen-controls')
            view = Adw.ToolbarView()
            header = Adw.HeaderBar()
            header.set_title_widget(Adw.WindowTitle(title=title, subtitle='ErgenOS'))
            view.add_top_bar(header)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18,
                          margin_top=20, margin_bottom=24, margin_start=26, margin_end=26)
            icon = Gtk.Image(icon_name='display-brightness-symbolic' if mode == 'brightness' else 'battery-symbolic', pixel_size=48)
            icon.add_css_class('accent')
            box.append(icon)
            value = Gtk.Label()
            value.add_css_class('title-1')
            box.append(value)
            description = Gtk.Label(wrap=True, justify=Gtk.Justification.CENTER)
            box.append(description)
            if mode == 'brightness':
                try:
                    current = int(subprocess.check_output(['brightnessctl', 'get'], text=True))
                    maximum = int(subprocess.check_output(['brightnessctl', 'max'], text=True))
                    percent = max(1, round(current * 100 / maximum))
                except (OSError, ValueError, subprocess.CalledProcessError, ZeroDivisionError):
                    value.set_text('Brightness control unavailable')
                    description.set_text('No supported display backlight was detected.')
                else:
                    value.set_text(f'{percent}%')
                    description.set_text('Move the slider to adjust screen brightness.')
                    slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 100, 1)
                    slider.set_draw_value(False)
                    slider.set_value(percent)
                    slider.set_hexpand(True)
                    def apply():
                        self.pending = None
                        setting = round(slider.get_value())
                        try:
                            subprocess.run(['brightnessctl', '--min-value=1', 'set', f'{setting}%'], check=True, capture_output=True)
                            description.set_text('Screen brightness')
                        except (OSError, subprocess.CalledProcessError):
                            description.set_text('Unable to adjust brightness.')
                        return GLib.SOURCE_REMOVE
                    def changed(control):
                        value.set_text(f'{round(control.get_value())}%')
                        if self.pending is not None:
                            GLib.source_remove(self.pending)
                        self.pending = GLib.timeout_add(100, apply)
                    slider.connect('value-changed', changed)
                    box.append(slider)
            else:
                def refresh():
                    batteries = battery_details()
                    if not batteries:
                        value.set_text('No battery detected')
                        description.set_text('This computer is running on AC power.')
                    else:
                        capacity, status, extra, charging = batteries[0]
                        value.set_text(f'{capacity}%')
                        description.set_text(status + ('\n' + extra if extra else ''))
                        level = min(100, max(0, round(int(capacity or 0) / 10) * 10))
                        icon.set_from_icon_name(f'battery-level-{level}' + ('-charging' if charging else '') + '-symbolic')
                    return GLib.SOURCE_CONTINUE
                button = Gtk.Button(label='Power settings')
                button.add_css_class('suggested-action')
                button.connect('clicked', lambda *_: subprocess.Popen(['python', '/usr/share/ergenos-hyprland/power-settings.py']))
                box.append(button)
                refresh()
                GLib.timeout_add_seconds(5, refresh)
            view.set_content(box)
            window.set_content(view)
            window.present()
    Controls().run([sys.argv[0]])


if __name__ == '__main__':
    main()
