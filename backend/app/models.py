from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    raw_path: Optional[str] = None
    wiki_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    queries: List["Query"] = Relationship(back_populates="project")


class Query(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", index=True)
    question: str
    context: Optional[str] = None
    query_type: str = Field(default="yes_no")  # yes_no, single_select, multi_select
    choices_json: Optional[str] = None  # JSON string of choices
    priority_score: float = Field(default=0.5)
    status: str = Field(default="pending")  # pending, answered, skipped
    llm_generated: bool = Field(default=False)
    raw_file_refs_json: Optional[str] = None  # JSON string of file refs
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    project: Optional[Project] = Relationship(back_populates="queries")
    answers: List["Answer"] = Relationship(back_populates="query")


class Answer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    query_id: int = Field(foreign_key="query.id", index=True)
    selected_choice_ids_json: str = Field(default="[]")  # JSON string of choice IDs
    free_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    integrated_at: Optional[datetime] = None

    query: Optional[Query] = Relationship(back_populates="answers")
