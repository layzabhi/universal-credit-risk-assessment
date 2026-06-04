import random
import numpy as np
import tensorflow as tf
import torch

def set_seed(seed=42):

    random.seed(seed)
    np.random.seed(seed)

    tf.random.set_seed(seed)

    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    print(f"Random seed set to: {seed}")