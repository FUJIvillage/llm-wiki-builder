pub mod commands;
pub mod db;
pub mod error;
pub mod indexer;
pub mod llm;
pub mod models;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let app_data_dir = dirs::data_dir()
        .unwrap_or(std::path::PathBuf::from("."))
        .join("llm-wiki-builder");

    let db_state = match db::init_db(app_data_dir) {
        Ok(state) => state,
        Err(e) => {
            eprintln!("Failed to initialize database: {e}");
            std::process::exit(1);
        }
    };

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .manage(db_state)
        .invoke_handler(tauri::generate_handler![
            commands::project::create_project,
            commands::project::list_projects,
            commands::project::get_project,
            commands::project::delete_project,
            commands::query::list_queries,
            commands::query::submit_answer,
            commands::query::skip_query,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
