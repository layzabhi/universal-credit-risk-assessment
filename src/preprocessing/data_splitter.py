from sklearn.model_selection import train_test_split

from configs.config import (
    RANDOM_STATE,
    TEST_SIZE
)


def split_data(df, target_col="TARGET"):

    X = df.drop(columns=[target_col])

    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y
    )

    return X_train, X_test, y_train, y_test