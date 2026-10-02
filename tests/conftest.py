from pathlib import Path
import pandas as pd
import pytest
from gold_analysis.data import clean_data, load_data


@pytest.fixture
def raw():
    return load_data(Path(__file__).parent / "fixtures/sample_prices.csv")


@pytest.fixture
def clean(raw):
    return clean_data(raw)[0]
