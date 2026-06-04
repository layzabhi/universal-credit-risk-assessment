import pandas as pd
import numpy as np
from src.schema_mapper import detect_dataset_type, detect_columns
from src.preprocessing.risk_signal_engine import RiskSignalEngine
from src.utils.logger import logger

class UniversalDatasetIngestionEngine:
    def __init__(self):
        self.risk_signal_engine = RiskSignalEngine()

    def ingest(self, df: pd.DataFrame) -> tuple:
        """
        Ingests any credit risk dataset.
        Returns:
            normalized_df: pd.DataFrame with standardized columns
            dataset_type: str (the identified dataset name)
            mapping: dict (the column name mapping used)
        """
        raw_df = df.copy()
        
        # 1. Detect dataset type
        dataset_type = detect_dataset_type(raw_df.columns)
        logger.info(f"Detected dataset type: {dataset_type}")
        
        # 2. Map columns
        mapping = detect_columns(raw_df.columns)
        logger.info(f"Column mapping detected: {mapping}")
        
        normalized_df = pd.DataFrame(index=raw_df.index)
        
        # --- 3. Process Income ---
        if "income" in mapping:
            income_col = mapping["income"]
            # Check if Give Me Some Credit monthly income is used
            if dataset_type == "Give Me Some Credit":
                normalized_df["income"] = pd.to_numeric(raw_df[income_col], errors='coerce') * 12.0
            else:
                normalized_df["income"] = pd.to_numeric(raw_df[income_col], errors='coerce')
        else:
            # German credit fallback or missing income
            if dataset_type == "German Credit" and "loan_amount" in mapping:
                # Approximate income as 2x credit amount divided by duration in years if available
                normalized_df["income"] = pd.to_numeric(raw_df[mapping["loan_amount"]], errors='coerce') * 0.5
            else:
                normalized_df["income"] = np.nan
        
        # --- 4. Process Age ---
        if "age" in mapping:
            age_col = mapping["age"]
            age_val = pd.to_numeric(raw_df[age_col], errors='coerce')
            # Check if Home Credit negative days is used
            if age_val.mean() < 0:
                normalized_df["age"] = np.abs(age_val) / 365.0
            else:
                normalized_df["age"] = age_val
        else:
            normalized_df["age"] = np.nan

        # --- 5. Process Loan Amount ---
        if "loan_amount" in mapping:
            loan_col = mapping["loan_amount"]
            normalized_df["loan_amount"] = pd.to_numeric(raw_df[loan_col], errors='coerce')
        else:
            normalized_df["loan_amount"] = np.nan

        # --- 6. Process Employment Duration (in Years) ---
        if "employment" in mapping:
            emp_col = mapping["employment"]
            
            # Helper to parse string values (LendingClub style "10+ years")
            def parse_emp_len(val):
                if pd.isna(val):
                    return np.nan
                val_str = str(val).strip().lower()
                if "10+" in val_str:
                    return 10.0
                if "< 1" in val_str or "<1" in val_str:
                    return 0.5
                # Extract digits
                digits = re.findall(r'\d+', val_str)
                if digits:
                    return float(digits[0])
                return np.nan
                
            import re
            
            # Check if columns are numeric or strings
            if raw_df[emp_col].dtype == object:
                normalized_df["employment_years"] = raw_df[emp_col].apply(parse_emp_len)
            else:
                emp_val = pd.to_numeric(raw_df[emp_col], errors='coerce')
                # If negative, like DAYS_EMPLOYED in Home Credit
                if emp_val.mean() < 0:
                    normalized_df["employment_years"] = np.abs(emp_val) / 365.0
                else:
                    normalized_df["employment_years"] = emp_val
        else:
            normalized_df["employment_years"] = np.nan

        # --- 7. Process Dependents ---
        if "family_members" in mapping:
            dep_col = mapping["family_members"]
            normalized_df["dependents"] = pd.to_numeric(raw_df[dep_col], errors='coerce').fillna(0).astype(int)
        else:
            normalized_df["dependents"] = 0

        # --- 8. Process Credit Score (FICO scale 300 to 850) ---
        has_score = False
        if "credit_score" in mapping:
            score_col = mapping["credit_score"]
            score_series = pd.to_numeric(raw_df[score_col], errors='coerce')
            
            # If Home Credit EXT_SOURCE (range 0 to 1) is detected
            if score_series.max() <= 1.0:
                # Average multiple EXT_SOURCE if available
                ext_cols = [mapping[c] for c in ["credit_score"] if c in mapping]
                # Check for other EXT_SOURCE columns in raw_df
                other_exts = [c for c in raw_df.columns if "ext_source" in c.lower()]
                if len(other_exts) > 1:
                    ext_mean = raw_df[other_exts].mean(axis=1)
                else:
                    ext_mean = score_series
                normalized_df["credit_score"] = 300.0 + ext_mean * 550.0
                has_score = True
            # If FICO range (like LendingClub)
            elif "fico_range_low" in raw_df.columns and "fico_range_high" in raw_df.columns:
                normalized_df["credit_score"] = (raw_df["fico_range_low"] + raw_df["fico_range_high"]) / 2.0
                has_score = True
            else:
                # Direct FICO score or custom credit score
                normalized_df["credit_score"] = score_series
                has_score = True
                
        # If credit score doesn't exist, use RiskSignalEngine (SCQS)
        if not has_score or normalized_df["credit_score"].isna().sum() > len(df) * 0.5:
            logger.info("Credit score not found or mostly empty. Running Risk Signal Engine to compute SCQS.")
            normalized_df["credit_score"] = self.risk_signal_engine.generate_synthetic_scores(raw_df, mapping)
        
        # --- 9. Process Target Variable (Default) ---
        if "target" in mapping:
            target_col = mapping["target"]
            target_series = raw_df[target_col]
            
            if dataset_type == "LendingClub":
                # Charged Off / Default are 1, Fully Paid / Current are 0
                def LC_target_map(val):
                    val_str = str(val).strip().lower()
                    if any(x in val_str for x in ["charged off", "default", "late", "does not meet"]):
                        return 1
                    return 0
                normalized_df["target"] = target_series.apply(LC_target_map)
            elif dataset_type == "German Credit":
                # "bad" -> 1, "good" -> 0
                def GC_target_map(val):
                    val_str = str(val).strip().lower()
                    if "bad" in val_str or val == 2 or str(val) == "2":
                        return 1
                    return 0
                normalized_df["target"] = target_series.apply(GC_target_map)
            else:
                # Standard binary default mapping (0 or 1)
                normalized_df["target"] = pd.to_numeric(target_series, errors='coerce').fillna(0).astype(int)
        else:
            normalized_df["target"] = 0  # Default to 0 if not present (e.g., test/batch inputs)

        # --- 10. Missing Feature Imputation & Normalization ---
        # Apply median values to fill NaNs
        for col in ["income", "age", "loan_amount", "employment_years"]:
            median_val = normalized_df[col].median()
            if pd.isna(median_val):
                # Global defaults
                defaults = {"income": 60000.0, "age": 35.0, "loan_amount": 15000.0, "employment_years": 5.0}
                median_val = defaults[col]
            normalized_df[col] = normalized_df[col].fillna(median_val)
            
        # Standardize credit score
        normalized_df["credit_score"] = normalized_df["credit_score"].fillna(600.0)
        
        # --- 11. Add Engineered Features for Universal Model ---
        normalized_df["credit_income_ratio"] = normalized_df["loan_amount"] / (normalized_df["income"] + 1.0)
        normalized_df["employment_age_ratio"] = normalized_df["employment_years"] / (normalized_df["age"] + 1.0)
        normalized_df["income_per_person"] = normalized_df["income"] / (normalized_df["dependents"] + 1.0)
        
        return normalized_df, dataset_type, mapping
