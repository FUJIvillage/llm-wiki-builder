from sqlmodel import SQLModel, create_engine, Session

sqlite_url = "sqlite:///./wiki_builder.db"
engine = create_engine(sqlite_url, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
