#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{
    menu::{Menu, MenuItem},
    tray::TrayIconBuilder,
    Manager,
};
use tauri_plugin_global_shortcut::{Code, GlobalShortcutExt, Modifiers, Shortcut, ShortcutState};
use window_vibrancy::apply_blur;
use serde::{Deserialize, Serialize};
use std::fs;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Settings {
    pub shortcut_key: String,
    pub shortcut_mods: Vec<String>,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            shortcut_key: "F13".to_string(),
            shortcut_mods: vec![],
        }
    }
}

fn settings_path(app: &tauri::AppHandle) -> std::path::PathBuf {
    app.path()
        .app_config_dir()
        .expect("Could not resolve app config dir")
        .join("settings.json")
}

fn load_settings(app: &tauri::AppHandle) -> Settings {
    let path = settings_path(app);
    if let Ok(data) = fs::read_to_string(&path) {
        serde_json::from_str(&data).unwrap_or_default()
    } else {
        Settings::default()
    }
}

fn save_settings_to_disk(app: &tauri::AppHandle, settings: &Settings) -> Result<(), String> {
    let path = settings_path(app);
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).map_err(|e| e.to_string())?;
    }
    let data = serde_json::to_string_pretty(settings).map_err(|e| e.to_string())?;
    fs::write(&path, data).map_err(|e| e.to_string())
}

fn build_shortcut(settings: &Settings) -> Result<Shortcut, String> {
    let mut mods = Modifiers::empty();
    for m in &settings.shortcut_mods {
        match m.as_str() {
            "Ctrl"  => mods |= Modifiers::CONTROL,
            "Alt"   => mods |= Modifiers::ALT,
            "Shift" => mods |= Modifiers::SHIFT,
            "Super" => mods |= Modifiers::SUPER,
            _ => {}
        }
    }

    let code = key_str_to_code(&settings.shortcut_key)
        .ok_or_else(|| format!("Unknown key: {}", settings.shortcut_key))?;

    let modifier_opt = if mods.is_empty() { None } else { Some(mods) };
    Ok(Shortcut::new(modifier_opt, code))
}

fn key_str_to_code(key: &str) -> Option<Code> {
    if let Some(n) = key.strip_prefix('F').and_then(|n| n.parse::<u8>().ok()) {
        return match n {
            1  => Some(Code::F1),   2  => Some(Code::F2),   3  => Some(Code::F3),
            4  => Some(Code::F4),   5  => Some(Code::F5),   6  => Some(Code::F6),
            7  => Some(Code::F7),   8  => Some(Code::F8),   9  => Some(Code::F9),
            10 => Some(Code::F10),  11 => Some(Code::F11),  12 => Some(Code::F12),
            13 => Some(Code::F13),  14 => Some(Code::F14),  15 => Some(Code::F15),
            16 => Some(Code::F16),  17 => Some(Code::F17),  18 => Some(Code::F18),
            19 => Some(Code::F19),  20 => Some(Code::F20),
            _ => None,
        };
    }
    match key {
        "A" => Some(Code::KeyA), "B" => Some(Code::KeyB), "C" => Some(Code::KeyC),
        "D" => Some(Code::KeyD), "E" => Some(Code::KeyE), "F" => Some(Code::KeyF),
        "G" => Some(Code::KeyG), "H" => Some(Code::KeyH), "I" => Some(Code::KeyI),
        "J" => Some(Code::KeyJ), "K" => Some(Code::KeyK), "L" => Some(Code::KeyL),
        "M" => Some(Code::KeyM), "N" => Some(Code::KeyN), "O" => Some(Code::KeyO),
        "P" => Some(Code::KeyP), "Q" => Some(Code::KeyQ), "R" => Some(Code::KeyR),
        "S" => Some(Code::KeyS), "T" => Some(Code::KeyT), "U" => Some(Code::KeyU),
        "V" => Some(Code::KeyV), "W" => Some(Code::KeyW), "X" => Some(Code::KeyX),
        "Y" => Some(Code::KeyY), "Z" => Some(Code::KeyZ),
        "0" => Some(Code::Digit0), "1" => Some(Code::Digit1),
        "2" => Some(Code::Digit2), "3" => Some(Code::Digit3),
        "4" => Some(Code::Digit4), "5" => Some(Code::Digit5),
        "6" => Some(Code::Digit6), "7" => Some(Code::Digit7),
        "8" => Some(Code::Digit8), "9" => Some(Code::Digit9),
        "Space"      => Some(Code::Space),
        "Tab"        => Some(Code::Tab),
        "Enter"      => Some(Code::Enter),
        "Backspace"  => Some(Code::Backspace),
        "Delete"     => Some(Code::Delete),
        "Insert"     => Some(Code::Insert),
        "Home"       => Some(Code::Home),
        "End"        => Some(Code::End),
        "PageUp"     => Some(Code::PageUp),
        "PageDown"   => Some(Code::PageDown),
        "ArrowUp"    => Some(Code::ArrowUp),
        "ArrowDown"  => Some(Code::ArrowDown),
        "ArrowLeft"  => Some(Code::ArrowLeft),
        "ArrowRight" => Some(Code::ArrowRight),
        _ => None,
    }
}

#[tauri::command]
fn get_settings(app: tauri::AppHandle) -> Settings {
    load_settings(&app)
}

#[tauri::command]
fn save_settings(app: tauri::AppHandle, settings: Settings) -> Result<(), String> {
    build_shortcut(&settings)?;
    save_settings_to_disk(&app, &settings)?;

    let new_shortcut = build_shortcut(&settings)?;
    let shortcut_ext = app.global_shortcut();
    shortcut_ext.unregister_all().map_err(|e| e.to_string())?;

    shortcut_ext.on_shortcut(new_shortcut, move |app, _shortcut, event| {
        if let ShortcutState::Pressed = event.state() {
            if let Some(window) = app.get_webview_window("main") {
                if let Ok(cursor_pos) = window.cursor_position() {
                    let window_size = window.outer_size().unwrap_or_default();
                    let pos = tauri::PhysicalPosition {
                        x: cursor_pos.x as i32 - (window_size.width / 2) as i32,
                        y: cursor_pos.y as i32 - (window_size.height / 2) as i32,
                    };
                    let _ = window.set_position(pos);
                }
                let _ = window.show();
                let _ = window.set_focus();
            }
        }
    }).map_err(|e| e.to_string())?;

    Ok(())
}

#[tauri::command]
fn evaluate_math(expr: String) -> Result<String, String> {
    let expr = expr.replace('^', "**");
    match meval::eval_str(expr) {
        Ok(val) => {
            let rounded = (val * 1e12).round() / 1e12;
            Ok(rounded.to_string())
        }
        Err(_) => Err("Invalid expression".into()),
    }
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            #[cfg(target_os = "windows")]
            {
                let window = app.get_webview_window("main").unwrap();
                apply_blur(&window, Some((18, 18, 18, 125)))
                    .expect("apply_blur failed");
            }

            #[cfg(desktop)]
            let quit_i = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&quit_i])?;

            let _tray = TrayIconBuilder::new()
                .menu(&menu)
                .show_menu_on_left_click(true)
                .icon(app.default_window_icon().unwrap().clone())
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "quit" => app.exit(0),
                    _ => println!("menu item {:?} not handled", event.id),
                })
                .build(app)?;

            let settings = load_settings(app.handle());
            let hotkey = build_shortcut(&settings)
                .unwrap_or_else(|_| Shortcut::new(None, Code::F13));

            app.handle().plugin(
                tauri_plugin_global_shortcut::Builder::new()
                    .with_handler(move |app, shortcut, event| {
                        if shortcut == &hotkey {
                            if let ShortcutState::Pressed = event.state() {
                                if let Some(window) = app.get_webview_window("main") {
                                    if let Ok(cursor_pos) = window.cursor_position() {
                                        let window_size = window.outer_size().unwrap_or_default();
                                        let pos = tauri::PhysicalPosition {
                                            x: cursor_pos.x as i32 - (window_size.width / 2) as i32,
                                            y: cursor_pos.y as i32 - (window_size.height / 2) as i32,
                                        };
                                        let _ = window.set_position(pos);
                                    }
                                    let _ = window.show();
                                    let _ = window.set_focus();
                                }
                            }
                        }
                    })
                    .build(),
            )?;

            app.global_shortcut().register(hotkey)?;

            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                window.hide().unwrap();
                api.prevent_close();
            }
        })
        .invoke_handler(tauri::generate_handler![evaluate_math, get_settings, save_settings])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}