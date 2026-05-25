from typing import List, Optional
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    raw_path: Optional[str] = None
    wiki_path: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    raw_path: Optional[str]
    wiki_path: Optional[str]
    created_at: str
    updated_at: str
    pending_query_count: int = 0
    total_answer_count: int = 0


class Choice(BaseModel):
    id: str
    label: str
    description: Optional[str] = None


class QueryCreate(BaseModel):
    question: str
    context: Optional[str] = None
    query_type: str = "yes_no"
    choices: Optional[List[Choice]] = None
    priority_score: float = 0.5


class QueryResponse(BaseModel):
    id: int
    project_id: int
    question: str
    context: Optional[str]
    query_type: str
    choices: List[Choice]
    priority_score: float
    status: str
    llm_generated: bool
    raw_file_refs: List[str]
    created_at: str
    updated_at: str


class AnswerCreate(BaseModel):
    selected_choice_ids: List[str]
    free_text: Optional[str] = None


class AnswerResponse(BaseModel):
    id: int
    query_id: int
    selected_choice_ids: List[str]
    free_text: Optional[str]
    created_at: str


class WikiPageResponse(BaseModel):
    project_id: int
    title: str
    content: str
    updated_at: str
    source_queries: int


class SearchResult(BaseModel):
    type: str  # "query", "project"
    id: int
    title: str
    snippet: str
    project_id: int


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]


class ExportResponse(BaseModel):
    format: str
    filename: str
    content: str
