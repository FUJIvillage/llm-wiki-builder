pub fn query_generation_prompt(context_text: &str) -> String {
    format!(
        r#"You are a knowledge curator AI. Given the following raw notes, generate 5–10 high-importance clarification questions that would help build a structured wiki.

Rules:
- Questions must be selectable (yes/no, single-select, or multi-select). No open-ended questions.
- Each question must include 2–5 choices with short labels.
- Assign a priority_score (0.0–1.0) based on structural importance (e.g., "Is this a core concept?" = 0.95, "Tag color preference" = 0.3).
- Include a "context" field explaining why this question matters.
- Reference any relevant file paths in "raw_file_refs".

Respond in JSON format:
{{
  "queries": [
    {{
      "question": "string",
      "context": "string",
      "query_type": "yes_no|single_select|multi_select",
      "choices": [{{"id":"c1","label":"Yes"}}],
      "priority_score": 0.9,
      "raw_file_refs": ["path/to/file.md"]
    }}
  ]
}}

Raw notes:
{context_text}
"#
    )
}
