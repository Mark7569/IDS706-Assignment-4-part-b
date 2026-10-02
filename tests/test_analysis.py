import numpy as np
import pandas as pd
from gold_analysis.analysis import above_threshold, yearly_summary


def test_years_and_missing_predictors(clean):
    data = clean.iloc[:5].copy()
    data["Date"] = pd.to_datetime(["2015-01-01", "2015-12-31", "2016-01-01", "2018-05-01", "2025-12-31"])
    data["GLD"] = [100, 200, 300, np.nan, 400]
    data["SPX"] = np.nan
    original = data.copy(deep=True)
    result = yearly_summary(data).set_index("year")
    assert result.index.tolist() == list(range(2015, 2026))
    assert result.loc[2015].tolist() == [150, 2]
    assert result.loc[2016].tolist() == [300, 1]
    for year in [2017, 2018]:
        assert result.loc[year, "count"] == 0
        assert np.isnan(result.loc[year, "mean"])
    assert result.loc[2025].tolist() == [400, 1]
    pd.testing.assert_frame_equal(data, original)


def test_threshold(clean):
    data = clean.iloc[:4].copy()
    data["GLD"] = [199, 200, 201, np.nan]
    original = data.copy(deep=True)
    assert above_threshold(data).GLD.tolist() == [201]
    empty = above_threshold(data, 999)
    assert empty.empty and empty.columns.tolist() == data.columns.tolist()
    assert len(above_threshold(data.dropna(), 0)) == 3
    pd.testing.assert_frame_equal(data, original)
