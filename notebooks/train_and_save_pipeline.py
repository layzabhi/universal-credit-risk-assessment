import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.append(PROJECT_ROOT)

from src.data.data_loader import load_data

from src.feature_engineering.feature_engineering import (
    CreditRiskFeatureEngineer
)

from src.preprocessing.data_splitter import split_data

from src.preprocessing.advanced_preprocessor import (
    AdvancedCreditPreprocessor
)

from src.models.lightgbm_model import (
    CreditRiskLightGBM
)

from src.utils.model_serializer import (
    ModelSerializer
)

df = load_data("application_train.csv")

# =========================
# Feature Engineering
# =========================

engineer = CreditRiskFeatureEngineer()

df = engineer.transform(df)

# =========================
# Train/Test Split
# =========================

X_train, X_test, y_train, y_test = split_data(df)

# =========================
# Preprocessing
# =========================

preprocessor = AdvancedCreditPreprocessor()

preprocessor.build_pipeline(X_train)

X_resampled, y_resampled = (
    preprocessor.fit_resample(
        X_train,
        y_train
    )
)

# =========================
# Model Training
# =========================

model = CreditRiskLightGBM()

model.train(
    X_resampled,
    y_resampled
)

# =========================
# Save Artifacts
# =========================

serializer = ModelSerializer()

serializer.save_object(
    model.model,
    "lightgbm_model.pkl"
)

serializer.save_object(
    preprocessor,
    "preprocessor.pkl"
)

feature_names = (
    preprocessor.get_feature_names()
)

serializer.save_object(
    feature_names,
    "feature_names.pkl"
)

print(
    "\nTraining and serialization completed"
)