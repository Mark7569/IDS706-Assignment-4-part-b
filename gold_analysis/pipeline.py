"""File-oriented orchestration of the pure analytical functions."""
import json
from pathlib import Path
from .data import load_data, clean_data
from .analysis import yearly_summary, above_threshold
from .modeling import fit_and_evaluate
from .visualization import save_plots


def run_pipeline(input_path: str | Path, output_path: str | Path) -> dict:
    output = Path(output_path)
    names = ["yearly_gld.csv", "gld_above_200.csv", "test_predictions.csv", "metrics.json",
             "gld_timeseries.png", "yearly_gld.png", "actual_vs_predicted.png"]
    source = Path(input_path)
    destinations = [output / name for name in names]
    if any(source.resolve() == path.resolve() or
           (source.exists() and path.exists() and source.samefile(path))
           for path in destinations):
        raise ValueError("Input must not be one of the output files; choose a separate output directory.")
    data, report = clean_data(load_data(input_path))
    for key, value in report.items():
        print(f"{key}: {value}")
    yearly = yearly_summary(data)
    predictions, metrics, _ = fit_and_evaluate(data)
    output.mkdir(parents=True, exist_ok=True)
    yearly.to_csv(output / "yearly_gld.csv", index=False)
    above_threshold(data).to_csv(output / "gld_above_200.csv", index=False)
    predictions.to_csv(output / "test_predictions.csv", index=False)
    (output / "metrics.json").write_text(json.dumps(metrics, indent=2, allow_nan=False) + "\n")
    save_plots(data, yearly, predictions, output)
    print(json.dumps(metrics, indent=2, allow_nan=False))
    print("Coverage may include partial years and gaps; counts are observations, not complete trading sessions.")
    return metrics
