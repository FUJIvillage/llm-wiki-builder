use reqwest;
use serde::{Deserialize, Serialize};

use crate::error::{AppError, Result};

#[derive(Debug, Serialize)]
pub struct Message {
    pub role: String,
    pub content: String,
}

#[derive(Debug, Serialize)]
struct ChatCompletionRequest {
    model: String,
    messages: Vec<Message>,
    temperature: f64,
    max_tokens: i64,
    #[serde(skip_serializing_if = "Option::is_none")]
    response_format: Option<ResponseFormat>,
}

#[derive(Debug, Serialize)]
struct ResponseFormat {
    #[serde(rename = "type")]
    format_type: String,
}

#[derive(Debug, Deserialize)]
pub struct ChatCompletionResponse {
    pub choices: Vec<Choice>,
    pub usage: Option<Usage>,
}

#[derive(Debug, Deserialize)]
pub struct Choice {
    pub message: MessageResponse,
}

#[derive(Debug, Deserialize)]
pub struct MessageResponse {
    pub content: String,
}

#[derive(Debug, Deserialize)]
pub struct Usage {
    pub prompt_tokens: i64,
    pub completion_tokens: i64,
}

pub struct OpenAiCompatibleClient {
    client: reqwest::Client,
    endpoint: String,
    api_key: String,
    model: String,
}

impl OpenAiCompatibleClient {
    pub fn new(endpoint: String, api_key: String, model: String) -> Self {
        Self {
            client: reqwest::Client::new(),
            endpoint,
            api_key,
            model,
        }
    }

    pub async fn chat(
        &self,
        messages: Vec<Message>,
        temperature: f64,
        max_tokens: i64,
    ) -> Result<ChatCompletionResponse> {
        let request = ChatCompletionRequest {
            model: self.model.clone(),
            messages,
            temperature,
            max_tokens,
            response_format: Some(ResponseFormat {
                format_type: "json_object".to_string(),
            }),
        };

        let response = self
            .client
            .post(format!("{}/chat/completions", self.endpoint))
            .header("Authorization", format!("Bearer {}", self.api_key))
            .header("Content-Type", "application/json")
            .json(&request)
            .timeout(std::time::Duration::from_secs(30))
            .send()
            .await
            .map_err(|e| {
                if e.is_timeout() {
                    AppError::LlmTimeout
                } else {
                    AppError::LlmInvalidResponse(e.to_string())
                }
            })?;

        let status = response.status();
        if status == 429 {
            return Err(AppError::LlmRateLimited);
        }
        if !status.is_success() {
            let text = response.text().await.unwrap_or_default();
            return Err(AppError::LlmInvalidResponse(format!(
                "HTTP {}: {}",
                status, text
            )));
        }

        let body = response
            .json::<ChatCompletionResponse>()
            .await
            .map_err(|e| AppError::LlmInvalidResponse(e.to_string()))?;

        Ok(body)
    }
}
