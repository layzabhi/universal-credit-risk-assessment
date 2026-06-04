import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.append(PROJECT_ROOT)

from src.data.data_loader import load_data

from src.preprocessing.data_splitter import split_data

from src.preprocessing.advanced_preprocessor import (
    AdvancedCreditPreprocessor
)

from src.models.xgboost_model import (
    CreditRiskXGBoost
)

from src.evaluation.model_evaluation import (
    evaluate_model
)

from src.evaluation.threshold_optimizer import (
    optimize_threshold
)

from src.feature_engineering.feature_engineering import (
    CreditRiskFeatureEngineer
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

model = CreditRiskXGBoost()

model.train(X_resampled, y_resampled)

metrics = evaluate_model(
    model.model,
    X_test_processed,
    y_test
)

print("\nInitial Metrics:")
print(metrics)

results_df, best_row = optimize_threshold(
    model.model,
    X_test_processed,
    y_test
)

print("\nBest Threshold:")
print(best_row)