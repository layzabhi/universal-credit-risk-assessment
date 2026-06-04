import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)

import pandas as pd
import numpy as np
import urllib.request
from configs.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.preprocessing.ingestion_engine import UniversalDatasetIngestionEngine
from src.utils.logger import logger

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

def generate_synthetic_lending_club(n_rows=8000):
    logger.info("Generating correlated synthetic LendingClub dataset...")
    np.random.seed(42)
    
    annual_inc = np.random.lognormal(11.0, 0.5, n_rows)
    loan_amnt = np.random.uniform(5000, 40000, n_rows)
    
    # Int rate depends on risk
    fico_range_low = np.random.uniform(600, 820, n_rows)
    # grade depends on fico
    grades = []
    int_rates = []
    for f in fico_range_low:
        if f > 780:
            grades.append('A')
            int_rates.append(np.random.uniform(5.0, 8.0))
        elif f > 720:
            grades.append('B')
            int_rates.append(np.random.uniform(8.0, 12.0))
        elif f > 670:
            grades.append('C')
            int_rates.append(np.random.uniform(12.0, 16.0))
        elif f > 630:
            grades.append('D')
            int_rates.append(np.random.uniform(16.0, 20.0))
        else:
            grades.append('E')
            int_rates.append(np.random.uniform(20.0, 26.0))
            
    int_rates = np.array(int_rates)
    emp_length = np.random.choice(['< 1 year', '1 year', '3 years', '5 years', '10+ years'], n_rows)
    emp_map = {'< 1 year': 0.5, '1 year': 1.0, '3 years': 3.0, '5 years': 5.0, '10+ years': 10.0}
    emp_years = np.array([emp_map[e] for e in emp_length])
    
    # Calculate default probability using logistic function
    # higher fico -> lower default; higher int_rate -> higher default; higher income -> lower default
    logit = 1.5 + (int_rates * 0.15) - ((fico_range_low - 600) * 0.02) - ((annual_inc / 50000.0) * 0.3) - (emp_years * 0.05)
    prob = 1.0 / (1.0 + np.exp(-logit))
    
    loan_status = []
    for p in prob:
        if np.random.rand() < p:
            loan_status.append(np.random.choice(['Charged Off', 'Late (31-120 days)']))
        else:
            loan_status.append(np.random.choice(['Fully Paid', 'Current']))
            
    data = {
        "loan_amnt": loan_amnt,
        "int_rate": int_rates,
        "grade": grades,
        "emp_length": emp_length,
        "annual_inc": annual_inc,
        "fico_range_low": fico_range_low,
        "fico_range_high": fico_range_low + 30.0,
        "loan_status": loan_status
    }
    return pd.DataFrame(data)

def generate_synthetic_german_credit(n_rows=2000):
    logger.info("Generating correlated synthetic German Credit dataset...")
    np.random.seed(42)
    
    duration = np.random.randint(6, 60, n_rows)
    credit_amount = np.random.uniform(500, 15000, n_rows)
    age = np.random.randint(19, 75, n_rows)
    credit_history = np.random.choice(['critical', 'delayed', 'all paid', 'existing paid'], n_rows)
    
    hist_map = {'critical': 2.0, 'delayed': 1.5, 'existing paid': 0.5, 'all paid': 0.0}
    hist_risk = np.array([hist_map[h] for h in credit_history])
    
    # logit calculation
    logit = -2.0 + (duration * 0.03) + (credit_amount / 5000.0) * 0.4 - (age * 0.025) + (hist_risk * 0.8)
    prob = 1.0 / (1.0 + np.exp(-logit))
    
    classes = [2 if np.random.rand() < p else 1 for p in prob] # 2 = bad, 1 = good
    
    data = {
        "duration": duration,
        "credit_amount": credit_amount,
        "checking_status": np.random.choice(['<0 DM', '0<=X<200 DM', '>=200 DM', 'no checking'], n_rows),
        "savings_status": np.random.choice(['<100 DM', '100<=X<500 DM', '>=1000 DM', 'unknown'], n_rows),
        "credit_history": credit_history,
        "personal_status": np.random.choice(['male single', 'female divorced', 'male married'], n_rows),
        "property_magnitude": np.random.choice(['real estate', 'life insurance', 'car', 'no property'], n_rows),
        "class": classes
    }
    return pd.DataFrame(data)

def generate_synthetic_give_me_some_credit(n_rows=8000):
    logger.info("Generating correlated synthetic Give Me Some Credit dataset...")
    np.random.seed(42)
    
    age = np.random.randint(21, 85, n_rows)
    MonthlyIncome = np.random.lognormal(8.5, 0.6, n_rows)
    RevolvingUtilizationOfUnsecuredLines = np.random.uniform(0.0, 1.2, n_rows)
    DebtRatio = np.random.uniform(0.0, 1.5, n_rows)
    NumberOfTime30_59DaysPastDue = np.random.choice([0, 1, 2, 3], n_rows, p=[0.85, 0.10, 0.03, 0.02])
    
    # logit
    logit = -3.0 + (RevolvingUtilizationOfUnsecuredLines * 2.0) + (DebtRatio * 0.6) - (age * 0.03) - (MonthlyIncome / 10000.0) * 0.4 + (NumberOfTime30_59DaysPastDue * 0.9)
    prob = 1.0 / (1.0 + np.exp(-logit))
    
    SeriousDlqin2yrs = [1 if np.random.rand() < p else 0 for p in prob]
    
    data = {
        "SeriousDlqin2yrs": SeriousDlqin2yrs,
        "RevolvingUtilizationOfUnsecuredLines": RevolvingUtilizationOfUnsecuredLines,
        "age": age,
        "NumberOfTime30-59DaysPastDueNotWorse": NumberOfTime30_59DaysPastDue,
        "DebtRatio": DebtRatio,
        "MonthlyIncome": MonthlyIncome,
        "NumberOfDependents": np.random.choice([0, 1, 2, 3, 4], n_rows, p=[0.55, 0.25, 0.12, 0.06, 0.02])
    }
    return pd.DataFrame(data)

def main():
    logger.info("Universal dataset preparation starting...")
    
    # 1. Load Home Credit sample
    home_credit_path = os.path.join(RAW_DATA_DIR, "application_train.csv")
    if not os.path.exists(home_credit_path):
        logger.error(f"Home credit raw data not found at {home_credit_path}!")
        # Fallback to generating synthetic Home Credit if missing entirely
        logger.info("Generating correlated synthetic Home Credit dataset since file is missing...")
        np.random.seed(42)
        n_rows = 20000
        income = np.random.lognormal(11.2, 0.5, n_rows)
        credit = np.random.uniform(10000, 100000, n_rows)
        age_days = -np.random.randint(20, 70, n_rows) * 365
        emp_days = -np.random.randint(1, 40, n_rows) * 365
        ext_1 = np.random.uniform(0.1, 0.9, n_rows)
        ext_2 = np.random.uniform(0.1, 0.9, n_rows)
        ext_3 = np.random.uniform(0.1, 0.9, n_rows)
        
        ext_mean = (ext_1 + ext_2 + ext_3) / 3.0
        # logit
        logit = 2.0 - (ext_mean * 5.0) + (credit / income) * 0.5 + (emp_days / age_days) * 0.2
        prob = 1.0 / (1.0 + np.exp(-logit))
        target = [1 if np.random.rand() < p else 0 for p in prob]
        
        hc_data = {
            "AMT_INCOME_TOTAL": income,
            "AMT_CREDIT": credit,
            "DAYS_BIRTH": age_days,
            "DAYS_EMPLOYED": emp_days,
            "CNT_FAM_MEMBERS": np.random.choice([1, 2, 3, 4, 5], n_rows, p=[0.3, 0.4, 0.15, 0.1, 0.05]),
            "EXT_SOURCE_1": ext_1,
            "EXT_SOURCE_2": ext_2,
            "EXT_SOURCE_3": ext_3,
            "TARGET": target
        }
        df_home_credit = pd.DataFrame(hc_data)
    else:
        logger.info(f"Loading sample from Home Credit dataset ({home_credit_path})...")
        # Load a larger sample of 30,000 rows to ensure robust modeling representation
        df_home_credit = pd.read_csv(home_credit_path, nrows=30000)

    # 2. German Credit
    df_german = generate_synthetic_german_credit()

    # 3. Lending Club
    df_lending_club = generate_synthetic_lending_club()

    # 4. Give Me Some Credit
    df_gms_credit = generate_synthetic_give_me_some_credit()

    # 5. Normalize all datasets using the ingestion engine
    engine = UniversalDatasetIngestionEngine()
    
    logger.info("Ingesting and normalizing datasets...")
    hc_norm, _, _ = engine.ingest(df_home_credit)
    german_norm, _, _ = engine.ingest(df_german)
    lc_norm, _, _ = engine.ingest(df_lending_club)
    gms_norm, _, _ = engine.ingest(df_gms_credit)
    
    # Tag datasets for records
    hc_norm["source_dataset"] = "Home Credit"
    german_norm["source_dataset"] = "German Credit"
    lc_norm["source_dataset"] = "LendingClub"
    gms_norm["source_dataset"] = "Give Me Some Credit"
    
    # 6. Concatenate
    logger.info("Concatenating into universal dataset...")
    universal_df = pd.concat([hc_norm, german_norm, lc_norm, gms_norm], axis=0, ignore_index=True)
    
    # Save output
    output_path = os.path.join(PROCESSED_DATA_DIR, "universal_credit_risk.csv")
    universal_df.to_csv(output_path, index=False)
    logger.info(f"Saved universal dataset to {output_path} (Total Rows: {len(universal_df)})")

if __name__ == "__main__":
    main()
