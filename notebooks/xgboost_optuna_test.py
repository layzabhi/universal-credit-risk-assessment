import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.append(PROJECT_ROOT)

from sklearn.model_selection import train_test_split

from src.data.data_loader import load_data

from src.feature_engineering.feature_engineering import (
    CreditRiskFeatureEngineer
)

from src.preprocessing.data_splitter import split_data

from src.preprocessing.advanced_preprocessor import (
    AdvancedCreditPreprocessor
)

from src.models.xgboost_optuna import (
    XGBoostOptunaTuner
)

from src.evaluation.model_evaluation import (
    evaluate_model
)

from src.evaluation.threshold_optimizer import (
    optimize_threshold
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

X_train_final, X_valid, y_train_final, y_valid = (
    train_test_split(
        X_resampled,
        y_resampled,
        test_size=0.2,
        random_state=42,
        stratify=y_resampled
    )
)

tuner = XGBoostOptunaTuner()

best_model = tuner.tune(
    X_train_final,
    y_train_final,
    X_valid,
    y_valid,
    n_trials=20
)

metrics = evaluate_model(
    best_model,
    X_test_processed,
    y_test
)

print("\nOptimized Metrics:")
print(metrics)

results_df, best_row = optimize_threshold(
    best_model,
    X_test_processed,
    y_test
)

print("\nBest Threshold:")
print(best_row)