import os

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    RocCurveDisplay
)

from configs.config import FIGURE_DIR

from src.utils.logger import logger


def evaluate_model(model, X_test, y_test):

    logger.info("Evaluating model")

    y_pred = model.predict(X_test)

    y_prob = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)

    precision = precision_score(y_test, y_pred)

    recall = recall_score(y_test, y_pred)

    f1 = f1_score(y_test, y_pred)

    roc_auc = roc_auc_score(y_test, y_prob)

    logger.info(f"Accuracy: {accuracy:.4f}")
    logger.info(f"Precision: {precision:.4f}")
    logger.info(f"Recall: {recall:.4f}")
    logger.info(f"F1 Score: {f1:.4f}")
    logger.info(f"ROC-AUC: {roc_auc:.4f}")

    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(6, 5))

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues"
    )

    plt.title("Confusion Matrix")

    save_path = os.path.join(
        FIGURE_DIR,
        "confusion_matrix.png"
    )

    plt.savefig(save_path, bbox_inches="tight")

    plt.close()

    logger.info(f"Saved: {save_path}")

    # ROC Curve
    RocCurveDisplay.from_predictions(y_test, y_prob)

    plt.title("ROC Curve")

    save_path = os.path.join(
        FIGURE_DIR,
        "roc_curve.png"
    )

    plt.savefig(save_path, bbox_inches="tight")

    plt.close()

    logger.info(f"Saved: {save_path}")

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc
    }