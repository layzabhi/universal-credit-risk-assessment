import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.append(PROJECT_ROOT)

from src.data.data_loader import load_data

from src.data.leakage_detection import (
    detect_high_target_correlation,
    detect_constant_features,
    detect_high_missing_features,
    detect_high_cardinality
)

df = load_data("application_train.csv")

detect_high_target_correlation(df)

detect_constant_features(df)

detect_high_missing_features(df, threshold=50)

detect_high_cardinality(df)

print("Leakage diagnostics completed")