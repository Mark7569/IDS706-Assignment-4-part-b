"""Pure descriptive operations on validated observations."""
import pandas as pd
from .data import YEARS


def yearly_summary(data: pd.DataFrame) -> pd.DataFrame:
    result = data.groupby(data.Date.dt.year).GLD.agg(mean="mean", count="count")
    result = result.reindex(YEARS)
    result["count"] = result["count"].fillna(0).astype(int)
    return result.rename_axis("year").reset_index()


def above_threshold(data: pd.DataFrame, threshold: float = 200) -> pd.DataFrame:
    return data.loc[data.GLD > threshold].copy()
