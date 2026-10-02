import numpy as np
import pandas as pd
import pytest
from gold_analysis.modeling import FEATURES, chronological_split, fit_and_evaluate, evaluate


def test_split_rounding_and_features(clean):
    data = clean.iloc[:13].iloc[::-1].copy()
    train, test = chronological_split(data)
    assert len(train) == 10 and len(test) == 3
    assert train.Date.max() < test.Date.min()
    data["extra"] = "ignored"
    original = data.copy(deep=True)
    _, _, model = fit_and_evaluate(data)
    assert list(model.feature_names_in_) == ["SPX", "USO", "SLV", "EUR/USD"]
    pd.testing.assert_frame_equal(data, original)
    with pytest.raises(ValueError, match="Insufficient"):
        chronological_split(data.iloc[:12])
    data.loc[data.index[0], "GLD"] = np.nan
    with pytest.raises(ValueError, match="Insufficient"):
        chronological_split(data)


def test_training_only_imputation_and_baseline(clean):
    data = clean.copy()
    n = int(0.8 * len(data))
    data.loc[0, "SPX"] = np.nan
    data.loc[n:, "SPX"] = 1e9
    data.loc[n, "USO"] = np.nan
    data.loc[n:, "GLD"] = 10000
    predictions, metrics, model = fit_and_evaluate(data)
    np.testing.assert_allclose(model.named_steps["imputer"].statistics_, data.iloc[:n][FEATURES].median())
    np.testing.assert_allclose(predictions.baseline_prediction, data.iloc[:n].GLD.mean())
    assert metrics["regression"]["r2"] is None
    assert metrics["baseline"]["r2"] is None
    assert np.isfinite(predictions.regression_prediction).all()
    data.loc[:n-1, "SLV"] = np.nan
    with pytest.raises(ValueError, match="entirely missing.*SLV"):
        fit_and_evaluate(data)


def test_metrics_independently():
    metrics = evaluate([1, 2, 3], [2, 2, 5])
    assert metrics["mae"] == pytest.approx(1)
    assert metrics["rmse"] == pytest.approx(np.sqrt(5 / 3))
    assert metrics["r2"] == pytest.approx(-1.5)
    assert evaluate([2, 2], [1, 3])["r2"] is None


def test_missing_targets_removed_before_split(clean):
    data = clean.copy()
    data.loc[[0, 13], "GLD"] = np.nan
    train, test = chronological_split(data.iloc[::-1])
    assert len(train) == 10 and len(test) == 3
    assert train.Date.tolist() == clean.Date.iloc[1:11].tolist()
    assert test.Date.tolist() == clean.Date.iloc[[11, 12, 14]].tolist()
    predictions, _, _ = fit_and_evaluate(data)
    np.testing.assert_allclose(predictions.baseline_prediction, 225)
