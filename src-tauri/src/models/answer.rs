use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Answer {
    pub id: String,
    pub query_id: String,
    pub selected_choice_ids: Vec<String>,
    pub free_text: Option<String>,
    pub created_at: String,
    pub integrated_at: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct SubmitAnswerPayload {
    pub query_id: String,
    pub selected_choice_ids: Vec<String>,
    pub free_text: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct SkipQueryPayload {
    pub query_id: String,
    pub reason: Option<String>,
    pub reason_text: Option<String>,
}
