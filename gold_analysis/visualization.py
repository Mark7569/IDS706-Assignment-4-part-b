"""Noninteractive figures from prepared results, without filling missing prices."""
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg


def save_plots(data, yearly, predictions, output: Path) -> None:
    def figure():
        fig = Figure(figsize=(9, 4.5), layout="constrained")
        FigureCanvasAgg(fig)
        return fig, fig.subplots()

    fig, ax = figure()
    # Points avoid drawing invented paths across unobserved dates or missing GLD.
    ax.plot(data.Date, data.GLD, ".", markersize=3)
    ax.set(title="Observed GLD values", xlabel="Observation date", ylabel="GLD adjusted close (USD/share)")
    fig.savefig(output / "gld_timeseries.png", dpi=150)

    fig, ax = figure()
    ax.plot(yearly.year, yearly["mean"], "o-")
    ax.set(title="Yearly mean GLD (observed values only)", xlabel="Year", ylabel="GLD adjusted close (USD/share)")
    ax.set_xticks(yearly.year)
    fig.savefig(output / "yearly_gld.png", dpi=150)

    fig, ax = figure()
    ax.scatter(predictions.actual_gld, predictions.regression_prediction, label="Regression")
    ax.scatter(predictions.actual_gld, predictions.baseline_prediction, marker="x", label="Training-mean baseline")
    bounds = [predictions.iloc[:, 1:].min().min(), predictions.iloc[:, 1:].max().max()]
    ax.plot(bounds, bounds, "k--", label="Perfect agreement")
    ax.set(title="Held-out contemporaneous estimates", xlabel="Actual GLD adjusted close (USD/share)", ylabel="Estimated GLD adjusted close (USD/share)")
    ax.legend()
    fig.savefig(output / "actual_vs_predicted.png", dpi=150)
