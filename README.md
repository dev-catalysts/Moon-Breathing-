# 🌙 Moon Breathing Cursor — Premium Edition

A stunning desktop cursor effect for Windows that adds ethereal moon-breathing smoke trails, glowing crescents, magic circles, and particle effects to your mouse pointer.

**Made by Umang Sharma — dev.catalyst**

---

![Platform](https://img.shields.io/badge/Platform-Windows-blue?style=for-the-badge&logo=windows)
![Python](https://img.shields.io/badge/Python-3.9%2B-yellow?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## ✨ Features

- 🌫 **Ethereal Smoke Trails** — Dynamic smoke particles follow your cursor
- ✨ **Glowing Trail** — Catmull-Rom spline-based smooth light trails
- 🌙 **Crescent Particles** — Floating moon crescents orbit around your cursor
- 🔮 **Magic Circles** — Click to spawn animated magic circle runes
- 💥 **Shockwave Rings** — Beautiful ripple effects on click
- ⚡ **Spark Particles** — Tiny sparks burst out as you move
- 🎨 **6 Color Themes** — Purple, Blue, Crimson, Cyan, Gold, Emerald
- ⚙ **Settings Panel** — Adjust smoke intensity, trail length, color theme
- 🖥 **System Tray** — Minimize to tray, runs silently in the background
- 🚀 **Start on Windows Startup** — Optional auto-start toggle

---

## 🚀 Quick Start

### Option 1: Run the `.exe` (No setup needed)

1. Download `moon_breathing_cursor.exe` from [Releases](../../releases)
2. Double-click to launch
3. A splash screen appears → settings panel opens → effects start immediately
4. Right-click the tray icon (🌙) to access settings or quit

### Option 2: Run from Source (CLI-based)

#### Prerequisites

- **Python 3.9+** — [Download Python](https://www.python.org/downloads/)
- **Windows 10/11** (required for system-level overlay and input hooks)

#### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/moon-breathing-cursor.git
cd moon-breathing-cursor

# 2. (Recommended) Create a virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

#### Run

```bash
python moon_breathing_cursor.py
```

That's it! The cursor effect starts immediately.

---

## 🎮 Controls

| Action | Effect |
|---|---|
| **Move mouse** | Smoke trail + sparks + crescents follow your cursor |
| **Left click** | Magic circle + shockwave + burst particles |
| **Press ESC** | Quit the application |
| **Tray icon → double-click** | Open settings panel |
| **Tray icon → right-click** | Settings / Quit menu |

---

## ⚙ Settings

Open the settings panel by double-clicking the system tray icon (🌙).

| Setting | Description |
|---|---|
| **🌫 Smoke Intensity** | Controls how many smoke particles spawn (0–100%) |
| **✨ Trail Length** | Controls how long the glowing trail persists (0–100%) |
| **🎨 Color Theme** | Choose from 6 premium color themes |
| **⚙ Start on Startup** | Toggle auto-start with Windows |

Settings are saved automatically to `moon_cursor_settings.json` in the app directory.

---

## 📁 Project Structure

```
moon-breathing-cursor/
├── moon_breathing_cursor.py    # Main application source code
├── moon_breathing_cursor.exe   # Pre-built Windows executable
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── moon_cursor_settings.json   # Auto-generated settings (after first run)
```

---

## 🔧 Building the EXE Yourself

If you want to build the executable from source:

```bash
# Install PyInstaller
pip install pyinstaller

# Build single-file executable
pyinstaller --noconfirm --onefile --windowed --name "moon_breathing_cursor" moon_breathing_cursor.py
```

The `.exe` will be generated in the `dist/` folder.

---

## 🎨 Color Themes

| Theme | Preview Colors |
|---|---|
| **Purple** | 💜 Violet, lavender, gold accents |
| **Blue** | 💙 Ocean blue, cyan highlights |
| **Crimson** | ❤️ Deep red, warm orange accents |
| **Cyan** | 🩵 Teal, aqua, electric blue |
| **Gold** | 💛 Amber, warm golden glow |
| **Emerald** | 💚 Forest green, mint highlights |

---

## ⚠ Notes

- This app creates a **transparent full-screen overlay** on top of your desktop. All clicks and keyboard input pass through to the applications below.
- The app requires **Windows** (uses `winreg` for startup, `ctypes` for DPI awareness).
- If you see no effects, make sure your display scaling (DPI) is set correctly or try running as administrator.

---

## 📜 License

MIT License — Free to use, modify, and distribute.

---

<p align="center">
  <b>Made with 💜 by Umang Sharma — dev.catalyst</b><br>
  <i>Moon Breathing Cursor • Premium Edition</i>
</p>
