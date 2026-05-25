import json
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.database import create_db_and_tables, get_session
from app.models import Project, Query
from app.schemas import (
    ProjectCreate, ProjectResponse,
    QueryCreate, QueryResponse,
    AnswerCreate, AnswerResponse,
    WikiPageResponse, SearchResponse,
    ExportResponse,
)
from app.crud import (
    create_project, list_projects, get_project,
    create_query, list_queries,
    create_answer, get_wiki_page,
    search_wiki, export_project, generate_queries_for_project,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="LLM Wiki Builder API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _to_project_response(project: Project) -> ProjectResponse:
    pending = sum(1 for q in project.queries if q.status == "pending")
    answered = sum(1 for q in project.queries if q.status == "answered")
    return ProjectResponse(
        id=project.id,
        name=project.name,
        raw_path=project.raw_path,
        wiki_path=project.wiki_path,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat(),
        pending_query_count=pending,
        total_answer_count=answered,
    )


def _to_query_response(query: Query) -> QueryResponse:
    choices = json.loads(query.choices_json) if query.choices_json else []
    return QueryResponse(
        id=query.id,
        project_id=query.project_id,
        question=query.question,
        context=query.context,
        query_type=query.query_type,
        choices=[{"id": c["id"], "label": c["label"], "description": c.get("description")} for c in choices],
        priority_score=query.priority_score,
        status=query.status,
        llm_generated=query.llm_generated,
        raw_file_refs=json.loads(query.raw_file_refs_json) if query.raw_file_refs_json else [],
        created_at=query.created_at.isoformat(),
        updated_at=query.updated_at.isoformat(),
    )


@app.get("/api/projects", response_model=List[ProjectResponse])
def get_projects(db: Session = Depends(get_session)):
    projects = list_projects(db)
    return [_to_project_response(p) for p in projects]


@app.post("/api/projects", response_model=ProjectResponse)
def post_project(project: ProjectCreate, db: Session = Depends(get_session)):
    db_project = create_project(db, project)
    return _to_project_response(db_project)


@app.get("/api/projects/{project_id}/queries", response_model=List[QueryResponse])
def get_queries(project_id: int, db: Session = Depends(get_session)):
    queries = list_queries(db, project_id)
    return [_to_query_response(q) for q in queries]


@app.post("/api/projects/{project_id}/queries", response_model=QueryResponse)
def post_query(project_id: int, query: QueryCreate, db: Session = Depends(get_session)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db_query = create_query(db, project_id, query)
    return _to_query_response(db_query)


@app.post("/api/queries/{query_id}/answer", response_model=AnswerResponse)
def post_answer(query_id: int, answer: AnswerCreate, db: Session = Depends(get_session)):
    query = db.get(Query, query_id)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    db_answer = create_answer(db, query_id, answer)
    return AnswerResponse(
        id=db_answer.id,
        query_id=db_answer.query_id,
        selected_choice_ids=json.loads(db_answer.selected_choice_ids_json),
        free_text=db_answer.free_text,
        created_at=db_answer.created_at.isoformat(),
    )


@app.get("/api/projects/{project_id}/wiki")
def get_wiki(project_id: int, db: Session = Depends(get_session)):
    wiki = get_wiki_page(db, project_id)
    if not wiki:
        raise HTTPException(status_code=404, detail="Project not found")

    sections_md = "\n\n---\n\n".join(
        f"## {s['question']}\n\n{s['context']}\n\n**Answer:** {s['answer']}\n\n*Sources:* {', '.join(s['sources'])}"
        for s in wiki["sections"]
    )
    content = f"# {wiki['title']}\n\n*Generated from {wiki['source_queries']} answered queries*\n\n---\n\n{sections_md}"

    return WikiPageResponse(
        project_id=wiki["project_id"],
        title=wiki["title"],
        content=content,
        updated_at=wiki["updated_at"],
        source_queries=wiki["source_queries"],
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/search", response_model=SearchResponse)
def search(q: str = "", db: Session = Depends(get_session)):
    results = search_wiki(db, q)
    return SearchResponse(
        query=q,
        results=[
            {
                "type": r["type"],
                "id": r["id"],
                "title": r["title"],
                "snippet": r["snippet"],
                "project_id": r["project_id"],
            }
            for r in results
        ],
    )


@app.get("/api/projects/{project_id}/export", response_model=ExportResponse)
def export(project_id: int, format: str = "markdown", db: Session = Depends(get_session)):
    result = export_project(db, project_id, format)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return ExportResponse(**result)


@app.post("/api/projects/{project_id}/generate")
def generate_queries(project_id: int, db: Session = Depends(get_session)):
    count = generate_queries_for_project(db, project_id)
    if count == 0:
        raise HTTPException(status_code=400, detail="No queries generated. Check raw_path exists and contains .md files.")
    return {"generated": count}
