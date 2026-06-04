from sklearn.ensemble import RandomForestClassifier

from src.utils.logger import logger


class CreditRiskRandomForest:

    def __init__(self):

        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=4,
            n_jobs=-1,
            class_weight="balanced",
            random_state=42
        )

    def train(self, X_train, y_train):

        logger.info("Training Random Forest")

        self.model.fit(X_train, y_train)

        logger.info("Random Forest training completed")

    def predict(self, X):

        return self.model.predict(X)

    def predict_proba(self, X):

        return self.model.predict_proba(X)