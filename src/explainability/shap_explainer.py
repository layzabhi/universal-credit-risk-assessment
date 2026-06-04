import os
import joblib
import pandas as pd
import numpy as np
import shap
from configs.config import MODEL_DIR
from src.utils.logger import logger

class CreditRiskSHAPExplainer:
    def __init__(self):
        # Load artifacts
        logger.info("Initializing SHAP Explainer...")
        self.model_path = os.path.join(MODEL_DIR, "universal_ensemble.pkl")
        self.preprocessor_path = os.path.join(MODEL_DIR, "universal_preprocessor.pkl")
        self.features_path = os.path.join(MODEL_DIR, "universal_features.pkl")
        
        self.ensemble = joblib.load(self.model_path)
        self.preprocessor = joblib.load(self.preprocessor_path)
        self.features = joblib.load(self.features_path)
        
        # Extract base fitted LightGBM estimator from the CalibratedClassifierCV
        # cv=3, so we take the first fold's estimator
        calibrated_clf = self.ensemble.calibrated_classifiers_[0]
        voting_clf = calibrated_clf.estimator
        self.lgbm_model = voting_clf.named_estimators_['lgbm']
        
        # Initialize TreeExplainer on the LightGBM estimator
        self.explainer = shap.TreeExplainer(self.lgbm_model)

    def explain_instance(self, raw_data_dict: dict) -> dict:
        """
        Computes SHAP values for a single applicant.
        Args:
            raw_data_dict: dict containing applicant features
        Returns:
            explanation: dict with base_value, output_value, and feature_contributions
        """
        # Create a single row DataFrame
        df_row = pd.DataFrame([raw_data_dict])[self.features]
        
        # Preprocess
        proc_data = self.preprocessor.transform(df_row)
        
        # Compute SHAP values
        shap_values_raw = self.explainer.shap_values(proc_data)
        
        # Extract base value and SHAP values for class 1 (Defaulter)
        # Note: Depending on SHAP version, lgbm TreeExplainer might return list of length 2 or single array.
        if isinstance(shap_values_raw, list):
            # Class 1 is second element
            shap_vals = shap_values_raw[1][0]
            base_val = self.explainer.expected_value[1]
        elif len(shap_values_raw.shape) == 3:
            # Shape is (samples, features, classes)
            shap_vals = shap_values_raw[0, :, 1]
            base_val = self.explainer.expected_value[1]
        else:
            # Single array
            shap_vals = shap_values_raw[0]
            # Expected value is a scalar or array
            base_val = self.explainer.expected_value
            if isinstance(base_val, (list, np.ndarray)) and len(base_val) > 1:
                base_val = base_val[1]
                
        # Base value and shap values are in log-odds space for TreeExplainer
        # Convert to probability or leave as contribution points. Let's return contributions.
        contributions = []
        for feat_name, feat_val, shap_val in zip(self.features, df_row.iloc[0], shap_vals):
            contributions.append({
                "feature": feat_name,
                "value": float(feat_val),
                "shap_value": float(shap_val)
            })
            
        # Sort by impact
        contributions = sorted(contributions, key=lambda x: abs(x["shap_value"]), reverse=True)
        
        # Calculate log-odds prediction (base_value + sum(shap_values))
        log_odds_pred = base_val + sum(shap_vals)
        # Convert to probability
        output_prob = 1.0 / (1.0 + np.exp(-log_odds_pred))
        
        return {
            "base_value": float(base_val),
            "output_value_prob": float(output_prob),
            "contributions": contributions
        }