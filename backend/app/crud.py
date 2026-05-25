import json
import os
from typing import List, Optional
from sqlmodel import Session, select
from app.models import Project, Query, Answer
from app.schemas import ProjectCreate, QueryCreate, AnswerCreate


def create_project(db: Session, project: ProjectCreate) -> Project:
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_project(db: Session, project_id: int) -> Optional[Project]:
    return db.get(Project, project_id)


def list_projects(db: Session) -> List[Project]:
    return db.exec(select(Project)).all()


def create_query(db: Session, project_id: int, query: QueryCreate) -> Query:
    choices_json = json.dumps([c.model_dump() for c in query.choices]) if query.choices else None
    db_query = Query(
        project_id=project_id,
        question=query.question,
        context=query.context,
        query_type=query.query_type,
        choices_json=choices_json,
        priority_score=query.priority_score,
    )
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query


def list_queries(db: Session, project_id: int) -> List[Query]:
    return db.exec(select(Query).where(Query.project_id == project_id)).all()


def create_answer(db: Session, query_id: int, answer: AnswerCreate) -> Answer:
    db_answer = Answer(
        query_id=query_id,
        selected_choice_ids_json=json.dumps(answer.selected_choice_ids),
        free_text=answer.free_text,
    )
    db.add(db_answer)

    # Mark query as answered
    query = db.get(Query, query_id)
    if query:
        query.status = "answered"
        db.add(query)

    db.commit()
    db.refresh(db_answer)
    return db_answer


def get_wiki_page(db: Session, project_id: int) -> dict:
    project = db.get(Project, project_id)
    if not project:
        return None

    queries = db.exec(
        select(Query).where(
            Query.project_id == project_id,
            Query.status == "answered"
        )
    ).all()

    sections = []
    for q in queries:
        answers = db.exec(select(Answer).where(Answer.query_id == q.id)).all()
        choices = json.loads(q.choices_json) if q.choices_json else []
        answer_texts = []
        for ans in answers:
            selected_ids = json.loads(ans.selected_choice_ids_json)
            selected_labels = [c["label"] for c in choices if c["id"] in selected_ids]
            answer_texts.extend(selected_labels)

        sections.append({
            "question": q.question,
            "context": q.context or "",
            "answer": ", ".join(answer_texts) if answer_texts else "No answer",
            "sources": json.loads(q.raw_file_refs_json) if q.raw_file_refs_json else [],
        })

    return {
        "project_id": project_id,
        "title": f"{project.name} Wiki",
        "sections": sections,
        "updated_at": project.updated_at.isoformat(),
        "source_queries": len(sections),
    }


def search_wiki(db: Session, query: str) -> List[dict]:
    """Full-text search across projects and queries."""
    search_pattern = f"%{query}%"
    results = []

    # Search projects by name
    projects = db.exec(
        select(Project).where(Project.name.ilike(search_pattern))
    ).all()
    for p in projects:
        results.append({
            "type": "project",
            "id": p.id,
            "title": p.name,
            "snippet": f"Project with {len(p.queries)} queries",
            "project_id": p.id,
        })

    # Search queries by question or context
    queries_found = db.exec(
        select(Query).where(
            (Query.question.ilike(search_pattern)) |
            (Query.context.ilike(search_pattern))
        )
    ).all()
    for q in queries_found:
        # Skip if already added as project result
        if any(r["id"] == q.project_id and r["type"] == "project" for r in results):
            pass
        results.append({
            "type": "query",
            "id": q.id,
            "title": q.question,
            "snippet": q.context or "",
            "project_id": q.project_id,
        })

    return results


def _read_file_samples(raw_path: str, max_files: int = 10, max_chars: int = 2000) -> List[dict]:
    """Read markdown files from raw_path and return samples."""
    import os
    import glob
    files = []
    pattern = os.path.join(raw_path, "**/*.md")
    for filepath in glob.glob(pattern, recursive=True)[:max_files]:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read(max_chars)
            files.append({
                "filename": os.path.basename(filepath),
                "content": content,
            })
        except Exception:
            continue
    return files


def _build_generate_prompt(samples: List[dict], project_name: str) -> str:
    files_text = "\n\n".join(
        f"--- FILE: {s['filename']} ---\n{s['content'][:500]}"
        for s in samples
    )
    prompt = f"""Given this raw markdown note from project "{project_name}", generate 1-2 concise quiz questions with multiple-choice answers.

RULES:
- Output ONLY a raw JSON array. No markdown code fences. No explanation. No reasoning text.
- The response must start with [ and end with ].
- Do NOT write anything before or after the JSON.

Format:
[
  {{
    "question": "Question?",
    "context": "Why this matters, referencing the source file.",
    "query_type": "yes_no",
    "choices": [
      {{"id": "c1", "label": "Yes", "description": "..."}},
      {{"id": "c2", "label": "No", "description": "..."}}
    ],
    "priority_score": 0.85,
    "raw_file_refs": ["filename.md"]
  }}
]

Raw files:
{files_text}"""
    return prompt


def generate_queries_for_project(db: Session, project_id: int) -> int:
    """Generate queries from raw files using LLM. One file per call to avoid token limits."""
    from app.llm_client import chat_completion, extract_json
    project = db.get(Project, project_id)
    if not project:
        return 0
    if not project.raw_path or not os.path.exists(project.raw_path):
        return 0

    samples = _read_file_samples(project.raw_path, max_files=5, max_chars=600)
    if not samples:
        return 0

    all_queries: List[dict] = []
    for sample in samples:
        prompt = _build_generate_prompt([sample], project.name)
        try:
            response = chat_completion(prompt, max_tokens=2000)
            queries = extract_json(response)
            if queries:
                all_queries.extend(queries)
        except Exception:
            continue

    if not all_queries:
        return 0

    created = 0
    for q_data in all_queries:
        try:
            choices = q_data.get("choices", [])
            choices_json = json.dumps(choices) if choices else None
            raw_refs = q_data.get("raw_file_refs", [])
            raw_refs_json = json.dumps(raw_refs) if raw_refs else None
            db_query = Query(
                project_id=project_id,
                question=q_data["question"],
                context=q_data.get("context", ""),
                query_type=q_data.get("query_type", "single_select"),
                choices_json=choices_json,
                priority_score=q_data.get("priority_score", 0.5),
                status="pending",
                llm_generated=True,
                raw_file_refs_json=raw_refs_json,
            )
            db.add(db_query)
            created += 1
        except Exception:
            continue

    if created > 0:
        db.commit()
    return created


def export_project(db: Session, project_id: int, fmt: str) -> dict:
    """Export project data as markdown or json."""
    project = db.get(Project, project_id)
    if not project:
        return None

    queries = db.exec(
        select(Query).where(Query.project_id == project_id)
    ).all()

    query_data = []
    for q in queries:
        answers = db.exec(select(Answer).where(Answer.query_id == q.id)).all()
        choices = json.loads(q.choices_json) if q.choices_json else []
        answer_texts = []
        for ans in answers:
            selected_ids = json.loads(ans.selected_choice_ids_json)
            selected_labels = [c["label"] for c in choices if c["id"] in selected_ids]
            answer_texts.extend(selected_labels)

        query_data.append({
            "id": q.id,
            "question": q.question,
            "context": q.context,
            "type": q.query_type,
            "choices": choices,
            "priority_score": q.priority_score,
            "status": q.status,
            "answers": answer_texts,
            "sources": json.loads(q.raw_file_refs_json) if q.raw_file_refs_json else [],
            "created_at": q.created_at.isoformat(),
        })

    safe_name = project.name.replace(" ", "_").lower()

    if fmt == "json":
        content = json.dumps({
            "project": {
                "id": project.id,
                "name": project.name,
                "created_at": project.created_at.isoformat(),
            },
            "queries": query_data,
        }, ensure_ascii=False, indent=2)
        filename = f"{safe_name}_export.json"
    else:
        # Markdown
        lines = [f"# {project.name} Wiki", ""]
        lines.append(f"*Exported on {project.updated_at.isoformat()}*")
        lines.append(f"*{len(query_data)} queries*")
        lines.append("")

        answered = [q for q in query_data if q["status"] == "answered"]
        pending = [q for q in query_data if q["status"] == "pending"]

        if answered:
            lines.append("## Answered Queries")
            lines.append("")
            for q in answered:
                lines.append(f"### {q['question']}")
                lines.append("")
                if q["context"]:
                    lines.append(f"**Context:** {q['context']}")
                    lines.append("")
                lines.append(f"**Answer:** {', '.join(q['answers']) if q['answers'] else 'No answer'}")
                lines.append("")
                if q["sources"]:
                    lines.append(f"*Sources:* {', '.join(q['sources'])}")
                    lines.append("")
                lines.append("---")
                lines.append("")

        if pending:
            lines.append("## Pending Queries")
            lines.append("")
            for q in pending:
                lines.append(f"- {q['question']}")
            lines.append("")

        content = "\n".join(lines)
        filename = f"{safe_name}_export.md"

    return {
        "format": fmt,
        "filename": filename,
        "content": content,
    }
