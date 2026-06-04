import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import RobustScaler

from src.utils.logger import logger


class CreditRiskPreprocessor:

    def __init__(self):

        self.num_imputer = SimpleImputer(strategy="median")

        self.cat_imputer = SimpleImputer(
            strategy="constant",
            fill_value="Unknown"
        )

        self.scaler = RobustScaler()

        self.label_encoders = {}

        self.numerical_cols = None
        self.categorical_cols = None

    def fit(self, X):

        logger.info("Fitting preprocessing pipeline")

        self.numerical_cols = X.select_dtypes(
            include=["int64", "float64"]
        ).columns

        self.categorical_cols = X.select_dtypes(
            include=["object"]
        ).columns

        # Numerical
        self.num_imputer.fit(X[self.numerical_cols])

        # Categorical
        self.cat_imputer.fit(X[self.categorical_cols])

        X_cat = pd.DataFrame(
            self.cat_imputer.transform(X[self.categorical_cols]),
            columns=self.categorical_cols
        )

        for col in self.categorical_cols:

            le = LabelEncoder()

            X_cat[col] = le.fit_transform(X_cat[col])

            self.label_encoders[col] = le

        X_num = pd.DataFrame(
            self.num_imputer.transform(X[self.numerical_cols]),
            columns=self.numerical_cols
        )

        self.scaler.fit(X_num)

        logger.info("Preprocessor fitted successfully")

    def transform(self, X):

        logger.info("Transforming dataset")

        X_num = pd.DataFrame(
            self.num_imputer.transform(X[self.numerical_cols]),
            columns=self.numerical_cols
        )

        X_num = pd.DataFrame(
            self.scaler.transform(X_num),
            columns=self.numerical_cols
        )

        X_cat = pd.DataFrame(
            self.cat_imputer.transform(X[self.categorical_cols]),
            columns=self.categorical_cols
        )

        for col in self.categorical_cols:

            le = self.label_encoders[col]

            X_cat[col] = le.transform(X_cat[col])

        X_processed = pd.concat(
            [X_num, X_cat],
            axis=1
        )

        logger.info("Transformation completed")

        return X_processed