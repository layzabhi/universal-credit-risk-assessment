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

from src.models.logistic_regression_model import (
    CreditRiskLogisticModel
)

from src.evaluation.model_evaluation import (
    evaluate_model
)

df = load_data("application_train.csv")

X_train, X_test, y_train, y_test = split_data(df)

preprocessor = AdvancedCreditPreprocessor()

preprocessor.build_pipeline(X_train)

X_resampled, y_resampled = preprocessor.fit_resample(
    X_train,
    y_train
)

X_test_processed = preprocessor.transform(X_test)

model = CreditRiskLogisticModel()

model.train(X_resampled, y_resampled)

metrics = evaluate_model(
    model.model,
    X_test_processed,
    y_test
)

print("\nMetrics:")
print(metrics)