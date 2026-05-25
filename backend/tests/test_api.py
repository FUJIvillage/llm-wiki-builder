import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine
from app.main import app, get_session
from app.models import Project

engine = create_engine(
    "sqlite:///:memory:",
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def get_test_session():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = get_test_session
client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_project():
    response = client.post("/api/projects", json={"name": "Test Project"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["id"] is not None


def test_list_projects():
    # Create a project first
    client.post("/api/projects", json={"name": "List Project"})

    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    # Just verify at least one project exists (DB is shared across tests)
    assert any(p["name"] == "List Project" for p in data)


def test_create_and_list_queries():
    # Create project
    proj_resp = client.post("/api/projects", json={"name": "Query Test"})
    project_id = proj_resp.json()["id"]

    # Create query
    query_resp = client.post(
        f"/api/projects/{project_id}/queries",
        json={"question": "Is this a test?", "query_type": "yes_no"},
    )
    assert query_resp.status_code == 200
    query_data = query_resp.json()
    assert query_data["question"] == "Is this a test?"
    assert query_data["status"] == "pending"

    # List queries
    list_resp = client.get(f"/api/projects/{project_id}/queries")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


def test_answer_query():
    # Create project
    proj_resp = client.post("/api/projects", json={"name": "Answer Test"})
    project_id = proj_resp.json()["id"]

    # Create query
    query_resp = client.post(
        f"/api/projects/{project_id}/queries",
        json={
            "question": "Test question?",
            "query_type": "yes_no",
            "choices": [
                {"id": "c1", "label": "Yes"},
                {"id": "c2", "label": "No"},
            ],
        },
    )
    query_id = query_resp.json()["id"]

    # Submit answer
    answer_resp = client.post(
        f"/api/queries/{query_id}/answer",
        json={"selected_choice_ids": ["c1"]},
    )
    assert answer_resp.status_code == 200
    assert answer_resp.json()["selected_choice_ids"] == ["c1"]

    # Query should now be answered
    list_resp = client.get(f"/api/projects/{project_id}/queries")
    queries = list_resp.json()
    assert queries[0]["status"] == "answered"


def test_wiki_page():
    # Create project
    proj_resp = client.post("/api/projects", json={"name": "Wiki Test"})
    project_id = proj_resp.json()["id"]

    # Create query
    query_resp = client.post(
        f"/api/projects/{project_id}/queries",
        json={
            "question": "What is the meaning?",
            "query_type": "yes_no",
            "choices": [{"id": "c1", "label": "42"}],
        },
    )
    query_id = query_resp.json()["id"]

    # Answer query
    client.post(f"/api/queries/{query_id}/answer", json={"selected_choice_ids": ["c1"]})

    # Get wiki
    wiki_resp = client.get(f"/api/projects/{project_id}/wiki")
    assert wiki_resp.status_code == 200
    data = wiki_resp.json()
    assert data["title"] == "Wiki Test Wiki"
    assert "42" in data["content"]
    assert data["source_queries"] == 1


def test_search_queries():
    # Create project
    proj_resp = client.post("/api/projects", json={"name": "Searchable Project"})
    project_id = proj_resp.json()["id"]

    # Create queries
    client.post(
        f"/api/projects/{project_id}/queries",
        json={"question": "How to deploy to AWS?", "query_type": "yes_no"},
    )
    client.post(
        f"/api/projects/{project_id}/queries",
        json={"question": "Best practices for React", "query_type": "yes_no"},
    )

    # Search for "AWS"
    search_resp = client.get("/api/search?q=AWS")
    assert search_resp.status_code == 200
    data = search_resp.json()
    assert len(data["results"]) >= 1
    assert any("AWS" in r["title"] for r in data["results"])

    # Search for "React"
    search_resp = client.get("/api/search?q=React")
    assert search_resp.status_code == 200
    data = search_resp.json()
    assert any("React" in r["title"] for r in data["results"])

    # Search with no results
    search_resp = client.get("/api/search?q=xyznonexistent")
    assert search_resp.status_code == 200
    assert len(search_resp.json()["results"]) == 0


def test_export_markdown():
    # Create project
    proj_resp = client.post("/api/projects", json={"name": "Export Test"})
    project_id = proj_resp.json()["id"]

    # Create and answer a query
    query_resp = client.post(
        f"/api/projects/{project_id}/queries",
        json={
            "question": "What is the answer?",
            "query_type": "yes_no",
            "choices": [{"id": "c1", "label": "42"}],
        },
    )
    query_id = query_resp.json()["id"]
    client.post(f"/api/queries/{query_id}/answer", json={"selected_choice_ids": ["c1"]})

    # Export as markdown
    export_resp = client.get(f"/api/projects/{project_id}/export?format=markdown")
    assert export_resp.status_code == 200
    data = export_resp.json()
    assert data["format"] == "markdown"
    assert "# Export Test Wiki" in data["content"]
    assert "42" in data["content"]
    assert data["filename"].endswith(".md")


def test_export_json():
    # Create project
    proj_resp = client.post("/api/projects", json={"name": "JSON Export Test"})
    project_id = proj_resp.json()["id"]

    # Create query
    client.post(
        f"/api/projects/{project_id}/queries",
        json={"question": "Test?", "query_type": "yes_no"},
    )

    # Export as JSON
    export_resp = client.get(f"/api/projects/{project_id}/export?format=json")
    assert export_resp.status_code == 200
    data = export_resp.json()
    assert data["format"] == "json"
    assert "project" in data["content"]
    assert data["filename"].endswith(".json")
