use chrono::Utc;
use std::path::Path;
use uuid::Uuid;

use crate::db::repo;
use crate::error::{AppError, Result};
use crate::models::*;

#[tauri::command]
pub fn create_project(
    state: tauri::State<'_, crate::db::DbState>,
    payload: CreateProjectPayload,
) -> Result<Project> {
    let raw = Path::new(&payload.raw_path);
    if !raw.exists() {
        return Err(AppError::PathInvalid(
            "raw_path does not exist".to_string(),
        ));
    }

    let wiki = Path::new(&payload.wiki_path);
    if !wiki.exists() {
        std::fs::create_dir_all(wiki)?;
    }

    let id = Uuid::new_v4().to_string();
    let now = Utc::now().to_rfc3339();
    let project = Project {
        id: id.clone(),
        name: payload.name,
        raw_path: raw.canonicalize()?.to_string_lossy().to_string(),
        wiki_path: wiki.canonicalize()?.to_string_lossy().to_string(),
        llm_endpoint: payload.llm_endpoint,
        llm_model: payload.llm_model,
        settings: ProjectSettings::default(),
        created_at: now.clone(),
        updated_at: now,
    };

    let conn = state.0.lock().map_err(|e| AppError::Internal(e.to_string()))?;
    repo::create_project(&conn, &project, &payload.llm_api_key)?;
    // TODO: store api_key in OS keyring
    Ok(project)
}

#[tauri::command]
pub fn list_projects(state: tauri::State<'_, crate::db::DbState>) -> Result<Vec<ProjectSummary>> {
    let conn = state.0.lock().map_err(|e| AppError::Internal(e.to_string()))?;
    repo::list_projects(&conn)
}

#[tauri::command]
pub fn get_project(
    state: tauri::State<'_, crate::db::DbState>,
    project_id: String,
) -> Result<Project> {
    let conn = state.0.lock().map_err(|e| AppError::Internal(e.to_string()))?;
    repo::get_project(&conn, &project_id)?
        .ok_or(AppError::ProjectNotFound)
}

#[tauri::command]
pub fn delete_project(
    state: tauri::State<'_, crate::db::DbState>,
    project_id: String,
) -> Result<bool> {
    let conn = state.0.lock().map_err(|e| AppError::Internal(e.to_string()))?;
    repo::delete_project(&conn, &project_id)?;
    Ok(true)
}
