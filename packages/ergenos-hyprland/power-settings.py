#!/usr/bin/env python3
"""Power profiles shared with GNOME, idle settings scoped to Hyprland."""
import subprocess
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gtk, Gio, GLib, Gdk
from power_config import load, save, DEFAULTS, TIMES, ACTIONS

GLib.set_prgname('io.github.ergenossw.HyprlandPower')
GLib.set_application_name('ErgenOS Power')

class Power(Adw.Application):
    def __init__(self):
        super().__init__(application_id='io.github.ergenossw.HyprlandPower')
        self.window = None
        self.connect('activate', self.activate_window)

    def activate_window(self, app):
        if self.window:
            self.window.present()
            return
        Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        css = Gtk.CssProvider()
        css.load_from_data(b'window.ergen-power, .ergen-power headerbar { background: #081424; color: #eaf3ff; } .ergen-power .suggested-action { background: #0aa7ff; color: #081424; }')
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.window = Adw.ApplicationWindow(application=self, title='Power', default_width=540, default_height=650)
        self.window.add_css_class('ergen-power')
        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        header.set_title_widget(Adw.WindowTitle(title='Power', subtitle='ErgenOS'))
        toolbar.add_top_bar(header)
        scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, margin_start=20, margin_end=20, margin_top=16, margin_bottom=24)
        scroll.set_child(box)
        toolbar.set_content(scroll)
        self.window.set_content(toolbar)
        self.status = Gtk.Label(wrap=True)
        try:
            settings = load()
        except (OSError, ValueError) as error:
            settings = DEFAULTS.copy()
            self.status.set_text(f'Unable to read saved settings: {error}')
        profiles = Adw.PreferencesGroup(title='Power profile', description='The selected profile also applies in GNOME.')
        box.append(profiles)
        self.profile_row = Adw.ComboRow(title='Profile')
        profiles.add(self.profile_row)
        self.profile_proxy = None
        self.profile_busy = False
        try:
            self.profile_proxy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SYSTEM, Gio.DBusProxyFlags.NONE, None,
                'org.freedesktop.UPower.PowerProfiles', '/org/freedesktop/UPower/PowerProfiles',
                'org.freedesktop.UPower.PowerProfiles', None)
            self.profiles = [item['Profile'] for item in self.profile_proxy.get_cached_property('Profiles').unpack()]
            names = {'power-saver': 'Power Saver', 'balanced': 'Balanced', 'performance': 'Performance'}
            self.profile_row.set_model(Gtk.StringList.new([names.get(p, p) for p in self.profiles]))
            self.update_profile()
            self.profile_proxy.connect('g-properties-changed', lambda *args: self.update_profile())
            self.profile_row.connect('notify::selected', self.change_profile)
        except Exception:
            self.profile_row.set_sensitive(False)
            profiles.set_description('Power profiles are unavailable on this system.')
        self.rows = {}
        idle = Adw.PreferencesGroup(title='Idle', description='Choose when to lock, turn off the screen or suspend.')
        box.append(idle)
        time_names = ['Never' if n == 0 else f'{n // 60} minutes' if n != 60 else '1 minute' for n in TIMES]
        for key, title in [('lock', 'Lock screen after'), ('display', 'Turn screen off after'),
                           ('suspend_battery', 'Suspend on battery after'), ('suspend_ac', 'Suspend when plugged in after')]:
            row = Adw.ComboRow(title=title, model=Gtk.StringList.new(time_names))
            row.set_selected(TIMES.index(settings[key]))
            self.rows[key] = row
            idle.add(row)
        lid = Adw.PreferencesGroup(title='Laptop lid', description='Custom lid actions apply only in ErgenOS Hyprland.')
        box.append(lid)
        for key, title in [('lid_battery', 'On battery'), ('lid_ac', 'When plugged in')]:
            row = Adw.ComboRow(title=title, model=Gtk.StringList.new(['System default', 'Suspend', 'Lock screen', 'Do nothing']))
            row.set_selected(ACTIONS.index(settings[key]))
            self.rows[key] = row
            lid.add(row)
        guard = Adw.SwitchRow(title='Keep running with an external display', subtitle='For custom lid actions', active=settings['dock_guard'])
        self.rows['dock_guard'] = guard
        lid.add(guard)
        button = Gtk.Button(label='Apply session settings')
        button.add_css_class('suggested-action')
        button.connect('clicked', self.apply)
        box.append(button)
        box.append(self.status)
        self.window.present()

    def update_profile(self):
        active = self.profile_proxy.get_cached_property('ActiveProfile').unpack()
        if active in self.profiles:
            self.profile_busy = True
            self.profile_row.set_selected(self.profiles.index(active))
            self.profile_busy = False

    def change_profile(self, row, spec):
        if self.profile_busy:
            return
        try:
            subprocess.run(['powerprofilesctl', 'set', self.profiles[row.get_selected()]], check=True, capture_output=True, text=True, timeout=10)
            self.status.set_text('Power profile updated.')
        except (OSError, subprocess.SubprocessError):
            self.status.set_text('Unable to change the power profile.')
            self.update_profile()

    def apply(self, button):
        settings = {}
        for key, row in self.rows.items():
            settings[key] = row.get_active() if key == 'dock_guard' else (ACTIONS if key.startswith('lid_') else TIMES)[row.get_selected()]
        try:
            save(settings)
            self.status.set_text('Session settings saved. Changes take effect immediately.')
        except (OSError, ValueError) as error:
            self.status.set_text(f'Unable to save settings: {error}')

Power().run(None)
