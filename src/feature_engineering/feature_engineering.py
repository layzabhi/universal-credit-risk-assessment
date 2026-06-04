import numpy as np

from src.utils.logger import logger


class CreditRiskFeatureEngineer:

    def __init__(self):

        pass

    def transform(self, df):

        logger.info("Starting feature engineering")

        # =========================
        # Financial Ratios
        # =========================

        df["CREDIT_INCOME_RATIO"] = (
            df["AMT_CREDIT"] /
            (df["AMT_INCOME_TOTAL"] + 1)
        )

        df["ANNUITY_INCOME_RATIO"] = (
            df["AMT_ANNUITY"] /
            (df["AMT_INCOME_TOTAL"] + 1)
        )

        df["CREDIT_GOODS_RATIO"] = (
            df["AMT_CREDIT"] /
            (df["AMT_GOODS_PRICE"] + 1)
        )

        # =========================
        # Employment Stability
        # =========================

        df["EMPLOYMENT_AGE_RATIO"] = (
            df["DAYS_EMPLOYED"] /
            (df["DAYS_BIRTH"] + 1)
        )

        # =========================
        # Family Burden
        # =========================

        df["INCOME_PER_PERSON"] = (
            df["AMT_INCOME_TOTAL"] /
            (df["CNT_FAM_MEMBERS"] + 1)
        )

        # =========================
        # EXT_SOURCE Aggregations
        # =========================

        ext_sources = [
            "EXT_SOURCE_1",
            "EXT_SOURCE_2",
            "EXT_SOURCE_3"
        ]

        df["EXT_SOURCE_MEAN"] = (
            df[ext_sources].mean(axis=1)
        )

        df["EXT_SOURCE_MAX"] = (
            df[ext_sources].max(axis=1)
        )

        df["EXT_SOURCE_MIN"] = (
            df[ext_sources].min(axis=1)
        )

        # =========================
        # Document Flags
        # =========================

        doc_flags = [
            col for col in df.columns
            if "FLAG_DOCUMENT" in col
        ]

        df["TOTAL_DOC_FLAGS"] = (
            df[doc_flags].sum(axis=1)
        )

        logger.info("Feature engineering completed")

        return df