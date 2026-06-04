import os
import sys
import pytest
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from backend.database import User, init_db, SessionLocal, engine
from backend.auth import get_password_hash, verify_password
from src.preprocessing.risk_signal_engine import RiskSignalEngine
from src.preprocessing.ingestion_engine import UniversalDatasetIngestionEngine


def test_auth_hashing():
    password = "test_password_123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_risk_signal_engine_scqs():
    # Test SCQS starting scores based on grade
    score_a = RiskSignalEngine.calculate_scqs(loan_grade='A')
    score_c = RiskSignalEngine.calculate_scqs(loan_grade='C')
    score_g = RiskSignalEngine.calculate_scqs(loan_grade='G')
    
    assert score_a > score_c
    assert score_c > score_g
    
    # Test interest rate penalty
    score_base = RiskSignalEngine.calculate_scqs(loan_grade='B', loan_int_rate=5.0)
    score_penalty = RiskSignalEngine.calculate_scqs(loan_grade='B', loan_int_rate=25.0)
    assert score_penalty < score_base
    
    # Test default history penalty
    score_no_defaults = RiskSignalEngine.calculate_scqs(loan_grade='B', default_history=0)
    score_defaults = RiskSignalEngine.calculate_scqs(loan_grade='B', default_history=4)
    assert score_defaults < score_no_defaults
    
    # Test bounds clamping (300 to 850)
    extreme_low = RiskSignalEngine.calculate_scqs(loan_grade='G', loan_int_rate=30.0, default_history=10)
    assert extreme_low >= 300.0
    
    extreme_high = RiskSignalEngine.calculate_scqs(loan_grade='A', loan_int_rate=3.0, credit_history='perfect')
    assert extreme_high <= 850.0


def test_ingestion_engine_normalization():
    # Construct a mock LendingClub dataframe row
    raw_data = {
        "loan_amnt": [25000.0],
        "int_rate": [12.5],
        "grade": ["B"],
        "emp_length": ["10+ years"],
        "annual_inc": [85000.0],
        "fico_range_low": [720.0],
        "fico_range_high": [750.0],
        "loan_status": ["Fully Paid"]
    }
    df = pd.DataFrame(raw_data)
    
    engine = UniversalDatasetIngestionEngine()
    df_norm, dataset_type, mapping = engine.ingest(df)
    
    assert dataset_type == "LendingClub"
    assert "income" in mapping
    assert df_norm["income"].iloc[0] == 85000.0
    assert df_norm["loan_amount"].iloc[0] == 25000.0
    assert df_norm["employment_years"].iloc[0] == 10.0
    assert df_norm["credit_score"].iloc[0] == 735.0 # Average of low & high FICO
    assert df_norm["target"].iloc[0] == 0 # Fully Paid mapped to 0


def test_database_init():
    # Make sure we can initialize tables and execute a query
    init_db()
    db = SessionLocal()
    try:
        # Check if users table is accessible
        num_users = db.query(User).count()
        assert isinstance(num_users, int)
    finally:
        db.close()


def test_admin_user_endpoint():
    init_db()
    db = SessionLocal()
    try:
        # Create a test admin user if not exists
        admin = db.query(User).filter(User.username == "test_admin_spec").first()
        if not admin:
            admin = User(username="test_admin_spec", hashed_password=get_password_hash("pw"), role="Admin")
            db.add(admin)
            db.commit()
            db.refresh(admin)
        
        assert admin.role == "Admin"
        users = db.query(User).all()
        assert len(users) >= 1
        assert any(u.username == "test_admin_spec" for u in users)
        
        # Clean up test user
        db.delete(admin)
        db.commit()
    finally:
        db.close()
