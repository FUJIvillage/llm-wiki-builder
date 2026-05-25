use serde::Serialize;
use thiserror::Error;

#[derive(Error, Debug, Serialize)]
pub enum AppError {
    #[error("PROJECT_NOT_FOUND")]
    ProjectNotFound,
    #[error("QUERY_NOT_FOUND")]
    QueryNotFound,
    #[error("PATH_INVALID: {0}")]
    PathInvalid(String),
    #[error("LLM_TIMEOUT")]
    LlmTimeout,
    #[error("LLM_RATE_LIMITED")]
    LlmRateLimited,
    #[error("LLM_INVALID_RESPONSE: {0}")]
    LlmInvalidResponse(String),
    #[error("DB_ERROR: {0}")]
    DbError(String),
    #[error("INTERNAL: {0}")]
    Internal(String),
}

impl From<anyhow::Error> for AppError {
    fn from(e: anyhow::Error) -> Self {
        AppError::Internal(e.to_string())
    }
}

impl From<rusqlite::Error> for AppError {
    fn from(e: rusqlite::Error) -> Self {
        AppError::DbError(e.to_string())
    }
}

impl From<serde_json::Error> for AppError {
    fn from(e: serde_json::Error) -> Self {
        AppError::Internal(format!("JSON error: {e}"))
    }
}

impl From<std::io::Error> for AppError {
    fn from(e: std::io::Error) -> Self {
        AppError::PathInvalid(e.to_string())
    }
}

pub type Result<T> = std::result::Result<T, AppError>;
