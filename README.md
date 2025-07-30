# Control-PC-with-PS4-Controller

[Read in Turkish / Türkçe için tıklayın](README-TR.md)

## Description

An app made with Python for using the mouse, keyboard & some shortcuts, writing with speech, changing tabs etc.

## Controls

| 🎮 Control                  | 💻 Function                        |
|----------------------------|------------------------------------|
| Left analog                 | Move mouse      |
| Right analog                | Scroll up/down (also horizontal scroll for OS X and Linux, sometimes works on Windows too) |
| X / L3                      | Left click                         |
| R3                          | Right click                        |
| Square                      | Backspace                            |
| Triangle                    | Space                              |
| Circle                      | ESC                                |
| Share                       | Enter                              |
| D-pad                       | Arrow keys                         |
| Hold R1                     | Hold Shift                         |
| R1 (single press)           | Copy                               |
| R1 (double press)           | Cut                                |
| L1                          | Paste                              |
| R2 (single press)           | Undo                               |
| R2 (double press)           | Redo                               |
| Hold L2                     | Hold Alt                           |
| Hold L2 + Right D-pad       | Alt + Tab                                |
| Touchpad                    | Toggle on-screen keyboard (Windows)          |
| Options                     | Toggle speech-to-text              |


💡 **Tips:**
- While holding R1, you can select text with the D-pad, then copy/cut with R1 and paste with L1.
- While holding L2, use the right D-pad to switch between tabs!

⚠️ **Warning:** The app was only tested on Windows 11.

ℹ️ **Info:** To use the on-screen keyboard (Windows), go to On-Screen Keyboard > Options > Hover over keys > Set hover duration to 3 seconds.

ℹ️ **Info:** To use speech-to-text, you need to create a [Speechmatics](https://www.speechmatics.com/) account and enter your API key in the app. Speechmatics offers a good amount of free usage.

ℹ️ **Info:** API key information is stored in `settings.json` file. You can delete it manually or through the app by leaving the input empty and clicking save.

## Installation

1. Clone the project:
   ```bash
   git clone https://github.com/AlperBayraktar/Control-PC-with-PS4-Controller.git
   cd Control-PC-with-PS4-Controller
   ```
2. (Optional) Create a virtual environment:
   - Windows:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python main.py
   ```
5. (For speech-to-text) Enter your Speechmatics API key in the app.

## AI Usage

A significant part of the application's UI and threading code was written by AI. I only made some corrections.

## License

[MIT License.](LICENSE)
