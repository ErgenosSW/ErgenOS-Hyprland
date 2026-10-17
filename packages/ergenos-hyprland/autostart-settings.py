#!/usr/bin/env python3
"""Manage standard XDG autostart overrides without changing system entries."""
import os
from pathlib import Path
import sys


def config_home():
    return Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))


def entries():
    result = {}
    directories = [config_home(), *[Path(p) for p in os.environ.get('XDG_CONFIG_DIRS', '/etc/xdg').split(':') if p]]
    for directory in directories:
        for path in sorted((directory / 'autostart').glob('*.desktop')):
            result.setdefault(path.name, path)
    return result


def main():
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Adw, Gtk, Gio, GLib, Gdk
    GLib.set_prgname('io.github.ergenossw.HyprlandAutostart')
    GLib.set_application_name('ErgenOS Autostart')

    def keyfile(path):
        key = GLib.KeyFile()
        key.load_from_file(str(path), GLib.KeyFileFlags.KEEP_COMMENTS | GLib.KeyFileFlags.KEEP_TRANSLATIONS)
        return key

    def value(key, name, default=''):
        try:
            return key.get_string('Desktop Entry', name)
        except GLib.Error:
            return default

    def write_override(name, key):
        directory = config_home() / 'autostart'
        directory.mkdir(parents=True, exist_ok=True)
        data, _ = key.to_data()
        temporary = directory / ('.' + name + '.tmp')
        temporary.write_text(data)
        temporary.replace(directory / name)

    class Autostart(Adw.Application):
        def __init__(self):
            super().__init__(application_id='io.github.ergenossw.HyprlandAutostart')
            self.connect('activate', self.activate_window)
            self.rows = []

        def activate_window(self, application):
            if self.get_active_window():
                self.get_active_window().present()
                return
            Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.FORCE_DARK)
            window = Adw.ApplicationWindow(application=self, title='Startup applications', default_width=570, default_height=520)
            window.add_css_class('ergen-autostart')
            css = Gtk.CssProvider()
            css.load_from_data(b'window.ergen-autostart { background: #081424; color: #eaf3ff; } .ergen-autostart headerbar { background: #081424; }')
            Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            view = Adw.ToolbarView()
            header = Adw.HeaderBar()
            header.set_title_widget(Adw.WindowTitle(title='Startup applications', subtitle='ErgenOS'))
            add = Gtk.Button(label='Add application')
            add.connect('clicked', self.choose_application, window)
            header.pack_end(add)
            view.add_top_bar(header)
            scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14,
                          margin_top=20, margin_bottom=20, margin_start=20, margin_end=20)
            note = Gtk.Label(label='Enabled applications start the next time you log in.\nTurning an entry off does not close its running application.', wrap=True, xalign=0)
            box.append(note)
            self.group = Adw.PreferencesGroup()
            box.append(self.group)
            self.status = Gtk.Label(wrap=True, xalign=0)
            box.append(self.status)
            scroll.set_child(box)
            view.set_content(scroll)
            window.set_content(view)
            self.refresh()
            window.present()

        def refresh(self):
            for row in self.rows:
                self.group.remove(row)
            self.rows = []
            desktops = set(os.environ.get('XDG_CURRENT_DESKTOP', 'Hyprland').split(':'))
            for name, path in entries().items():
                try:
                    key = keyfile(path)
                    only = set(filter(None, value(key, 'OnlyShowIn').split(';')))
                    excluded = set(filter(None, value(key, 'NotShowIn').split(';')))
                    if only and not desktops.intersection(only) or desktops.intersection(excluded):
                        continue
                    if value(key, 'Type', 'Application') != 'Application':
                        continue
                    hidden = value(key, 'Hidden').lower() == 'true'
                    row = Adw.SwitchRow(title=value(key, 'Name', name), subtitle=name, active=not hidden)
                    row.connect('notify::active', self.toggle, name, key)
                    self.group.add(row)
                    self.rows.append(row)
                except (GLib.Error, OSError) as error:
                    self.status.set_text(f'Unable to read {name}: {error}')
            if not self.rows:
                self.status.set_text('No startup applications are configured for this desktop.')

        def toggle(self, row, property_spec, name, key):
            try:
                key.set_boolean('Desktop Entry', 'Hidden', not row.get_active())
                write_override(name, key)
                self.status.set_text('Saved. Changes take effect at the next login.')
            except (OSError, GLib.Error) as error:
                self.status.set_text(f'Unable to save: {error}')

        def choose_application(self, button, window):
            dialog = Gtk.FileChooserNative.new('Choose an application', window, Gtk.FileChooserAction.OPEN, 'Add', 'Cancel')
            dialog.set_current_folder(Gio.File.new_for_path('/usr/share/applications'))
            filter = Gtk.FileFilter()
            filter.set_name('Application launchers (*.desktop)')
            filter.add_pattern('*.desktop')
            dialog.add_filter(filter)
            def selected(chooser, response):
                if response == Gtk.ResponseType.ACCEPT:
                    try:
                        path = Path(chooser.get_file().get_path())
                        destination = config_home() / 'autostart' / path.name
                        existing = destination.exists()
                        key = keyfile(destination if existing else path)
                        if value(key, 'Type') != 'Application' or not value(key, 'Exec'):
                            raise ValueError('Choose an application launcher with an Exec command.')
                        key.set_boolean('Desktop Entry', 'Hidden', False)
                        only = value(key, 'OnlyShowIn')
                        if not existing or only:
                            desktops = set(filter(None, only.split(';'))) if existing else set()
                            desktops.add('Hyprland')
                            key.set_string('Desktop Entry', 'OnlyShowIn', ';'.join(sorted(desktops)) + ';')
                        excluded = [desktop for desktop in value(key, 'NotShowIn').split(';') if desktop and desktop != 'Hyprland']
                        try:
                            key.remove_key('Desktop Entry', 'NotShowIn')
                        except GLib.Error:
                            pass
                        if excluded:
                            key.set_string('Desktop Entry', 'NotShowIn', ';'.join(excluded) + ';')
                        write_override(path.name, key)
                        self.refresh()
                        self.status.set_text('Application added for the next Hyprland login.')
                    except (OSError, GLib.Error, ValueError, TypeError) as error:
                        self.status.set_text(f'Unable to add application: {error}')
                chooser.destroy()
            dialog.connect('response', selected)
            dialog.show()
    Autostart().run([sys.argv[0]])


if __name__ == '__main__':
    main()
