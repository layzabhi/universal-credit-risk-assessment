import pandas as pd
import numpy as np

class RiskSignalEngine:
    """
    RiskSignalEngine removes dependency on traditional credit scores by generating
    a Synthetic Credit Quality Score (SCQS) ranging from 300 to 850 based on alternative signals.
    """
    
    @staticmethod
    def calculate_scqs(
        loan_grade=None,
        loan_int_rate=None,
        credit_history=None,
        default_history=None,
        income=None,
        loan_amount=None
    ):
        # Base starting score
        score = 650.0
        
        # 1. Map Loan Grade if available
        if loan_grade is not None:
            grade_scores = {
                'A': 810.0, 'B': 730.0, 'C': 650.0, 'D': 570.0, 'E': 490.0, 'F': 410.0, 'G': 330.0
            }
            # Clean string and get first character
            grade_str = str(loan_grade).strip().upper()
            if grade_str in grade_scores:
                score = grade_scores[grade_str]
        
        # 2. Interest Rate Adjustments (higher rate -> higher risk -> lower score)
        if loan_int_rate is not None and not pd.isna(loan_int_rate):
            try:
                rate = float(loan_int_rate)
                # Deduct points for rates above 8%
                if rate > 8.0:
                    score -= (rate - 8.0) * 8.0
            except ValueError:
                pass
                
        # 3. Credit History Adjustments
        if credit_history is not None and not pd.isna(credit_history):
            history_str = str(credit_history).strip().lower()
            if any(x in history_str for x in ['critical', 'bad', 'delay', 'all paid delayed', 'no credit']):
                score -= 100.0
            elif any(x in history_str for x in ['good', 'all paid', 'existing paid', 'perfect']):
                score += 50.0
                
        # 4. Default History / Delinquency Adjustments
        if default_history is not None and not pd.isna(default_history):
            try:
                defaults = float(default_history)
                score -= min(defaults * 60.0, 300.0)  # Deduct up to 300 points for defaults
            except ValueError:
                pass
                
        # 5. Income-to-Loan Ratio minor adjustment if no grade was given
        if loan_grade is None and income is not None and loan_amount is not None:
            try:
                inc = float(income)
                lamnt = float(loan_amount)
                if inc > 0:
                    ratio = lamnt / inc
                    if ratio > 0.5:
                        score -= 50.0
                    elif ratio < 0.15:
                        score += 30.0
            except ValueError:
                pass

        # Clamp between 300 and 850
        return float(np.clip(score, 300.0, 850.0))

    def generate_synthetic_scores(self, df: pd.DataFrame, mapping: dict) -> pd.Series:
        """
        Calculates SCQS for a dataframe using mapped columns.
        """
        scores = []
        for _, row in df.iterrows():
            grade = row.get(mapping.get("loan_grade")) if "loan_grade" in mapping else None
            rate = row.get(mapping.get("loan_int_rate")) if "loan_int_rate" in mapping else None
            history = row.get(mapping.get("credit_history")) if "credit_history" in mapping else None
            defaults = row.get(mapping.get("default_history")) if "default_history" in mapping else None
            inc = row.get(mapping.get("income")) if "income" in mapping else None
            lamnt = row.get(mapping.get("loan_amount")) if "loan_amount" in mapping else None
            
            scqs = self.calculate_scqs(
                loan_grade=grade,
                loan_int_rate=rate,
                credit_history=history,
                default_history=defaults,
                income=inc,
                loan_amount=lamnt
            )
            scores.append(scqs)
            
        return pd.Series(scores, index=df.index)
