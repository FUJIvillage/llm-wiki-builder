export interface CreateProjectPayload {
  name: string;
  raw_path: string;
  wiki_path: string;
  llm_endpoint: string;
  llm_model: string;
  llm_api_key: string;
}

export interface IndexResult {
  scanned_files: number;
  indexed_files: number;
  skipped_files: number;
  total_bytes: number;
  duration_ms: number;
}

export interface Project {
  id: string;
  name: string;
  raw_path: string;
  wiki_path: string;
  llm_endpoint: string;
  llm_model: string;
  settings: ProjectSettings;
  created_at: string;
  updated_at: string;
}

export interface ProjectSettings {
  auto_integrate?: boolean;
  auto_integrate_threshold?: number;
}

export interface ProjectSummary {
  id: string;
  name: string;
  pending_query_count: number;
  total_answer_count: number;
  last_indexed_at: string | null;
  created_at: string;
}

export interface SkipQueryPayload {
  query_id: string;
}

export interface SubmitAnswerPayload {
  query_id: string;
  selected_choice_ids: string[];
  free_text?: string | null;
}

export interface ListQueriesPayload {
  project_id: string;
  status?: string | null;
  limit: number;
  offset: number;
}

export interface Query {
  id: string;
  project_id: string;
  question: string;
  context: string;
  query_type: 'yes_no' | 'single_select' | 'multi_select' | 'scale';
  choices: Choice[];
  priority_score: number;
  status: 'pending' | 'answered' | 'skipped' | 'archived';
  llm_generated: boolean;
  raw_file_refs: string[];
  created_at: string;
  updated_at: string;
}

export interface Choice {
  id: string;
  label: string;
  description?: string;
}

export interface Answer {
  id: string;
  query_id: string;
  selected_choice_ids: string[];
  free_text: string | null;
  created_at: string;
  integrated_at: string | null;
}
