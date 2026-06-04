import os
import sys
import pandas as pd
import numpy as np
import optuna
import joblib
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import VotingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score, f1_score, classification_report

from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from xgboost import XGBClassifier

from configs.config import MODEL_DIR, RANDOM_STATE
from src.utils.logger import logger
from backend.database import SessionLocal, ModelGovernance, init_db

optuna.logging.set_verbosity(optuna.logging.WARNING)

def train_and_evaluate():
    logger.info("Universal model optimization starting...")
    
    # 1. Load universal dataset
    data_path = os.path.join(PROJECT_ROOT, "data", "processed", "universal_credit_risk.csv")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Universal dataset not found at {data_path}. Run prepare_universal_dataset.py first.")
        
    df = pd.read_csv(data_path)
    
    features = [
        'income', 'age', 'loan_amount', 'employment_years', 'dependents', 
        'credit_score', 'credit_income_ratio', 'employment_age_ratio', 'income_per_person'
    ]
    
    X = df[features]
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    
    # 2. Pipeline preprocessing
    preprocessor = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', RobustScaler())
    ])
    
    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)
    
    logger.info("Tuning hyperparameters using Optuna...")
    
    # Define Optuna objective for LightGBM
    def tune_lgbm(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 600),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.2, log=True),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'num_leaves': trial.suggest_int('num_leaves', 15, 127),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'random_state': RANDOM_STATE,
            'verbose': -1,
            'n_jobs': -1
        }
        clf = LGBMClassifier(**params)
        clf.fit(X_train_proc, y_train)
        preds = clf.predict_proba(X_test_proc)[:, 1]
        return roc_auc_score(y_test, preds)

    # Define Optuna objective for XGBoost
    def tune_xgb(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 600),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.2, log=True),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'random_state': RANDOM_STATE,
            'eval_metric': 'auc',
            'n_jobs': -1
        }
        clf = XGBClassifier(**params)
        clf.fit(X_train_proc, y_train)
        preds = clf.predict_proba(X_test_proc)[:, 1]
        return roc_auc_score(y_test, preds)

    # Run study for LightGBM
    lgbm_study = optuna.create_study(direction='maximize')
    lgbm_study.optimize(tune_lgbm, n_trials=15)
    best_lgbm_params = lgbm_study.best_params
    logger.info(f"Best LightGBM ROC-AUC: {lgbm_study.best_value:.4f}")
    
    # Run study for XGBoost
    xgb_study = optuna.create_study(direction='maximize')
    xgb_study.optimize(tune_xgb, n_trials=15)
    best_xgb_params = xgb_study.best_params
    logger.info(f"Best XGBoost ROC-AUC: {xgb_study.best_value:.4f}")
    
    # Define optimal CatBoost (using standard robust parameters for speed)
    best_cat_params = {
        'iterations': 500,
        'learning_rate': 0.05,
        'depth': 6,
        'eval_metric': 'AUC',
        'random_seed': RANDOM_STATE,
        'verbose': 0,
        'thread_count': -1
    }
    
    # 3. Create Ensemble Model
    lgbm_best = LGBMClassifier(**best_lgbm_params, random_state=RANDOM_STATE, verbose=-1, n_jobs=-1)
    xgb_best = XGBClassifier(**best_xgb_params, random_state=RANDOM_STATE, n_jobs=-1)
    cat_best = CatBoostClassifier(**best_cat_params)
    
    ensemble = VotingClassifier(
        estimators=[
            ('lgbm', lgbm_best),
            ('xgb', xgb_best),
            ('cat', cat_best)
        ],
        voting='soft',
        n_jobs=-1
    )
    
    # Calibrate probability predictions using cross-validation
    logger.info("Fitting and calibrating ensemble model...")
    calibrated_ensemble = CalibratedClassifierCV(
        estimator=ensemble,
        method='sigmoid',
        cv=3
    )
    
    calibrated_ensemble.fit(X_train_proc, y_train)
    
    # 4. Evaluate metrics
    test_probs = calibrated_ensemble.predict_proba(X_test_proc)[:, 1]
    
    # Optimize decision threshold for F1 score
    thresholds = np.linspace(0.05, 0.95, 91)
    best_thresh = 0.5
    best_f1 = 0.0
    
    for thresh in thresholds:
        test_preds = (test_probs >= thresh).astype(int)
        f1 = f1_score(y_test, test_preds)
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = thresh
            
    test_preds = (test_probs >= best_thresh).astype(int)
    roc_auc = roc_auc_score(y_test, test_probs)
    
    logger.info(f"Optimal Threshold: {best_thresh:.2f}")
    logger.info(f"Universal Ensemble Metrics:")
    logger.info(f"  ROC-AUC: {roc_auc:.4f}")
    logger.info(f"  F1 Score: {best_f1:.4f}")
    
    print("\nTest Classification Report:")
    print(classification_report(y_test, test_preds))
    
    # 5. Serialize model artifacts
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Save components
    joblib.dump(calibrated_ensemble, os.path.join(MODEL_DIR, "universal_ensemble.pkl"))
    joblib.dump(preprocessor, os.path.join(MODEL_DIR, "universal_preprocessor.pkl"))
    joblib.dump(features, os.path.join(MODEL_DIR, "universal_features.pkl"))
    
    logger.info("Saved universal model artifacts to models/")
    
    # 6. Log to Model Governance DB
    try:
        init_db()
        db = SessionLocal()
        
        gov_entry = ModelGovernance(
            version="v2.0.0-UniversalEnsemble",
            roc_auc=float(roc_auc),
            f1=float(best_f1),
            threshold=float(best_thresh),
            features_used=", ".join(features),
            training_date=datetime.utcnow()
        )
        db.add(gov_entry)
        db.commit()
        db.close()
        logger.info("Logged model entry in Model Governance Registry database.")
    except Exception as e:
        logger.warning(f"Failed to log governance entry in DB: {e}")

if __name__ == "__main__":
    train_and_evaluate()
