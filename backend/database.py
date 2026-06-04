import os
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///credit_risk.db")

# For SQLite, we need to allow multithreading access
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="Risk Analyst")  # Admin, Risk Analyst, Manager

class Applicant(Base):
    __tablename__ = "applicants"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    income = Column(Float, nullable=False)
    loan_amount = Column(Float, nullable=False)
    credit_score = Column(Float, nullable=True)  # Can be None if SCQS is used
    default_probability = Column(Float, nullable=False)
    prediction = Column(String, nullable=False)
    dataset_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class PortfolioRun(Base):
    __tablename__ = "portfolio_runs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    dataset_type = Column(String, nullable=False)
    total_applicants = Column(Integer, nullable=False)
    approval_rate = Column(Float, nullable=False)
    average_risk = Column(Float, nullable=False)
    high_risk_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    applicants = relationship("PortfolioApplicant", back_populates="portfolio_run", cascade="all, delete-orphan")

class PortfolioApplicant(Base):
    __tablename__ = "portfolio_applicants"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_run_id = Column(Integer, ForeignKey("portfolio_runs.id"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=False)

    portfolio_run = relationship("PortfolioRun", back_populates="applicants")
    applicant = relationship("Applicant")

class ModelGovernance(Base):
    __tablename__ = "model_governance"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, nullable=False)
    roc_auc = Column(Float, nullable=False)
    f1 = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    features_used = Column(String, nullable=False)
    training_date = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
