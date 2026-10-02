"""Chronological evaluation with training-only preprocessing."""
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

FEATURES = ["SPX", "USO", "SLV", "EUR/USD"]


def chronological_split(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    usable = data.dropna(subset=["GLD"]).sort_values("Date")
    if usable.Date.duplicated().any():
        raise ValueError("Model observations must have unique dates.")
    n_train = int(np.floor(0.8 * len(usable)))
    if n_train < 10 or len(usable) - n_train < 2:
        raise ValueError("Insufficient observations: require at least 10 training and 2 test rows (at least 13 usable rows).")
    return usable.iloc[:n_train].copy(), usable.iloc[n_train:].copy()


def evaluate(actual, predicted) -> dict:
    actual = np.asarray(actual, dtype=float)
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": None if np.all(actual == actual[0]) else float(r2_score(actual, predicted)),
    }


def fit_and_evaluate(data: pd.DataFrame) -> tuple[pd.DataFrame, dict, Pipeline]:
    train, test = chronological_split(data)
    absent = train[FEATURES].columns[train[FEATURES].isna().all()].tolist()
    if absent:
        raise ValueError(f"Predictors entirely missing in training set: {', '.join(absent)}")
    model = Pipeline([("imputer", SimpleImputer(strategy="median")), ("regression", LinearRegression())])
    model.fit(train[FEATURES], train.GLD)
    predicted = model.predict(test[FEATURES])
    baseline = np.full(len(test), train.GLD.mean())
    predictions = pd.DataFrame({"Date": test.Date.to_numpy(), "actual_gld": test.GLD.to_numpy(),
                                "regression_prediction": predicted, "baseline_prediction": baseline})
    metrics = {"regression": evaluate(test.GLD, predicted), "baseline": evaluate(test.GLD, baseline),
               "train_rows": len(train), "test_rows": len(test),
               "train_date_range": [str(train.Date.min().date()), str(train.Date.max().date())],
               "test_date_range": [str(test.Date.min().date()), str(test.Date.max().date())]}
    return predictions, metrics, model
