import datetime
from typing import List
from sqlmodel import Field, SQLModel, create_engine, Session, JSON, select, desc

class DbSubmission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime.datetime = Field(nullable=False)
    png_bytes: bytes = Field(nullable=False)
    label: int = Field(nullable=False)
    predictions: List[dict] = Field(sa_type=JSON, nullable=False)

class InMemorySubmissionStore:
    def __init__(self):
        self.submissions = []

    def add_submission(self, submission: DbSubmission):
        self.submissions.append(submission)

    def get_recent_submissions(self, count) -> List[DbSubmission]:
        return self.submissions[-count:]


class PostgreSqlSubmissionStore:
    def __init__(self, database_url: str):
        engine = create_engine(database_url)
        SQLModel.metadata.create_all(engine)
        self.engine = engine

    def _get_session(self):
        with Session(self.engine) as session:
            yield session

    def add_submission(self, submission: DbSubmission):
        with Session(self.engine) as session:
            session.add(submission)
            session.commit()

    def get_recent_submissions(self, count) -> List[DbSubmission]:
        with Session(self.engine) as session:
            statement=select(DbSubmission).order_by(desc(DbSubmission.timestamp)).limit(count)
            return [x for x in session.exec(statement)]

def load_env_string(name: str) -> str:
    """Load string environment variable"""
    import os
    loaded = os.getenv(name)
    if loaded is None:
        raise ValueError(f"Environment variable {name} not set")
    return loaded

import os
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None or DATABASE_URL == "":
    submission_store = InMemorySubmissionStore()
else:
    submission_store = PostgreSqlSubmissionStore(database_url=load_env_string("DATABASE_URL"))