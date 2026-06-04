from xgboost import XGBClassifier

from src.utils.logger import logger


class CreditRiskXGBoost:

    def __init__(self):

        self.model = XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="binary:logistic",
            eval_metric="auc",
            scale_pos_weight=1,
            random_state=42,
            n_jobs=-1
        )

    def train(self, X_train, y_train):

        logger.info("Training XGBoost")

        self.model.fit(X_train, y_train)

        logger.info("XGBoost training completed")

    def predict(self, X):

        return self.model.predict(X)

    def predict_proba(self, X):

        return self.model.predict_proba(X)