from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./ai_sentinel.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String, unique=True, index=True, nullable=False)
    email           = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role            = Column(String, default="developer")
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    id             = Column(Integer, primary_key=True, index=True)
    repo_url       = Column(String, nullable=True)
    repo_name      = Column(String, nullable=False)
    total_files    = Column(Integer, default=0)
    health_score   = Column(Float, default=0.0)
    critical_count = Column(Integer, default=0)
    high_count     = Column(Integer, default=0)
    moderate_count = Column(Integer, default=0)
    low_count      = Column(Integer, default=0)
    total_tdc      = Column(Float, default=0.0)
    run_by         = Column(String, nullable=True)
    created_at     = Column(DateTime, default=datetime.utcnow)


class FileResult(Base):
    __tablename__ = "file_results"
    id                    = Column(Integer, primary_key=True, index=True)
    run_id                = Column(Integer, nullable=False)
    filename              = Column(String, nullable=False)
    filepath              = Column(String, nullable=False)
    loc                   = Column(Integer, default=0)
    cyclomatic_complexity = Column(Float, default=0.0)
    halstead_effort       = Column(Float, default=0.0)
    maintainability_index = Column(Float, default=0.0)
    churn_rate            = Column(Float, default=0.0)
    risk_score            = Column(Float, default=0.0)
    risk_tier             = Column(String, default="Low")
    hotspot_score         = Column(Float, default=0.0)
    is_hotspot            = Column(Boolean, default=False)
    tdc_annual            = Column(Float, default=0.0)
    created_at            = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id         = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    user       = Column(String, nullable=True)
    detail     = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()