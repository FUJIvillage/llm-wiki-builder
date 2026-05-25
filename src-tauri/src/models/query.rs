use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Query {
    pub id: String,
    pub project_id: String,
    pub question: String,
    pub context: String,
    pub query_type: QueryType,
    pub choices: Vec<Choice>,
    pub priority_score: f64,
    pub status: QueryStatus,
    pub llm_generated: bool,
    pub raw_file_refs: Vec<String>,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum QueryType {
    YesNo,
    SingleSelect,
    MultiSelect,
    Scale,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum QueryStatus {
    Pending,
    Answered,
    Skipped,
    Archived,
}

impl std::fmt::Display for QueryStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            QueryStatus::Pending => write!(f, "pending"),
            QueryStatus::Answered => write!(f, "answered"),
            QueryStatus::Skipped => write!(f, "skipped"),
            QueryStatus::Archived => write!(f, "archived"),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Choice {
    pub id: String,
    pub label: String,
    pub description: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ListQueriesPayload {
    pub project_id: String,
    #[serde(default)]
    pub status: Option<String>,
    #[serde(default = "default_limit")]
    pub limit: i64,
    #[serde(default)]
    pub offset: i64,
}

fn default_limit() -> i64 {
    50
}
