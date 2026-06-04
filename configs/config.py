import os

# =========================
# PROJECT PATHS
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

MODEL_DIR = os.path.join(BASE_DIR, "models")

REPORT_DIR = os.path.join(BASE_DIR, "reports")
FIGURE_DIR = os.path.join(REPORT_DIR, "figures")
METRIC_DIR = os.path.join(REPORT_DIR, "metrics")

LOG_DIR = os.path.join(BASE_DIR, "logs")

# =========================
# RANDOM SEED
# =========================

RANDOM_STATE = 42

# =========================
# TARGET VARIABLE
# =========================

TARGET_COLUMN = "default"

# =========================
# TEST SIZE
# =========================

TEST_SIZE = 0.2

# =========================
# VALIDATION SIZE
# =========================

VALIDATION_SIZE = 0.1