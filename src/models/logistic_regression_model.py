from sklearn.linear_model import LogisticRegression

from src.utils.logger import logger


class CreditRiskLogisticModel:

    def __init__(self):

        self.model = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        )

    def train(self, X_train, y_train):

        logger.info("Training Logistic Regression")

        self.model.fit(X_train, y_train)

        logger.info("Training completed")

    def predict(self, X):

        return self.model.predict(X)

    def predict_proba(self, X):

        return self.model.predict_proba(X)