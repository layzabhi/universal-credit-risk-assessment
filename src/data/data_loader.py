import pandas as pd
from configs.config import RAW_DATA_DIR
import os

def load_data(filename):

    path = os.path.join(RAW_DATA_DIR, filename)

    df = pd.read_csv(path)

    return df