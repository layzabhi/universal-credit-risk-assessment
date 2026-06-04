import re

# Standard mapping dictionary for dataset detection and automatic mapping
DATASET_SIGNATURES = {
    "Home Credit": [
        "amt_income_total", "amt_credit", "days_birth", "days_employed", 
        "ext_source_1", "ext_source_2", "ext_source_3", "target"
    ],
    "LendingClub": [
        "loan_amnt", "int_rate", "grade", "emp_length", "annual_inc", 
        "loan_status", "fico_range_low", "fico_range_high"
    ],
    "German Credit": [
        "duration", "credit_amount", "checking_status", "credit_history", 
        "savings_status", "personal_status", "property_magnitude", "class"
    ],
    "Give Me Some Credit": [
        "seriousdlqin2yrs", "revolvingutilizationofunsecuredlines", 
        "numberoftime30-59dayspastduenotworse", "debtratio", "monthlyincome"
    ]
}

FIELD_MAPPING = {
    "income": [
        "income", "annual_income", "monthly_income", "person_income",
        "amt_income_total", "annual_inc", "monthlyincome", "income_annual"
    ],
    "age": [
        "age", "person_age", "customer_age", "days_birth", "dob"
    ],
    "loan_amount": [
        "loan_amount", "loan_amnt", "amt_credit", "credit_amount", 
        "loan_amount_requested", "credit_amt"
    ],
    "employment": [
        "days_employed", "employment_length", "months_employed", "job_tenure", 
        "emp_length", "employment_duration", "duration"
    ],
    "family_members": [
        "cnt_fam_members", "family_size", "dependents", "numberofdependents"
    ],
    "credit_score": [
        "credit_score", "fico", "fico_score", "score", "ext_source_1", 
        "ext_source_2", "ext_source_3", "fico_range_low", "fico_range_high"
    ],
    "loan_grade": [
        "loan_grade", "grade", "credit_grade"
    ],
    "loan_int_rate": [
        "loan_int_rate", "int_rate", "interest_rate", "rate"
    ],
    "credit_history": [
        "credit_history", "history", "checking_status", "savings_status"
    ],
    "default_history": [
        "default_history", "numberoftime30-59dayspastduenotworse", 
        "numberoftimes90dayslate", "numberoftime60-89dayspastduenotworse", 
        "delinq_2yrs", "pub_rec"
    ],
    "target": [
        "default", "target", "class", "seriousdlqin2yrs", "loan_status"
    ]
}

def normalize_column(col: str) -> str:
    return re.sub(r'[^a-z0-9]', '', str(col).lower())

def detect_dataset_type(columns: list) -> str:
    normalized_cols = {normalize_column(col) for col in columns}
    
    best_match = "Custom Dataset"
    max_overlap = 0
    
    for dataset_name, signatures in DATASET_SIGNATURES.items():
        overlap = sum(1 for sig in signatures if normalize_column(sig) in normalized_cols)
        if overlap > max_overlap and overlap >= 2:
            max_overlap = overlap
            best_match = dataset_name
            
    return best_match

def detect_columns(columns: list) -> dict:
    detected = {}
    normalized = {normalize_column(col): col for col in columns}
    
    for standard_field, aliases in FIELD_MAPPING.items():
        for alias in aliases:
            alias_norm = normalize_column(alias)
            # Exact match first
            if alias_norm in normalized:
                detected[standard_field] = normalized[alias_norm]
                break
            
            # Substring match if exact match not found
            matched = False
            for col_norm, original_col in normalized.items():
                if alias_norm in col_norm or col_norm in alias_norm:
                    detected[standard_field] = original_col
                    matched = True
                    break
            if matched:
                break
                
    return detected