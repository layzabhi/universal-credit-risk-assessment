from sklearn.compose import ColumnTransformer

from sklearn.pipeline import Pipeline

from sklearn.impute import SimpleImputer

from sklearn.preprocessing import (
    OneHotEncoder,
    RobustScaler
)

from imblearn.pipeline import Pipeline as ImbPipeline

from imblearn.over_sampling import SMOTE

from src.utils.logger import logger


class AdvancedCreditPreprocessor:

    def __init__(self):

        self.pipeline = None

    def build_pipeline(self, X):

        logger.info("Building advanced preprocessing pipeline")

        numerical_cols = X.select_dtypes(
            include=["int64", "float64"]
        ).columns

        categorical_cols = X.select_dtypes(
            include=["object"]
        ).columns

        numerical_pipeline = Pipeline([
            (
                "imputer",
                SimpleImputer(
                    strategy="median",
                    add_indicator=True
                )
            ),
            (
                "scaler",
                RobustScaler()
            )
        ])

        categorical_pipeline = Pipeline([
            (
                "imputer",
                SimpleImputer(
                    strategy="constant",
                    fill_value="Unknown"
                )
            ),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore"
                )
            )
        ])

        preprocessor = ColumnTransformer([
            (
                "num",
                numerical_pipeline,
                numerical_cols
            ),
            (
                "cat",
                categorical_pipeline,
                categorical_cols
            )
        ])

        self.pipeline = ImbPipeline([
            ("preprocessor", preprocessor),
            ("smote", SMOTE(random_state=42))
        ])

        logger.info("Pipeline built successfully")

    def fit_resample(self, X, y):

        logger.info("Running fit_resample")

        X_resampled, y_resampled = self.pipeline.fit_resample(X, y)

        logger.info("Resampling completed")

        return X_resampled, y_resampled

    def transform(self, X):

        logger.info("Transforming new data")

        return self.pipeline.named_steps[
            "preprocessor"
        ].transform(X)
    
    def get_feature_names(self):

        preprocessor = self.pipeline.named_steps[
            "preprocessor"
        ]

        feature_names = []

        # Numerical features
        num_features = preprocessor.transformers_[0][2]

        feature_names.extend(num_features)

        # Categorical features
        cat_pipeline = preprocessor.transformers_[1][1]

        encoder = cat_pipeline.named_steps["encoder"]

        cat_features = preprocessor.transformers_[1][2]

        encoded_names = encoder.get_feature_names_out(
            cat_features
        )

        feature_names.extend(encoded_names)

        return feature_names