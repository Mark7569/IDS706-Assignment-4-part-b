# Implementation verification — October 1, 2026

## Tester review — final verification

Read the approved plan before reviewing implementation and tests. The original 21 tests passed. Review found two input-integrity problems, reproduced with four failing regression cases before applying fixes:

- pandas CSV inference silently accepted overlong records by treating a field as an index, padded short records as missing data, and renamed duplicate headers (including duplicate GLD columns). The loader now checks unique headers and exact record widths with Python's CSV reader before constructing a string DataFrame. Explicit empty cells, UTF-8 BOMs, and quoted commas/newlines remain supported.
- Output protection compared resolved paths but missed hard links. An output hard-linked to the source could overwrite raw data. The pipeline now also checks file identity before writing any results.

Expanded checks cover those failures, valid quoted CSV content, malformed-input CLI errors, exact synthetic regression predictions, missing-target removal before splitting, constant-target JSON nulls, and header-only threshold output.

Final results: **29 passed locally and 29 passed in the rebuilt Docker image**, with runtime networking disabled in Docker. The existing 14 matplotlib/pyparsing deprecation warnings remain non-failing. Re-ran the real-data pipeline locally and in Docker with read-only container input; local raw bytes remained unchanged. All three CSV tables and JSON metrics agree at `rtol=1e-10`, `atol=1e-10`. Visually inspected all three regenerated real-data plots: labels, dates, units, and legends are readable. The container missing-file CLI exits with status 1 and no traceback. Generated outputs are in `outputs/tester-real` and `outputs/tester-docker-real`.

The reviewed implementation follows the approved analytical plan. No train/test leakage was found: features exclude date and target, missing targets are removed before chronological splitting, imputation uses training medians, and the baseline uses only training targets. The documented limitations concerning partial coverage, unsynchronized closes, and association rather than forecasting remain appropriate. Git ignores raw data, outputs, and the environment; whitespace checks pass. This review reused the existing Python 3.13 environment; the original clean-install verification and temporary-interpreter caveat below still apply.

## Builder verification record

The approved architecture in `docs/plan.md` was implemented without scope changes. Python 3.13, strict ISO dates, and the real filename were finalized during implementation. Data was downloaded directly from the requested Kaggle dataset, not copied from the previous repository.

## Completed checks

- Created a clean local virtual environment and installed only `requirements.txt`. The system's Python 3.13 links were broken, so local verification used a standalone CPython 3.13 interpreter in `/tmp/gold-python`. The current `.venv` depends on that temporary interpreter; for ongoing use, install Python 3.13 normally and recreate the environment using the README.
- Local pytest: **21 passed**. Final Docker image pytest with networking disabled: **21 passed**. Tests use synthetic data only.
- Built the single-stage `python:3.13-slim` image and ran as its non-root user, with read-only input and a writable host output mount. Runtime networking was disabled.
- Ran synthetic and real-data pipelines locally and in Docker. All three CSV tables and JSON metrics agreed with `rtol=1e-10`, `atol=1e-10`; split dates and counts matched exactly.
- Independently checked synthetic yearly means (190, 240, 290), counts (5 each), strict threshold selection (210 through 310), 12/3 split, baseline prediction 225, baseline MAE 75, and RMSE 75.4431353.
- Checked real yearly counts and means, threshold output (356 rows), test dates/counts, and valid JSON. Opened all three local real-data plots and checked dates, units, legends, and layout. Time-series points do not interpolate unobserved sessions; yearly missing values break plotted lines.
- Missing-file CLI checks returned status 1 and an actionable message locally and in Docker.
- Compared raw input bytes with the downloaded ZIP member after execution: unchanged. Confirmed Git ignores raw CSVs, generated outputs and `.venv`; `git diff --check` passed.

## Real-data results

The inspected file contains 2,666 rows from **2015-01-02 through 2025-08-14**, all within the intended study period. Missing numeric values, exact duplicate rows, conflicting dates, and missing GLD exclusions were all zero.

Training: 2,132 observations, 2015-01-02–2023-06-27. Testing: 534 observations, 2023-06-28–2025-08-14.

| Model | MAE (USD/share) | RMSE (USD/share) | R² |
| --- | --- | --- | --- |
| Linear regression | 31.273315 | 41.883123 | 0.100359 |
| Training-mean baseline | 90.305223 | 100.523220 | -4.182316 |

Regression improves on this baseline but explains little held-out variation under R². The plot shows substantial underestimation at higher GLD values. These are same-day association estimates, not future forecasts or causal effects.

The 2025 mean is 288.867581 across 153 observations, ending August 14; it is not a full-year mean. Counts for 2015–2024 range from 249 to 253. Missing exchange sessions have not been independently reconciled against market calendars, and synchronized closing times cannot be verified from a date-only CSV.

## Environment notes

Matplotlib 3.10.3 emits 14 deprecation warnings from the installed transitive pyparsing version. They do not fail tests or prevent figures from rendering. Local sandbox restrictions also caused a font-cache warning on first plot generation; verification used a writable `MPLCONFIGDIR` under `/tmp`. These environment details do not change analytical results. Dependency pins cover the five direct dependencies, not all transitive packages.

Generated examples are in `outputs/real`, `outputs/sample`, `outputs/docker-real`, and `outputs/docker-fixture` in the working checkout. They are intentionally untracked and can be regenerated using the documented commands.
