import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from src.data.data_loader import load_data
from src.data.eda import (
    target_distribution,
    missing_value_analysis,
    correlation_analysis
)
from src.data.eda import target_balance_analysis

df = load_data("application_train.csv")

target_distribution(df)

missing_value_analysis(df)

correlation_analysis(df)

target_balance_analysis(df)

print("EDA completed successfully")