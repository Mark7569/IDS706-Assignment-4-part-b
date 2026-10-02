import numpy as np
import pandas as pd
import pytest
from gold_analysis.data import clean_data, load_data


def test_loading_errors(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_data(tmp_path / "absent.csv")
    path = tmp_path / "empty.csv"
    path.write_text("")
    with pytest.raises(ValueError, match="empty"):
        load_data(path)
    path.write_text("Date,SPX,GLD,USO,SLV,EUR/USD\n")
    with pytest.raises(ValueError, match="no observations"):
        clean_data(load_data(path))


@pytest.mark.parametrize("contents,message", [
    ("Date,SPX,GLD,USO,SLV,EUR/USD\nignored,2015-01-01,2000,170,30,15,1.1\n", "fields"),
    ("Date,SPX,GLD,USO,SLV,EUR/USD\n2015-01-01,2000,170,30,15\n", "fields"),
    ("Date,SPX,GLD,USO,SLV,EUR/USD,GLD\n2015-01-01,2000,170,30,15,1.1,999\n", "Duplicate column"),
])
def test_malformed_csv(tmp_path, contents, message):
    path = tmp_path / "malformed.csv"
    path.write_text(contents)
    with pytest.raises(ValueError, match=message):
        load_data(path)


def test_csv_quoted_extras_and_explicit_missing(tmp_path):
    path = tmp_path / "quoted.csv"
    path.write_text('\ufeffDate,SPX,GLD,USO,SLV,EUR/USD,note\n'
                    '2015-01-01,2000,170,30,15,,"comma, and\nnewline"\n')
    data, _ = clean_data(load_data(path))
    assert np.isnan(data.loc[0, "EUR/USD"])
    assert data.loc[0, "note"] == "comma, and\nnewline"


@pytest.mark.parametrize("column,value,message", [
    ("Date", "01/02/2015", "YYYY-MM-DD"), ("Date", "2015-02-30", "Invalid calendar"),
    ("Date", "2015-1-01", "YYYY-MM-DD"), ("Date", "", "YYYY-MM-DD"),
    ("GLD", "oops", "Invalid numeric"), ("SPX", "NaN", "Invalid numeric"),
    ("SLV", "inf", "Infinity"), ("USO", "-inf", "Infinity")])
def test_invalid(raw, column, value, message):
    raw.loc[0, column] = value
    with pytest.raises(ValueError, match=message):
        clean_data(raw)


def test_columns_and_unchanged_input(raw):
    with pytest.raises(ValueError, match="Missing required.*SPX"):
        clean_data(raw.drop(columns="SPX"))
    raw["extra"] = "note"
    original = raw.copy(deep=True)
    result, _ = clean_data(raw)
    pd.testing.assert_frame_equal(raw, original)
    assert "extra" in result


def test_sort_duplicates_and_conflicts(raw):
    shuffled = pd.concat([raw.iloc[::-1], raw.iloc[[0]]], ignore_index=True)
    data, report = clean_data(shuffled)
    assert data.Date.is_monotonic_increasing
    assert report["exact_duplicates_removed"] == 1
    assert len(data) == len(raw)
    duplicate = raw.iloc[[0]].copy()
    duplicate["GLD"] = "999"
    with pytest.raises(ValueError, match="Conflicting"):
        clean_data(pd.concat([raw, duplicate]))


def test_boundaries(raw):
    frame = raw.iloc[:4].copy()
    frame["Date"] = ["2014-12-31", "2015-01-01", "2025-12-31", "2026-01-01"]
    data, report = clean_data(frame)
    assert data.Date.dt.strftime("%Y-%m-%d").tolist() == ["2015-01-01", "2025-12-31"]
    assert report["out_of_period_rows"] == 2
    with pytest.raises(ValueError, match="No observations remain"):
        clean_data(frame.iloc[[0, 3]])


def test_missing_values(raw):
    raw.loc[0, "GLD"] = ""
    raw.loc[1, "SPX"] = " "
    data, report = clean_data(raw)
    assert len(data) == len(raw)
    assert np.isnan(data.loc[0, "GLD"])
    assert np.isnan(data.loc[1, "SPX"])
    assert report["missing_gld_excluded"] == 1
    assert report["usable_gld_rows"] == len(raw) - 1
    raw["GLD"] = ""
    with pytest.raises(ValueError, match="No usable GLD"):
        clean_data(raw)
