import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.append(PROJECT_ROOT)

from src.data.data_loader import load_data

from src.preprocessing.data_splitter import split_data

from src.preprocessing.preprocessor import (
    CreditRiskPreprocessor
)

df = load_data("application_train.csv")

X_train, X_test, y_train, y_test = split_data(df)

print("Train Shape:", X_train.shape)
print("Test Shape:", X_test.shape)

preprocessor = CreditRiskPreprocessor()

preprocessor.fit(X_train)

X_train_processed = preprocessor.transform(X_train)

X_test_processed = preprocessor.transform(X_test)

print("Processed Train Shape:", X_train_processed.shape)
print("Processed Test Shape:", X_test_processed.shape)

print("Preprocessing completed successfully")