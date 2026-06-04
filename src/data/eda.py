import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from configs.config import FIGURE_DIR
from src.utils.logger import logger

os.makedirs(FIGURE_DIR, exist_ok=True)

sns.set_style("darkgrid")


def target_distribution(df, target_col="TARGET"):

    logger.info("Generating target distribution plot")

    plt.figure(figsize=(8, 6))

    sns.countplot(x=df[target_col])

    plt.title("Target Distribution")

    save_path = os.path.join(FIGURE_DIR, "target_distribution.png")

    plt.savefig(save_path, bbox_inches="tight")

    plt.close()

    logger.info(f"Saved: {save_path}")


def missing_value_analysis(df):

    logger.info("Analyzing missing values")

    missing_percent = (
        df.isnull().sum() / len(df) * 100
    ).sort_values(ascending=False)

    missing_df = pd.DataFrame({
        "Feature": missing_percent.index,
        "Missing_Percentage": missing_percent.values
    })

    missing_df = missing_df[missing_df["Missing_Percentage"] > 0]

    plt.figure(figsize=(12, 8))

    sns.barplot(
        x="Missing_Percentage",
        y="Feature",
        data=missing_df.head(20)
    )

    plt.title("Top 20 Missing Features")

    save_path = os.path.join(FIGURE_DIR, "missing_values.png")

    plt.savefig(save_path, bbox_inches="tight")

    plt.close()

    logger.info(f"Saved: {save_path}")


def correlation_analysis(df):

    logger.info("Generating correlation heatmap")

    numerical_df = df.select_dtypes(include=["int64", "float64"])

    correlation_matrix = numerical_df.corr()

    plt.figure(figsize=(20, 16))

    sns.heatmap(
        correlation_matrix,
        cmap="coolwarm",
        center=0
    )

    plt.title("Correlation Heatmap")

    save_path = os.path.join(FIGURE_DIR, "correlation_heatmap.png")

    plt.savefig(save_path, bbox_inches="tight")

    plt.close()

    logger.info(f"Saved: {save_path}")


def target_balance_analysis(df, target_col="TARGET"):

    logger.info("Analyzing target balance")

    distribution = df[target_col].value_counts()

    percentage = (
        df[target_col].value_counts(normalize=True) * 100
    )

    logger.info("Target Counts:")
    logger.info(distribution)

    logger.info("Target Percentages:")
    logger.info(percentage)

    return distribution, percentage