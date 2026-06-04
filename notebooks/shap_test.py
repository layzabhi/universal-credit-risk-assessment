import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.append(PROJECT_ROOT)

from src.data.data_loader import load_data

from src.feature_engineering.feature_engineering import (
    CreditRiskFeatureEngineer
)

from src.preprocessing.data_splitter import split_data

from src.preprocessing.advanced_preprocessor import (
    AdvancedCreditPreprocessor
)

from src.models.lightgbm_model import (
    CreditRiskLightGBM
)

from src.explainability.shap_explainer import (
    CreditRiskSHAPExplainer
)

df = load_data("application_train.csv")

engineer = CreditRiskFeatureEngineer()

df = engineer.transform(df)

X_train, X_test, y_train, y_test = split_data(df)

preprocessor = AdvancedCreditPreprocessor()

preprocessor.build_pipeline(X_train)

X_resampled, y_resampled = preprocessor.fit_resample(
    X_train,
    y_train
)

X_test_processed = preprocessor.transform(X_test)

feature_names = preprocessor.get_feature_names()

model = CreditRiskLightGBM()

model.train(X_resampled, y_resampled)

X_sample = X_test_processed[:1000]

explainer = CreditRiskSHAPExplainer(
    model.model,
    feature_names
)

explainer.create_explainer()

explainer.generate_summary_plot(
    X_sample
)

explainer.generate_waterfall_plot(
    X_sample,
    sample_index=0
)

risk_factors = (
    explainer.extract_top_risk_factors(
        X_sample,
        sample_index=0
    )
)

print("\nRisk Factors:\n")

print(risk_factors)

print("SHAP analysis completed")