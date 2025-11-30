#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{
  menu::{Menu, MenuItem},
  tray::TrayIconBuilder,
};
use tauri::Manager;


fn main() {

    tauri::Builder::default()
        .setup(|app| {
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
                    Code, GlobalShortcutExt, Modifiers, Shortcut, ShortcutState,
                };

                let hotkey = Shortcut::new(Some(Modifiers::CONTROL), Code::Space);

                app.handle().plugin(
                    tauri_plugin_global_shortcut::Builder::new()
                        .with_handler(move |app, shortcut, event| {
                            if shortcut == &hotkey {
                                if let ShortcutState::Pressed = event.state() {
                                    if let Some(window) = app.get_webview_window("main") {
                                        if let Ok(cursor_pos) = window.cursor_position() {
                                            let pos = tauri::PhysicalPosition {
                                                x: cursor_pos.x as i32,
                                                y: cursor_pos.y as i32,
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



        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
