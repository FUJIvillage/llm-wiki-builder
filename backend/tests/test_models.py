import pytest
from sqlmodel import Session, SQLModel, create_engine
from app.models import Project, Query, Answer

# In-memory SQLite for tests
engine = create_engine("sqlite:///:memory:", echo=False)


@pytest.fixture
def session():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


def test_create_project(session: Session):
    project = Project(name="Test Project")
    session.add(project)
    session.commit()
    session.refresh(project)
    assert project.id is not None
    assert project.name == "Test Project"


def test_create_query_with_project(session: Session):
    project = Project(name="Test Project")
    session.add(project)
    session.commit()

    query = Query(
        project_id=project.id,
        question="Test question?",
        query_type="yes_no",
        priority_score=0.9,
    )
    session.add(query)
    session.commit()
    session.refresh(query)

    assert query.id is not None
    assert query.project_id == project.id
    assert query.status == "pending"


def test_create_answer_with_query(session: Session):
    project = Project(name="Test Project")
    session.add(project)
    session.commit()

    query = Query(
        project_id=project.id,
        question="Test question?",
        query_type="yes_no",
    )
    session.add(query)
    session.commit()

    answer = Answer(
        query_id=query.id,
        selected_choice_ids_json='["c1"]',
    )
    session.add(answer)
    session.commit()
    session.refresh(answer)

    assert answer.id is not None
    assert answer.query_id == query.id
    assert answer.selected_choice_ids_json == '["c1"]'


def test_project_query_relationship(session: Session):
    project = Project(name="Rel Project")
    session.add(project)
    session.commit()

    for i in range(3):
        query = Query(
            project_id=project.id,
            question=f"Question {i}?",
            query_type="yes_no",
        )
        session.add(query)
    session.commit()

    session.refresh(project)
    assert len(project.queries) == 3
