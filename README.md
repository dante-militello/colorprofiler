# ColorProfiler

> Display color profiles for NVIDIA GPUs — gamma, vibrance and hue, per monitor, from your system tray.

<!-- screenshot -->
<p align="center">
  <img src="https://i.imgur.com/nn8Kp86.png" alt="ColorProfiler UI" width="420"/>
</p>

---

## What is it for?

Some games don't let you adjust brightness or gamma from within the game, or their settings simply don't go high enough. ColorProfiler lets you boost gamma and digital vibrance at the driver level — outside the game — so you can see better in dark areas, spot enemies hiding in shadows, and get a sharper, more vivid image without touching the game's own options.

Common use cases:
- Crank up gamma in dark games (horror, survival, battle royale) to see in places others can't
- Boost digital vibrance for more vivid colors and easier enemy spotting
- Switch between a "gaming" profile and a "normal" profile instantly with a hotkey
- Apply different settings per monitor without touching NVIDIA Control Panel every time

---

## Features

- **Gamma control** via ArgyllCMS dispwin (works where standard Windows APIs fail)
- **Digital Vibrance & Hue** via NVAPI — the same interface NVIDIA Control Panel uses
- **Per-monitor or all displays** — apply settings to one or every connected screen
- **Profiles** — create, name, and switch between presets instantly
- **Global hotkeys** — switch profiles without alt-tabbing out of your game
- **System tray** — lives quietly in the background, opens on left click
- **Real-time preview** — sliders apply changes as you drag them

---

## Requirements

- Windows 10/11
- NVIDIA GPU with up-to-date drivers
- Python 3.12+

---

## Installation

```bash
git clone https://github.com/youruser/colorprofiler
cd colorprofiler
pip install -r requirements.txt
python app.py
```

> `dispwin.exe` (ArgyllCMS) is included in the repo — no additional installs needed.

---

## Usage

| Action | How |
|--------|-----|
| Open panel | Left-click the tray icon |
| Switch profile | Click a profile in the list |
| Edit profile | Select it and adjust the sliders |
| Save changes | Click **Guardar** (appears when changes are detected) |
| Reset to default | Click **↺** |
| Delete profile | Click **🗑** |
| Assign hotkey | Click the Hotkey field and press your combo |

---

## Project Structure

```
colorprofiler/
├── app.py          # Entry point
├── gui.py          # UI — tray panel and profile editor
├── engine.py       # Gamma (dispwin) + DVC/Hue (NVAPI)
├── profiles.py     # Profile CRUD and config persistence
├── hotkeys.py      # Global hotkey registration
├── tray.py         # System tray icon
├── dispwin.exe     # ArgyllCMS display calibration tool
└── config.json     # User profiles (auto-generated)
```

---

## Changelog

### v1.0.3
- Splash screen on startup
- Double-click a profile to activate it instantly
- Hotkey modal redesigned: distinct color, Accept button, supports single-key hotkeys
- Monitor dropdown defaults to Display 1

### v1.0.2
- Hotkey capture replaced with a modal dialog — cleaner UX, no more accidental typing
- Gamma slider debounced (120ms) — smoother live preview, less CPU usage

### v1.0.1
- Fix: console windows no longer flash on each gamma change in the compiled build
- Fix: profiles now persist between sessions when running as a compiled `.exe` (saved to `%APPDATA%\ColorProfiler\`)

### v1.0.0
- Initial release

---

## License

MIT
