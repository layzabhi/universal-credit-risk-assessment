from src.utils.logger import logger
from src.utils.reproducibility import set_seed

def main():

    logger.info("Starting Credit Risk Enterprise System")

    set_seed(42)

    logger.info("System initialized successfully")

if __name__ == "__main__":
    main()