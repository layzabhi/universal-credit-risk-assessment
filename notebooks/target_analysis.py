import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.append(PROJECT_ROOT)

from src.data.data_loader import load_data

df = load_data("application_train.csv")

target_counts = df["TARGET"].value_counts()

target_percentage = (
    df["TARGET"].value_counts(normalize=True) * 100
)

print("\nTARGET COUNTS:")
print(target_counts)

print("\nTARGET PERCENTAGE:")
print(target_percentage)