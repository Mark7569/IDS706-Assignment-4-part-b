"""Explicit CSV validation and immutable cleaning."""
import csv
from pathlib import Path

import numpy as np
import pandas as pd

COLUMNS = ["Date", "SPX", "GLD", "USO", "SLV", "EUR/USD"]
NUMERIC = COLUMNS[1:]
YEARS = range(2015, 2026)


def load_data(path: str | Path) -> pd.DataFrame:
    """Load strings with explicit headers and row widths; never infer an index."""
    try:
        with Path(path).open(encoding="utf-8-sig", newline="") as source:
            reader = csv.reader(source, strict=True)
            header = next((row for row in reader if row), None)
            if header is None:
                raise ValueError("Input CSV is empty; supply a header and observations.")
            if len(set(header)) != len(header):
                raise ValueError("Duplicate column names in CSV header; use unique names.")
            rows = []
            for row in reader:
                if not row:
                    continue
                if len(row) != len(header):
                    raise ValueError(
                        f"CSV record ending at line {reader.line_num} has {len(row)} fields; "
                        f"expected {len(header)}. Use blank cells for missing values."
                    )
                rows.append(row)
    except csv.Error as exc:
        raise ValueError(f"Malformed CSV: {exc}") from exc
    return pd.DataFrame(rows, columns=header, dtype=str)


def clean_data(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Validate, deduplicate, sort and restrict dates; preserve missing targets."""
    missing = set(COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if frame.empty:
        raise ValueError("Input has no observations.")
    data = frame.copy(deep=True)
    raw_dates = data["Date"].astype(str)
    if not raw_dates.str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
        raise ValueError("Date must use unambiguous YYYY-MM-DD format.")
    try:
        data["Date"] = pd.to_datetime(raw_dates, format="%Y-%m-%d", errors="raise")
    except ValueError as exc:
        raise ValueError("Invalid calendar date; expected YYYY-MM-DD.") from exc
    for column in NUMERIC:
        values = data[column].mask(data[column].astype(str).str.fullmatch(r"\s*"), np.nan)
        try:
            numeric = pd.to_numeric(values, errors="raise")
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Invalid numeric value in {column}; use blank cells for missing values.") from exc
        if np.isinf(numeric.to_numpy(dtype=float)).any():
            raise ValueError(f"Infinity is not allowed in {column}.")
        data[column] = numeric
    report = {
        "input_rows": len(data),
        "input_date_range": [str(data.Date.min().date()), str(data.Date.max().date())],
        "missing_values": data[NUMERIC].isna().sum().to_dict(),
        "exact_duplicates_removed": int(data.duplicated().sum()),
        "numeric_summary": data[NUMERIC].describe().to_string(),
    }
    data = data.drop_duplicates()
    if data.Date.duplicated().any():
        raise ValueError("Conflicting records for the same date; resolve them at the source.")
    in_period = data.Date.between("2015-01-01", "2025-12-31")
    report["out_of_period_rows"] = int((~in_period).sum())
    data = data.loc[in_period].sort_values("Date").reset_index(drop=True)
    if data.empty:
        raise ValueError("No observations remain within 2015–2025.")
    report["retained_rows"] = len(data)
    report["missing_gld_excluded"] = int(data.GLD.isna().sum())
    report["usable_gld_rows"] = int(data.GLD.notna().sum())
    report["retained_date_range"] = [str(data.Date.min().date()), str(data.Date.max().date())]
    if not data.GLD.notna().any():
        raise ValueError("No usable GLD observations remain; all retained GLD values are missing.")
    return data, report
