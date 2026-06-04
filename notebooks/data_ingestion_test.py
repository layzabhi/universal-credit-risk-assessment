from src.data.data_loader import load_data
from src.data.data_validation import validate_dataset

df = load_data("application_train.csv")

print(df.head())

validate_dataset(df)