# Goggles Link

Goggles Link is the VR streaming software of [Goggles OS](https://github.com/jamoijyt/gogglesos):
the PC side that GogglesXR runs, and the app on the headset. It is a fork of
[WiVRn](https://github.com/WiVRn/WiVRn) (GPL-3.0), kept close to it so WiVRn's improvements can
be merged in.

## What differs from WiVRn

Kept small on purpose. Every change is listed here.

| Change | Where |
|---|---|
| The headset app has its own application ID (`org.gogglesos.link`) and name, so it installs beside WiVRn's app | `build.gradle` (`wivrn_app_id`), set by the workflow |
| Builds for Goggles OS: a server archive for `/opt/goggles-link` (no Flatpak) with xrizer included, and the headset APK | `.github/workflows/goggles-link.yml` |
| WiVRn's own build and store-release workflows are removed (they publish WiVRn, not this fork) | `.github/workflows/` |
| Goggles look in the headset app: the Goggles Link logo (about page, top bar, splash, launcher icon; replaces every seasonal WiVRn logo), a "Goggles" colour theme and accent used by default (settings from older versions move to it once: `goggles_branding`) | `images/goggles-link.svg`, `client/CMakeLists.txt`, `build.gradle`, `client/render/ui_theme.cpp`, `client/configuration.*` |
| Names the user sees say Goggles Link: welcome and about headers, the in-game hint, the refresh-rate message, the empty server list hint, the licences page (which still credits WiVRn) | `client/scenes/*.cpp` |
| The server tells games the headset is "... on Goggles Link", and uses that name for desktop notifications and its sleep inhibitor | `server/driver/wivrn_session.cpp`, `server/main.cpp`, `server/sleep_inhibitor.cpp` |

Names inside the software (the `wivrn-server` program, its D-Bus name, its config folder, the
network protocol) are WiVRn's for now, so the two can't run at the same time, and a stock WiVRn app of the same
version can still connect.

## Builds

Every push builds both parts; a tag `gl-<version>` publishes a release that Goggles OS pins by
checksum. See the comments at the top of `.github/workflows/goggles-link.yml`, including the
signing key the headset app needs.

## Merging a new WiVRn release

```bash
git remote add upstream https://github.com/WiVRn/WiVRn
```

```bash
git fetch upstream --tags
```

```bash
git merge <release tag>
```

Then check the table above still holds, and that `XRIZER_REV` in the workflow matches
`flatpak/io.github.wivrn.wivrn.yml.in`.
