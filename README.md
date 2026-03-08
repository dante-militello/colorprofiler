# ColorProfiler

> Display color profiles for NVIDIA GPUs — gamma, vibrance and hue, per monitor, from your system tray.

<!-- screenshot -->
<p align="center">
  [<img src="screenshot.png" alt="ColorProfiler UI" width="420"/>](https://i.imgur.com/nn8Kp86.png)
</p>

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

## License

MIT
