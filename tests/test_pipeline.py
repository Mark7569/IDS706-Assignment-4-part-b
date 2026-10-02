import json
from pathlib import Path
import subprocess
import sys
import numpy as np
import pandas as pd
import pytest
from gold_analysis.pipeline import run_pipeline

FIXTURE = Path(__file__).parent / "fixtures/sample_prices.csv"


def test_cli(tmp_path):
    before = FIXTURE.read_bytes()
    result = subprocess.run([sys.executable, "-m", "gold_analysis", "--input", str(FIXTURE), "--output", str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "retained_rows: 15" in result.stdout
    yearly = pd.read_csv(tmp_path / "yearly_gld.csv")
    assert yearly.loc[0, "mean"] == 190
    assert yearly.loc[0, "count"] == 5
    assert yearly.loc[1, "mean"] == 240
    assert yearly.loc[1, "count"] == 5
    assert yearly.loc[10, "mean"] == 290
    assert pd.read_csv(tmp_path / "gld_above_200.csv").GLD.tolist() == list(range(210, 320, 10))
    predictions = pd.read_csv(tmp_path / "test_predictions.csv")
    assert predictions.Date.tolist() == ["2025-01-03", "2025-01-04", "2025-01-05"]
    np.testing.assert_allclose(predictions.baseline_prediction, 225)
    # Fixture GLD increases linearly with each predictor, including held-out rows.
    np.testing.assert_allclose(predictions.regression_prediction, [290, 300, 310], atol=1e-8)
    metrics = json.loads((tmp_path / "metrics.json").read_text(), parse_constant=lambda x: pytest.fail(x))
    assert metrics["baseline"]["mae"] == pytest.approx(75)
    assert metrics["baseline"]["rmse"] == pytest.approx(np.sqrt((65**2 + 75**2 + 85**2) / 3))
    for name in ["gld_timeseries.png", "yearly_gld.png", "actual_vs_predicted.png"]:
        assert (tmp_path / name).read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        assert (tmp_path / name).stat().st_size > 1000
    assert FIXTURE.read_bytes() == before


def test_cli_failure(tmp_path):
    result = subprocess.run([sys.executable, "-m", "gold_analysis", "--input", str(tmp_path / "missing.csv")], capture_output=True, text=True)
    assert result.returncode != 0
    assert "Error:" in result.stderr and "missing.csv" in result.stderr
    assert "Traceback" not in result.stderr


def test_raw_overwrite_protection(tmp_path):
    path = tmp_path / "yearly_gld.csv"
    path.write_bytes(FIXTURE.read_bytes())
    with pytest.raises(ValueError, match="Input must not"):
        run_pipeline(path, tmp_path)
    assert path.read_bytes() == FIXTURE.read_bytes()


def test_hardlinked_raw_overwrite_protection(tmp_path):
    source = tmp_path / "raw.csv"
    source.write_bytes(FIXTURE.read_bytes())
    (tmp_path / "yearly_gld.csv").hardlink_to(source)
    with pytest.raises(ValueError, match="Input must not"):
        run_pipeline(source, tmp_path)
    assert source.read_bytes() == FIXTURE.read_bytes()


def test_constant_target_json_and_empty_threshold(tmp_path):
    data = pd.read_csv(FIXTURE)
    data["GLD"] = 200
    source = tmp_path / "constant.csv"
    data.to_csv(source, index=False)
    output = tmp_path / "results"
    run_pipeline(source, output)
    metrics = json.loads((output / "metrics.json").read_text(),
                         parse_constant=lambda value: pytest.fail(value))
    for name in ["regression", "baseline"]:
        assert metrics[name] == {"mae": 0, "rmse": 0, "r2": None}
    empty = pd.read_csv(output / "gld_above_200.csv")
    assert empty.empty and empty.columns.tolist() == data.columns.tolist()


def test_cli_malformed_csv(tmp_path):
    source = tmp_path / "malformed.csv"
    source.write_text("Date,SPX,GLD,USO,SLV,EUR/USD\n2015-01-01,2000,170,30,15\n")
    output = tmp_path / "results"
    result = subprocess.run([sys.executable, "-m", "gold_analysis", "--input", str(source),
                             "--output", str(output)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "fields" in result.stderr and "Traceback" not in result.stderr
    assert not output.exists()
