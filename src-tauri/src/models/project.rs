use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IndexResult {
    pub scanned_files: i64,
    pub indexed_files: i64,
    pub skipped_files: i64,
    pub total_bytes: i64,
    pub duration_ms: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Project {
    pub id: String,
    pub name: String,
    pub raw_path: String,
    pub wiki_path: String,
    pub llm_endpoint: String,
    pub llm_model: String,
    pub settings: ProjectSettings,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ProjectSettings {
    #[serde(default)]
    pub auto_integrate: bool,
    #[serde(default = "default_threshold")]
    pub auto_integrate_threshold: i64,
}

fn default_threshold() -> i64 {
    10
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectSummary {
    pub id: String,
    pub name: String,
    pub pending_query_count: i64,
    pub total_answer_count: i64,
    pub last_indexed_at: Option<String>,
    pub created_at: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct CreateProjectPayload {
    pub name: String,
    pub raw_path: String,
    pub wiki_path: String,
    pub llm_endpoint: String,
    pub llm_model: String,
    pub llm_api_key: String,
}
