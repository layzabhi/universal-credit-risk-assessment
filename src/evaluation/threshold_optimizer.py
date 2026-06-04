import numpy as np
import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score
)

from src.utils.logger import logger


def optimize_threshold(model, X_test, y_test):

    logger.info("Optimizing classification threshold")

    probabilities = model.predict_proba(X_test)[:, 1]

    thresholds = np.arange(0.1, 0.9, 0.05)

    results = []

    for threshold in thresholds:

        predictions = (
            probabilities >= threshold
        ).astype(int)

        precision = precision_score(
            y_test,
            predictions
        )

        recall = recall_score(
            y_test,
            predictions
        )

        f1 = f1_score(
            y_test,
            predictions
        )

        results.append({
            "threshold": threshold,
            "precision": precision,
            "recall": recall,
            "f1": f1
        })

    results_df = pd.DataFrame(results)

    best_row = results_df.loc[
        results_df["f1"].idxmax()
    ]

    logger.info("Best Threshold Found")

    logger.info(best_row)

    return results_df, best_row