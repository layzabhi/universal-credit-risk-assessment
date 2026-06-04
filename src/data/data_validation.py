import pandas as pd
from src.utils.logger import logger

def validate_dataset(df):

    logger.info("Starting dataset validation")

    logger.info(f"Dataset Shape: {df.shape}")

    # Duplicate check
    duplicates = df.duplicated().sum()
    logger.info(f"Duplicate Rows: {duplicates}")

    # Missing values
    missing = df.isnull().sum().sort_values(ascending=False)

    logger.info("Top Missing Features:")
    logger.info(missing.head(10))

    # Data types
    logger.info("Data Types:")
    logger.info(df.dtypes.value_counts())

    logger.info("Validation completed")