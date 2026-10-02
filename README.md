# GLD relationship analysis

A small Python project analyzing GLD and same-day market prices. It validates a CSV, summarizes yearly GLD values, filters GLD strictly above 200 USD/share, and evaluates contemporaneous linear regression against a training-mean baseline. This is association analysis, not future-price forecasting or evidence of causation.

## Local setup

Use **Python 3.13**, the same minor version as the Docker image. From the repository root:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
```

On Windows, activate with `.venv\Scripts\activate`. The five direct dependencies are pinned to tested versions in `requirements.txt`; transitive dependencies may change. No package installation or `PYTHONPATH` adjustment is needed.

Download the dataset following [data/README.md](data/README.md), then run:

```bash
python -m gold_analysis --input data/raw/gold_data_2015_25.csv --output outputs/real
```

For a self-contained demonstration with synthetic prices:

```bash
python -m gold_analysis --input tests/fixtures/sample_prices.csv --output outputs/sample
```

The console reports input and retained coverage, numeric summaries, missingness, duplicate removals, period exclusions, missing-target exclusions, split dates, and metrics. Invalid input returns a nonzero exit status with an error message. The CLI requires `--input`; `--output` defaults to `outputs`.

## Processing and outputs

Dates must be `YYYY-MM-DD`. The six required columns are Date, SPX, GLD, USO, SLV, and EUR/USD. Invalid dates, nonnumeric text, infinity, empty data, and conflicting same-date records fail validation. Exact duplicate rows are removed. Observations are sorted and restricted to 2015–2025 inclusive. No calendar filling or price repair occurs.

CSV headers must be unique, and each record must contain the same number of fields as the header. Represent missing numeric values with explicit blank cells; truncated or overlong records are rejected. Quoted commas and newlines in extra columns are supported.

Rows with missing GLD are excluded wherever a target is required, but remain visible as missing in the time series. Missing predictors do not exclude observations from descriptive summaries. The earliest `floor(0.8 * n)` usable rows train a median-imputation/linear-regression pipeline; the remaining rows form the test set. Only SPX, USO, SLV, and EUR/USD are predictors. Imputation uses training data only. An entirely missing training predictor fails clearly. At least 10 training and 2 test rows are required (13 usable observations); that safeguard does not establish statistical adequacy.

Reruns replace these seven named files in the selected output directory:

| File | Contents |
| --- | --- |
| `yearly_gld.csv` | All years 2015–2025, mean GLD and valid observation count; absent means are blank, never zero |
| `gld_above_200.csv` | Observations with GLD > 200; a header-only table is valid |
| `test_predictions.csv` | Date, actual GLD, regression prediction, training-mean prediction |
| `metrics.json` | MAE, RMSE, R² for both models plus split counts and dates; constant-test-target R² is JSON null |
| `gld_timeseries.png` | Observed GLD points without invented connections across absent dates |
| `yearly_gld.png` | Yearly averages; missing years break the line |
| `actual_vs_predicted.png` | Held-out actual/estimated values and perfect-agreement reference |

Raw input is unchanged. Generated artifacts and environments are ignored by Git. Analytical functions do not write files or mutate inputs; file operations belong to the pipeline and visualization modules. Imports do not load data, fit models, or create figures.

## Docker

```bash
docker build -t gold-analysis .
mkdir -p outputs/docker
docker run --rm --network none \
  -v "$PWD/data/raw:/data:ro" \
  -v "$PWD/outputs/docker:/outputs" \
  gold-analysis --input /data/gold_data_2015_25.csv --output /outputs
```

The single-stage image runs as non-root UID 10001 with a noninteractive plotting backend. It uses the same requirements (including pytest). Builds need network access; analysis does not. Raw data, environments, caches, outputs, and Git history are excluded from the build context.

Docker Desktop on macOS normally permits writes to this host mount. On Linux, either make the output directory writable by UID 10001 or add `--user "$(id -u):$(id -g)"` to run with your host identity. Input is mounted read-only and outputs persist on the host.

Run the synthetic tests without networking:

```bash
docker run --rm --network none \
  -v "$PWD/tests:/app/tests:ro" \
  --entrypoint python gold-analysis -m pytest -p no:cacheprovider -q
```

Exercise error handling locally and in Docker with `--input missing.csv` or `/data/missing.csv`; both should report the missing file and exit nonzero.

## Interpretation and verification

Actual dataset coverage is January 2, 2015–August 14, 2025, not eleven complete calendar years. Yearly means weight observed rows equally and can be biased by missing sessions and partial coverage. Same-date values may have different market closing times. Shared price trends and correlated predictors can inflate apparent fit or destabilize coefficients. Median imputation can distort associations; inspect missingness. A single chronological split does not prove robustness, and scores are not tuned to the holdout.

Tests use only small synthetic inputs, with independently calculated means, thresholds, split sizes, baseline predictions and metrics. They cover validation failures, date boundaries, missing data, input immutability, leakage prevention, constant-target R², CLI outputs and errors. They neither download data nor assert a real-data score or pixel-identical plots.

After running both environments, compare CSVs and JSON numerically with tolerances, check raw input is unchanged, and open all three plots for readable dates and units. See [docs/verification.md](docs/verification.md) for the completed checks and observed results. The approved [architecture plan](docs/plan.md) is preserved.
