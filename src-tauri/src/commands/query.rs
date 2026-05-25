use crate::db::repo;
use crate::error::{AppError, Result};
use crate::models::*;
use chrono::Utc;

#[tauri::command]
pub fn list_queries(
    state: tauri::State<'_, crate::db::DbState>,
    payload: ListQueriesPayload,
) -> Result<Vec<Query>> {
    let conn = state
        .0
        .lock()
        .map_err(|e| AppError::Internal(e.to_string()))?;
    repo::list_queries(
        &conn,
        &payload.project_id,
        payload.status.as_deref(),
        payload.limit,
        payload.offset,
    )
}

#[tauri::command]
pub fn submit_answer(
    state: tauri::State<'_, crate::db::DbState>,
    payload: SubmitAnswerPayload,
) -> Result<Answer> {
    let conn = state
        .0
        .lock()
        .map_err(|e| AppError::Internal(e.to_string()))?;

    if payload.selected_choice_ids.is_empty() && payload.free_text.as_ref().map(|s| s.is_empty()).unwrap_or(true) {
        return Err(AppError::Internal("Answer cannot be empty".to_string()));
    }

    let answer = Answer {
        id: uuid::Uuid::new_v4().to_string(),
        query_id: payload.query_id.clone(),
        selected_choice_ids: payload.selected_choice_ids,
        free_text: payload.free_text,
        created_at: Utc::now().to_rfc3339(),
        integrated_at: None,
    };

    repo::insert_answer(&conn, &answer)?;
    repo::update_query_status(&conn, &payload.query_id, "answered")?;
    Ok(answer)
}

#[tauri::command]
pub fn skip_query(
    state: tauri::State<'_, crate::db::DbState>,
    payload: SkipQueryPayload,
) -> Result<Query> {
    let conn = state
        .0
        .lock()
        .map_err(|e| AppError::Internal(e.to_string()))?;
    repo::update_query_status(&conn, &payload.query_id, "skipped")?;
    repo::get_query(&conn, &payload.query_id)?
        .ok_or(AppError::QueryNotFound)
}
