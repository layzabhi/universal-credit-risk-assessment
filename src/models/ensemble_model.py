from sklearn.ensemble import VotingClassifier

from sklearn.linear_model import LogisticRegression

from lightgbm import LGBMClassifier

from xgboost import XGBClassifier

from src.utils.logger import logger


class CreditRiskEnsemble:

    def __init__(self):

        xgb_model = XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="binary:logistic",
            eval_metric="auc",
            random_state=42,
            n_jobs=-1
        )

        lgbm_model = LGBMClassifier(
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

        lr_model = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        )

        self.model = VotingClassifier(
            estimators=[
                ("xgb", xgb_model),
                ("lgbm", lgbm_model),
                ("lr", lr_model)
            ],
            voting="soft",
            n_jobs=-1
        )

    def train(self, X_train, y_train):

        logger.info("Training Ensemble Model")

        self.model.fit(X_train, y_train)

        logger.info("Ensemble training completed")

    def predict(self, X):

        return self.model.predict(X)

    def predict_proba(self, X):

        return self.model.predict_proba(X)