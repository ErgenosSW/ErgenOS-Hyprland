# Optional preview release checklist

## Build and review

- [x] Official-repository dependencies plus the local private panel helper; minimum compositor version recorded without blocking rolling updates.
- [x] Explicit source checksums, native parsers and 25 regression tests.
- [x] No install hook that seeds or overwrites home settings.
- [x] README and shortcut reference describe the current implementation.
- [x] Tested reboot, GNOME round trip, private-history cleanup and ordered logout.
- [x] Fresh-account graphical acceptance: user confirmed panel, launcher, terminal, settings, clipboard and lock.
- [ ] Review and commit the intended source changes manually; no automatic push.

- [x] Default application mappings for fresh XDG settings and the main account.
- [x] Native XWayland resolution and WoW fresh-launch UI checked on this laptop.
- [x] Additional codec/subtitle plugins are optional, not hard dependencies.

## Fresh-account graphical acceptance

Use a temporary ordinary account, with no administrator groups or copied config.
Log out of the main account rather than running concurrent graphical sessions.
Choose **ErgenOS Hyprland** at the login screen.

- [x] Panel, wallpaper and workspace indicators appear without a config error.
- [x] Super opens applications; Super+Return opens Foot; Super+E opens Files.
- [x] Super+comma opens settings; brightness, battery and Power windows work.
- [x] Copy a harmless sample, choose it with Super+Shift+V, paste it in Foot.
- [ ] Fresh-account screenshot follow-up (main-account screenshot test passed).
- [ ] Fresh-account notification follow-up (main-account notification tests passed).
- [x] Super+L locks and the account password unlocks.
- [x] Super+Shift+E -> Log out returns to the login screen normally.
- [x] Return to the main account; inspect the temporary account's log and confirm
      no remaining processes. Remove only this test account, home and test group.

## Explicitly deferred

- Browser screen-sharing stream (user postponed).
- External monitor/docking/audio (after Warsaw).
- Other hardware and webcam/Bluetooth pairing/audio coverage.

A passing test on one laptop supports this optional preview, not general hardware
or stable-release certification.

Fresh-account session: 2026-10-16 22:55:31-22:55:45 Europe/Warsaw.
User confirmed all requested core functions. Temporary account UID 1001, home
and private group were removed after return; no test-user processes remained.
