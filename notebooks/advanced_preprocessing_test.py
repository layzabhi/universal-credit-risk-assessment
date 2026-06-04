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

df = load_data("application_train.csv")

X_train, X_test, y_train, y_test = split_data(df)

print("Original Train Shape:", X_train.shape)
print("Original Target Distribution:")
print(y_train.value_counts())

preprocessor = AdvancedCreditPreprocessor()

preprocessor.build_pipeline(X_train)

X_resampled, y_resampled = preprocessor.fit_resample(
    X_train,
    y_train
)

print("\nResampled Train Shape:", X_resampled.shape)

print("\nResampled Target Distribution:")
print(y_resampled.value_counts())

print("\nAdvanced preprocessing completed successfully")