/// Application entry point for the tkk-UniversalValidator desktop shell.
/// The web frontend (React SPA) is loaded from the embedded dist or the dev server.
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .run(tauri::generate_context!())
        .expect("error while running tauri application")
}
