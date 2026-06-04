import optuna

from xgboost import XGBClassifier

from sklearn.metrics import roc_auc_score

from src.utils.logger import logger


class XGBoostOptunaTuner:

    def __init__(self):

        self.best_model = None

        self.best_params = None

    def objective(
        self,
        trial,
        X_train,
        y_train,
        X_valid,
        y_valid
    ):

        params = {

            "n_estimators": trial.suggest_int(
                "n_estimators",
                100,
                500
            ),

            "max_depth": trial.suggest_int(
                "max_depth",
                3,
                10
            ),

            "learning_rate": trial.suggest_float(
                "learning_rate",
                0.01,
                0.3,
                log=True
            ),

            "subsample": trial.suggest_float(
                "subsample",
                0.6,
                1.0
            ),

            "colsample_bytree": trial.suggest_float(
                "colsample_bytree",
                0.6,
                1.0
            ),

            "min_child_weight": trial.suggest_int(
                "min_child_weight",
                1,
                10
            ),

            "gamma": trial.suggest_float(
                "gamma",
                0,
                5
            ),

            "objective": "binary:logistic",

            "eval_metric": "auc",

            "random_state": 42,

            "n_jobs": -1
        }

        model = XGBClassifier(**params)

        model.fit(X_train, y_train)

        predictions = model.predict_proba(
            X_valid
        )[:, 1]

        auc = roc_auc_score(
            y_valid,
            predictions
        )

        return auc

    def tune(
        self,
        X_train,
        y_train,
        X_valid,
        y_valid,
        n_trials=20
    ):

        logger.info("Starting Optuna optimization")

        study = optuna.create_study(
            direction="maximize"
        )

        study.optimize(
            lambda trial: self.objective(
                trial,
                X_train,
                y_train,
                X_valid,
                y_valid
            ),
            n_trials=n_trials
        )

        self.best_params = study.best_params

        logger.info("Best Parameters Found")

        logger.info(self.best_params)

        logger.info(
            f"Best ROC-AUC: {study.best_value}"
        )

        self.best_model = XGBClassifier(
            **self.best_params,
            objective="binary:logistic",
            eval_metric="auc",
            random_state=42,
            n_jobs=-1
        )

        self.best_model.fit(X_train, y_train)

        return self.best_model