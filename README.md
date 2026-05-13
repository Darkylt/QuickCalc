# QuickCalc

QuickCalc is a personal and tiny always-on utility for fast calculations and quick scratchpad notes without breaking your flow state.

It lives quietly in your system tray and can be summoned instantly with a global hotkey (default: **F13**). No launching apps. No switching contexts. Just press the key and start typing.

## What it does

QuickCalc opens a small floating input window where you can type anything. It will scan your input for simple math expressions and evaluate them on the fly.

Example:

```
test 2+2=
```

QuickCalc detects the expression and shows the result in the corner. You can then press `Tab` to insert the result directly into your text.

It’s designed for speed and low friction rather than full calculator features.

## Core idea

The goal is simple: reduce the cognitive cost of doing quick calculations or jotting things down while working.

If you’re in the middle of something, you shouldn’t have to:

* open a calculator
* switch windows
* break your focus
* think about formatting

You just press a key and continue thinking.

## Features

* Global hotkey launcher (default: **F13**)
* Always runs in the system tray
* Lightweight floating input window
* Inline math detection in free text
* Instant evaluation preview
* `Tab` inserts computed result into the text

## Installation (Windows)

QuickCalc currently only supports Windows.

### Option 1: Download release

1. Go to the **Releases** page of this repository
2. Download the latest `.exe` build
3. Run it once. QuickCalc will launch and initialize

After first launch:

* The UI opens and lets you configure the hotkey via the settings menu
* Once configured, you can close the window
* The app will stay running in the system tray

From that point on, it just waits patiently for the hotkey.

### Option 2: Build from source

Requires Node.js + Rust (for Tauri).

```bash
git clone https://github.com/Darkylt/QuickCalc
cd QuickCalc
npm install
npm run tauri build
```

This will produce a Windows executable in `src-tauri\target\release` folder.

## Autostart (recommended)

To make QuickCalc start automatically when Windows boots:

### Method 1: Startup folder

1. Press `Win + R`
2. Type:

   ```
   shell:startup
   ```
3. Press Enter
4. Copy the QuickCalc `.exe` (or a shortcut to it) into that folder

Windows will now launch QuickCalc automatically on login.

### Method 2: Task Manager

1. Open **Task Manager**
2. Go to the **Startup** tab
3. Click **Enable startup app** (or “Run new task” depending on version)
4. Add QuickCalc executable if needed

---

Once set up, the intended workflow is:
launch once -> set hotkey -> close window -> forget it exists until you press the key again


## Have fun