from lightgbm import LGBMClassifier

from src.utils.logger import logger


class CreditRiskLightGBM:

    def __init__(self):

        self.model = LGBMClassifier(
            n_estimators=500,
            learning_rate=0.03,
            max_depth=7,
            num_leaves=31,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="binary",
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        )

    def train(self, X_train, y_train):

        logger.info("Training LightGBM")

        self.model.fit(X_train, y_train)

        logger.info("LightGBM training completed")

    def predict(self, X):

        return self.model.predict(X)

    def predict_proba(self, X):

        return self.model.predict_proba(X)