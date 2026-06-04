import os
import joblib

from src.utils.logger import logger


class ModelSerializer:

    def __init__(self, model_dir="models"):

        self.model_dir = model_dir

        os.makedirs(
            self.model_dir,
            exist_ok=True
        )

    def save_object(
        self,
        obj,
        filename
    ):

        path = os.path.join(
            self.model_dir,
            filename
        )

        joblib.dump(obj, path)

        logger.info(
            f"Saved object: {path}"
        )

    def load_object(
        self,
        filename
    ):

        path = os.path.join(
            self.model_dir,
            filename
        )

        logger.info(
            f"Loading object: {path}"
        )

        return joblib.load(path)