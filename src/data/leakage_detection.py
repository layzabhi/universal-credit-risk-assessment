import pandas as pd
import numpy as np

from src.utils.logger import logger


def detect_high_target_correlation(
    df,
    target_col="TARGET",
    threshold=0.9
):

    logger.info("Checking for suspicious target correlations")

    numerical_df = df.select_dtypes(include=["int64", "float64"])

    correlations = numerical_df.corr()[target_col].sort_values(
        ascending=False
    )

    suspicious = correlations[
        (abs(correlations) > threshold) &
        (correlations.index != target_col)
    ]

    logger.info("Suspicious Features:")
    logger.info(suspicious)

    return suspicious


def detect_constant_features(df):

    logger.info("Checking constant features")

    constant_features = [
        col for col in df.columns
        if df[col].nunique() <= 1
    ]

    logger.info(f"Constant Features Count: {len(constant_features)}")

    logger.info(constant_features)

    return constant_features


def detect_high_missing_features(df, threshold=80):

    logger.info("Checking high missing features")

    missing_percent = (
        df.isnull().sum() / len(df) * 100
    )

    high_missing = missing_percent[
        missing_percent > threshold
    ].sort_values(ascending=False)

    logger.info("Highly Missing Features:")

    logger.info(high_missing)

    return high_missing


def detect_high_cardinality(df, threshold=100):

    logger.info("Checking high-cardinality categorical features")

    categorical_cols = df.select_dtypes(
        include=["object"]
    ).columns

    high_cardinality = {}

    for col in categorical_cols:

        unique_count = df[col].nunique()

        if unique_count > threshold:

            high_cardinality[col] = unique_count

    logger.info(high_cardinality)

    return high_cardinality