from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

SQLALCHEMY_DATABASE_URL = "sqlite:///./financial_analysis.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(String, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)
    filename = Column(String)
    query = Column(String)
    status = Column(String, default="pending")  # pending, completed, failed
    result = Column(Text, nullable=True)
    output_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_task(db, filename: str, query: str):
    task_id = str(uuid.uuid4())
    db_task = AnalysisResult(
        id=str(uuid.uuid4()),
        task_id=task_id,
        filename=filename,
        query=query,
        status="pending"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return task_id

def update_task_result(db, task_id: str, result: str, output_path: str, status: str = "completed"):
    db_task = db.query(AnalysisResult).filter(AnalysisResult.task_id == task_id).first()
    if db_task:
        db_task.result = result
        db_task.output_path = output_path
        db_task.status = status
        db_task.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(db_task)
