import os
import sys
import pandas as pd
import numpy as np
from io import StringIO, BytesIO
from datetime import datetime
from typing import List, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Depends,
    HTTPException,
    status
)
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import custom modules
from backend.database import init_db, get_db, User, Applicant, PortfolioRun, PortfolioApplicant, ModelGovernance
from backend.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    RoleChecker
)
from src.preprocessing.ingestion_engine import UniversalDatasetIngestionEngine
from src.utils.logger import logger
from src.explainability.shap_explainer import CreditRiskSHAPExplainer
from backend.pdf_generator import generate_underwriting_pdf
from src.utils.model_serializer import ModelSerializer

app = FastAPI(title="Universal Credit Risk AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()
    
    # Create default admin user if none exists
    db = next(get_db())
    admin_exists = db.query(User).filter(User.role == "Admin").first()
    if not admin_exists:
        hashed_pw = get_password_hash("admin123")
        admin_user = User(username="admin", hashed_password=hashed_pw, role="Admin")
        db.add(admin_user)
        
        # Also create a default analyst
        analyst_user = User(username="analyst", hashed_password=get_password_hash("analyst123"), role="Risk Analyst")
        db.add(analyst_user)
        
        # Add a dummy ModelGovernance log if database is empty
        gov_exists = db.query(ModelGovernance).first()
        if not gov_exists:
            gov = ModelGovernance(
                version="v2.0.0-UniversalEnsemble",
                roc_auc=0.8603,
                f1=0.6380,
                threshold=0.38,
                features_used="income, age, loan_amount, employment_years, dependents, credit_score, credit_income_ratio, employment_age_ratio, income_per_person",
                training_date=datetime.utcnow()
            )
            db.add(gov)
            
        db.commit()

# Load Artifacts
serializer = ModelSerializer()
model = serializer.load_object("universal_ensemble.pkl")
preprocessor = serializer.load_object("universal_preprocessor.pkl")
feature_names = serializer.load_object("universal_features.pkl")
ingestion_engine = UniversalDatasetIngestionEngine()

# Initialize SHAP explainer
shap_explainer = CreditRiskSHAPExplainer()

# =====================================================================
# Request Schemas
# =====================================================================
class UserCreate(BaseModel):
    username: str
    password: str
    role: str # Admin, Risk Analyst, Manager

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class SingleApplicantInput(BaseModel):
    full_name: str
    income: float
    age: float
    loan_amount: float
    employment_years: float
    dependents: int
    credit_score: Optional[float] = None
    loan_grade: Optional[str] = None
    loan_int_rate: Optional[float] = None
    credit_history: Optional[str] = None
    default_history: Optional[float] = None

# =====================================================================
# Auth Routes
# =====================================================================
@app.post("/api/auth/register", response_model=dict)
def register(
    user_data: UserCreate, 
    current_user: User = Depends(RoleChecker(["Admin"])),
    db: Session = Depends(get_db)
):
    # Only Admin can register new users in this enterprise platform
    # For quick testing, we will check role or bypass if no users exist
    user_exists = db.query(User).filter(User.username == user_data.username).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    hashed_pw = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_pw,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully", "username": user_data.username, "role": user_data.role}

@app.get("/api/admin/users", response_model=dict)
def get_registered_users(
    current_user: User = Depends(RoleChecker(["Admin"])),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    user_list = [{"id": u.id, "username": u.username, "role": u.role} for u in users]
    return {
        "total_users": len(user_list),
        "users": user_list
    }

@app.post("/api/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": user.role,
        "username": user.username
    }

# =====================================================================
# Predictive Risk & SHAP Route
# =====================================================================
@app.post("/api/predict")
def predict(data: SingleApplicantInput, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    # Ingest and normalize using the Ingestion Engine
    df_raw = pd.DataFrame([data.dict()])
    df_norm, dataset_type, mapping = ingestion_engine.ingest(df_raw)
    
    # Extract mapped variables to build model input
    input_features = df_norm[feature_names]
    
    # Process with model pipeline
    processed = preprocessor.transform(input_features)
    
    # Get calibrated prediction probability
    probability = float(model.predict_proba(processed)[:, 1][0])
    
    # Decided using governance threshold
    gov = db.query(ModelGovernance).order_by(ModelGovernance.training_date.desc()).first()
    threshold = gov.threshold if gov else 0.38
    prediction = "Defaulter" if probability >= threshold else "Non-Defaulter"
    
    # Save applicant record to database
    applicant = Applicant(
        full_name=data.full_name,
        age=int(df_norm["age"].iloc[0]),
        income=float(df_norm["income"].iloc[0]),
        loan_amount=float(df_norm["loan_amount"].iloc[0]),
        credit_score=float(df_norm["credit_score"].iloc[0]),
        default_probability=probability,
        prediction=prediction,
        dataset_type=dataset_type
    )
    db.add(applicant)
    db.commit()
    db.refresh(applicant)
    
    # Generate SHAP explanation
    explanation = shap_explainer.explain_instance(df_norm.iloc[0].to_dict())
    
    return {
        "id": applicant.id,
        "full_name": applicant.full_name,
        "prediction": prediction,
        "default_probability": probability,
        "credit_score": applicant.credit_score,
        "risk_level": "LOW" if probability < 0.25 else ("MEDIUM" if probability < 0.50 else "HIGH"),
        "explanation": explanation,
        "dataset_type": dataset_type
    }

@app.get("/api/explain/shap/{applicant_id}")
def get_shap_explanation(applicant_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
        
    # Re-run ingestion-style normalization on saved fields
    data_dict = {
        "income": applicant.income,
        "age": applicant.age,
        "loan_amount": applicant.loan_amount,
        "employment_years": 5.0, # default/imputed placeholder
        "dependents": 0,
        "credit_score": applicant.credit_score,
        "credit_income_ratio": applicant.loan_amount / (applicant.income + 1.0),
        "employment_age_ratio": 5.0 / (applicant.age + 1.0),
        "income_per_person": applicant.income
    }
    
    explanation = shap_explainer.explain_instance(data_dict)
    return explanation

# =====================================================================
# PDF Report Endpoint
# =====================================================================
@app.get("/api/applicants/{applicant_id}/report")
def get_pdf_report(applicant_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
        
    # Re-run ingestion-style normalization on saved fields to construct explanation
    data_dict = {
        "income": applicant.income,
        "age": applicant.age,
        "loan_amount": applicant.loan_amount,
        "employment_years": 5.0,
        "dependents": 0,
        "credit_score": applicant.credit_score,
        "credit_income_ratio": applicant.loan_amount / (applicant.income + 1.0),
        "employment_age_ratio": 5.0 / (applicant.age + 1.0),
        "income_per_person": applicant.income
    }
    
    explanation = shap_explainer.explain_instance(data_dict)
    
    # Format database object as dict for PDF generator
    applicant_data = {
        "id": applicant.id,
        "full_name": applicant.full_name,
        "age": applicant.age,
        "income": applicant.income,
        "loan_amount": applicant.loan_amount,
        "credit_score": applicant.credit_score,
        "default_probability": applicant.default_probability,
        "prediction": applicant.prediction,
        "dependents": 0,
        "employment_years": 5.0
    }
    
    pdf_buffer = generate_underwriting_pdf(applicant_data, explanation)
    
    filename = f"underwriting_report_{applicant.full_name.replace(' ', '_')}_{applicant.id}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# =====================================================================
# Batch Portfolio Routes
# =====================================================================
@app.post("/api/portfolio/predict")
async def upload_portfolio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
        
    try:
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode("utf-8")))
        
        # 1. Run ingestion
        df_norm, dataset_type, mapping = ingestion_engine.ingest(df)
        
        # 2. Preprocess and Predict
        input_features = df_norm[feature_names]
        processed = preprocessor.transform(input_features)
        probabilities = model.predict_proba(processed)[:, 1]
        
        # Fetch governance threshold
        gov = db.query(ModelGovernance).order_by(ModelGovernance.training_date.desc()).first()
        threshold = gov.threshold if gov else 0.38
        
        predictions = ["Defaulter" if p >= threshold else "Non-Defaulter" for p in probabilities]
        
        # 3. Create Applicants in DB (batch write to prevent locking)
        applicants = []
        for i in range(len(df_norm)):
            # Fallback name
            name = df.iloc[i].get("name") or df.iloc[i].get("full_name") or f"Applicant {i+1}"
            
            # Type casting with NaN protection
            age_val = df_norm["age"].iloc[i]
            age = int(round(float(age_val))) if not pd.isna(age_val) else 35
            
            income_val = df_norm["income"].iloc[i]
            income = float(income_val) if not pd.isna(income_val) else 60000.0
            
            loan_val = df_norm["loan_amount"].iloc[i]
            loan_amount = float(loan_val) if not pd.isna(loan_val) else 15000.0
            
            score_val = df_norm["credit_score"].iloc[i]
            credit_score = float(score_val) if not pd.isna(score_val) else 600.0
            
            applicant = Applicant(
                full_name=str(name),
                age=age,
                income=income,
                loan_amount=loan_amount,
                credit_score=credit_score,
                default_probability=float(probabilities[i]),
                prediction=predictions[i],
                dataset_type=dataset_type
            )
            db.add(applicant)
            applicants.append(applicant)
            
        db.commit()
        applicant_ids = [app.id for app in applicants]
            
        # 4. Create Portfolio Run
        total = len(probabilities)
        defaulters = sum(1 for p in predictions if p == "Defaulter")
        non_defaulters = total - defaulters
        avg_risk = float(np.mean(probabilities))
        high_risk_count = sum(1 for p in probabilities if p > 0.50)
        
        portfolio_run = PortfolioRun(
            filename=file.filename,
            dataset_type=dataset_type,
            total_applicants=total,
            approval_rate=float(non_defaulters / total) if total > 0 else 0.0,
            average_risk=avg_risk,
            high_risk_count=high_risk_count
        )
        db.add(portfolio_run)
        db.commit()
        db.refresh(portfolio_run)
        
        # 5. Link Applicants to Portfolio Run (batch write)
        for app_id in applicant_ids:
            link = PortfolioApplicant(
                portfolio_run_id=portfolio_run.id,
                applicant_id=app_id
            )
            db.add(link)
        db.commit()
        
        # 6. Prepare response results
        results_df = df.copy()
        results_df["default_probability"] = probabilities
        results_df["prediction"] = predictions
        
        # Add normalized columns so the frontend table can display them reliably
        results_df["age"] = df_norm["age"]
        results_df["income"] = df_norm["income"]
        results_df["loan_amount"] = df_norm["loan_amount"]
        results_df["credit_score"] = df_norm["credit_score"]
        
        # Replace NaN/NaT/NA values with None to ensure JSON serialization compatibility
        results_df = results_df.astype(object).where(pd.notnull(results_df), None)
        
        return {
            "id": portfolio_run.id,
            "filename": file.filename,
            "dataset_type": dataset_type,
            "total_applicants": total,
            "approval_rate": portfolio_run.approval_rate,
            "average_risk": round(avg_risk, 4),
            "high_risk_count": high_risk_count,
            "rejected": defaulters,
            "risk_distribution": {
                "high_risk": high_risk_count,
                "medium_risk": sum(1 for p in probabilities if 0.25 < p <= 0.50),
                "low_risk": sum(1 for p in probabilities if p <= 0.25)
            },
            "results": results_df.to_dict(orient="records")
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process portfolio CSV: {str(e)}")

@app.get("/api/portfolio/history")
def get_portfolio_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    runs = db.query(PortfolioRun).order_by(PortfolioRun.created_at.desc()).all()
    return [
        {
            "id": run.id,
            "filename": run.filename,
            "dataset_type": run.dataset_type,
            "total_applicants": run.total_applicants,
            "approval_rate": run.approval_rate,
            "average_risk": run.average_risk,
            "high_risk_count": run.high_risk_count,
            "created_at": run.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for run in runs
    ]

# =====================================================================
# Governance Dashboard Route
# =====================================================================
@app.get("/api/governance")
def get_governance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(ModelGovernance).order_by(ModelGovernance.training_date.desc()).all()
    return [
        {
            "id": log.id,
            "version": log.version,
            "roc_auc": log.roc_auc,
            "f1": log.f1,
            "threshold": log.threshold,
            "features_used": log.features_used,
            "training_date": log.training_date.strftime("%Y-%m-%d %H:%M:%S")
        }
        for log in logs
    ]

# =====================================================================
# Health Check Route
# =====================================================================
@app.get("/health")
def health():
    return {"status": "healthy", "time": str(datetime.now())}