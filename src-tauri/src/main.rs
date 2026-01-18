#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{
  menu::{Menu, MenuItem},
  tray::TrayIconBuilder,
};
use tauri::Manager;
use meval;
use window_vibrancy::{apply_blur};

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
                    "quit" => {
                    app.exit(0);
                    }
                    _ => {
                    println!("menu item {:?} not handled", event.id);
                    }})
                .build(app);

            {
                use tauri_plugin_global_shortcut::{
                    Code, GlobalShortcutExt, Shortcut, ShortcutState,
                };

                let hotkey = Shortcut::new(None, Code::F13);

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
                                    } else {
                                        println!("Main window does not exist yet.");
                                    }
                                }
                            }
                        })
                        .build(),
                )?;

                app.global_shortcut().register(hotkey)?;
            }

            Ok(())
        })

        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                window.hide().unwrap();
                api.prevent_close();
            }
        })

        .invoke_handler(tauri::generate_handler![evaluate_math])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

#[tauri::command]
fn evaluate_math(expr: String) -> Result<String, String> {
    let expr = expr.replace("^", "**");

    match meval::eval_str(expr) {
        Ok(val) => {
            let rounded = (val * 1e12).round() / 1e12;
            Ok(rounded.to_string())
        }
        Err(_) => Err("Invalid expression".into()),
    }
}
