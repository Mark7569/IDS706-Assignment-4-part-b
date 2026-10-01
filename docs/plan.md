# Gold Price Analysis Project Plan

## Goals and scope

Rebuild the previous Python analysis as a small, modular course project rather than copying its implementation. Analyze a CSV containing `Date`, `SPX`, `GLD`, `USO`, `SLV`, and `EUR/USD`, with an intended study period of 2015–2025. Confirm actual coverage before claiming the dataset spans that period.

The project will inspect and clean data, calculate yearly GLD averages, filter GLD values strictly above 200, visualize results, and evaluate contemporaneous linear regression. The model will analyze associations between GLD and same-day market prices; it will not forecast future prices or establish causation.

Keep setup simple: use a virtual environment, `pip`, and `requirements.txt`. Do not introduce `uv.lock`, an input checksum or audit system, a database, a web application, or forecasting features. This document is the plan only; implementation follows a separate review.

## Proposed structure

```text
.
├── README.md
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── docs/
│   └── plan.md
├── data/
│   ├── README.md
│   └── raw/
├── gold_analysis/
│   ├── __init__.py
│   ├── __main__.py
│   ├── data.py
│   ├── analysis.py
│   ├── modeling.py
│   ├── visualization.py
│   └── pipeline.py
├── tests/
│   ├── fixtures/
│   │   └── sample_prices.csv
│   ├── test_data.py
│   ├── test_analysis.py
│   ├── test_modeling.py
│   └── test_pipeline.py
└── outputs/
```

Use a root-level Python package so the project can run from the repository root without packaging configuration or `PYTHONPATH` changes. Preserve separation of responsibilities without a separate configuration framework or CLI module.

### Important files

- `README.md`: supported Python version, local setup, commands, expected outputs, interpretation, and limitations.
- `requirements.txt`: exact tested versions of pandas, NumPy, scikit-learn, matplotlib, and pytest. Use one dependency file for this small project; no separate development dependency system is needed.
- `data/README.md`: source and download instructions, column definitions and units, expected date format, actual coverage, and redistribution restrictions. A separate data dictionary is unnecessary.
- `__main__.py`: a small `argparse` entry point accepting input and output paths; report actionable errors and return a nonzero exit status on failure.
- `data.py`: load, inspect, validate, and clean the CSV.
- `analysis.py`: functions for yearly summaries and strict threshold filtering.
- `modeling.py`: chronological split, preprocessing, regression, baseline, and metrics.
- `visualization.py`: plot prepared results and save figures.
- `pipeline.py`: coordinate the steps and write outputs.

Raw data stays unchanged. Generated outputs and virtual environments are ignored by Git. Analytical functions accept data and return results without writing files or modifying their input. Imports must not load data, train models, or generate plots.

## Analysis approach

### 1. Inspect and validate

- Require the six expected columns; ignore extra columns when selecting model features.
- Display row count, date range, missing-value counts, duplicates, and numeric summaries in a concise console report.
- Parse dates using the documented dataset format, with no ambiguous date guessing.
- Reject empty input, invalid dates, malformed numeric values, and infinity with clear messages. Distinguish missing numeric values from invalid text.
- Remove exact duplicate rows and report the count. Reject conflicting records for the same date.
- Sort by date and restrict analysis to January 1, 2015 through December 31, 2025, inclusive. Report excluded out-of-period rows and fail if none remain.
- Do not insert calendar dates, forward-fill prices, or silently repair suspicious values. Check unusual ranges against source definitions before choosing additional validation rules.

### 2. Handle missing data

- Exclude rows with missing GLD from calculations and modeling that require GLD, reporting the count. Fail clearly if no usable GLD observations remain.
- Retain rows with missing predictors for descriptive GLD analysis.
- For modeling, impute missing predictors with training-set medians using a scikit-learn pipeline.
- Reject a predictor that is entirely missing in the training set.
- Do not impute GLD or fit preprocessing on the complete dataset.

### 3. Summarize and visualize

- Calculate yearly mean GLD and the count of valid observations per year. Include all study years; years without observations have count zero and a missing mean, never a zero price.
- Filter observations using `GLD > 200`; a value equal to 200 is excluded. No matches is a valid result with an empty table retaining its columns.
- Create a GLD time-series plot, a yearly-average chart, and a held-out actual-versus-predicted plot. Use readable labels and verified units.
- Note partial-year coverage and gaps when interpreting yearly averages. Plot gaps without inventing values.

### 4. Fit and evaluate contemporaneous regression

- Target: `GLD`. Predictors: `SPX`, `USO`, `SLV`, and `EUR/USD` from the same observation date. Exclude `Date` and `GLD` from predictors.
- After cleaning and excluding missing targets, use the earliest 80% of rows for training and the latest 20% for testing, without shuffling. Define the training count as `floor(0.8 * n)`.
- Require at least 10 training rows and 2 test rows. These are execution safeguards, not evidence of adequate statistical sample size.
- Fit median imputation and linear regression on training data only. Scaling is unnecessary for the initial unregularized model.
- Compare against a baseline that predicts the training-set mean GLD for every test row.
- Report MAE, RMSE, and R² for both models on the same test observations. If test GLD is constant, report R² as unavailable rather than a misleading numeric result.
- Do not tune the model against the held-out test set or promise a minimum predictive score.

### 5. Save simple outputs

Write `yearly_gld.csv`, `gld_above_200.csv`, `test_predictions.csv`, `metrics.json`, and the three plot images under the selected output directory. Predictions include dates, actual GLD, regression predictions, and baseline predictions. Use JSON `null` for unavailable metrics.

Print retained and excluded row counts and train/test date ranges to the console. No checksum, run manifest, model registry, or audit subsystem is needed. Document that reruns replace the named generated files in the chosen output directory.

## Testing strategy and edge cases

Use pytest and small synthetic inputs with independently calculated expected results. Tests must not download data or depend on the full dataset.

| Area | Required checks |
| --- | --- |
| Loading | Missing file, empty file, header-only CSV, missing required columns, additional columns |
| Validation | Invalid or ambiguous dates, invalid numeric text, infinity, missing numeric values |
| Cleaning | Unsorted dates, exact duplicates, conflicting duplicate dates, date-range boundaries, all rows outside the study period, unchanged input |
| Missing data | Missing GLD exclusions, all GLD missing, predictor missingness does not affect descriptive summaries, entirely missing training predictor |
| Yearly averages | Known means and counts, year boundaries, partial years, absent years, years with no valid GLD |
| Threshold | Below 200, exactly 200, above 200, no matches, all matches |
| Model preparation | Exact feature list, chronological split and rounding, insufficient observations, no train/test date overlap |
| Leakage prevention | Training-only imputer statistics even when test data have extreme values or missing predictors |
| Evaluation | Independently calculated metrics, constant test target, baseline derived only from training targets |
| Integration | Run the CLI on a fixture using a temporary output directory; check table contents, prediction dates/counts, valid JSON, and nonempty image files |
| Error behavior | Invalid input produces a useful message and nonzero exit status |

Avoid tests that assert a particular real-data R², exact floating-point coefficients, or pixel-identical plots. Use numeric tolerances where appropriate. Inspect plot readability manually rather than maintaining brittle image snapshots.

## Local setup and Docker

Choose and document one supported Python minor version, using the same version locally and in a slim official Python Docker image. Pin dependency versions after confirming compatibility during implementation. A requirements file with exact versions is sufficient for this assignment, though it does not guarantee an identical transitive environment forever.

Planned local commands, run from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
python -m gold_analysis --input data/raw/gold_prices.csv --output outputs
```

The filename above is illustrative; document the real filename when the dataset is selected.

Use a single-stage Dockerfile for simplicity. Install the same requirements, copy the package, set a noninteractive matplotlib backend, and run as a non-root user. Using the same requirements includes pytest in the image; that small tradeoff avoids extra dependency files and build stages.

Exclude `.git`, `.venv`, caches, raw data, and outputs from the build context. Mount input read-only and outputs separately. Ensure the host output directory is writable by the container user; document any platform-specific ownership setup. No Docker Compose is needed.

Planned container commands:

```bash
docker build -t gold-analysis .
mkdir -p outputs
docker run --rm \
  -v "$PWD/data/raw:/data:ro" \
  -v "$PWD/outputs:/outputs" \
  gold-analysis --input /data/gold_prices.csv --output /outputs
```

The container entry point will be `python -m gold_analysis`. Runtime analysis should not require network access.

## Risks and design concerns

- Verify whether GLD is an ETF price, its units, and whether prices are adjusted. Do not label it spot gold without supporting source information.
- Verify actual 2015–2025 coverage. Missing sessions and partial years can bias summaries.
- Confirm that columns are aligned to the same dates. Different market calendars and closing times limit interpretation of same-day relationships.
- Regression describes association, not causation or future forecasting. Shared price trends can inflate fit, and correlated predictors can destabilize coefficients.
- Median imputation is simple but can distort relationships when missingness is substantial; report missingness and discuss its effect.
- A chronological holdout helps evaluate later observations, but a single split does not establish robustness across all market conditions.
- Confirm dataset licensing before committing raw data; otherwise provide acquisition instructions.
- Floating-point results may differ slightly across operating systems and numerical libraries. Compare numeric outputs using tolerances.
- Keep the scope focused. Automated CI and next-day forecasting can be added later if the course requires them.

## Verification and completion criteria

1. Obtain the dataset using `data/README.md`; confirm column meanings, date format, coverage, and permission to use it.
2. Follow the README from a fresh checkout and create a clean virtual environment. Install dependencies using only `requirements.txt`.
3. Run the full pytest suite. Confirm it works without the real dataset or network access.
4. Run the pipeline on a synthetic fixture. Independently verify yearly averages, strict threshold behavior, chronological splitting, and baseline metrics.
5. Run the pipeline on real data. Review missingness, exclusions, actual study coverage, train/test dates, and model-versus-baseline results.
6. Open generated CSV and JSON files and visually inspect all plots for correct labels, dates, and readable output.
7. Build and run Docker with read-only input and a writable output mount. Confirm outputs persist on the host and the raw file is unchanged.
8. Compare local and container tables and metrics on the same input, allowing small numerical differences. Do not require identical image bytes.
9. Exercise one invalid-input case through both the local and container CLI; verify a clear error and nonzero exit status.
10. Confirm the README contains every required setup step, and Git excludes generated artifacts and environments.

Implementation is complete when these checks pass and the documentation consistently describes contemporaneous association analysis rather than forecasting.
