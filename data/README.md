# Dataset

Use [gold price 2015–2025 by Md. Anwar Hossain](https://www.kaggle.com/datasets/mdanwarhossain200110/gold-price-2015-2025), version 1, published August 15, 2025. Downloaded directly from Kaggle on October 1, 2026; no files were copied from the previous project.

From the repository root:

```bash
mkdir -p data/raw
curl -L --fail 'https://www.kaggle.com/api/v1/datasets/download/mdanwarhossain200110/gold-price-2015-2025' -o /tmp/gold-prices.zip
unzip -n /tmp/gold-prices.zip -d data/raw
```

Alternatively use Download on the dataset page (Kaggle may require sign-in) and extract `gold_data_2015_25.csv` into `data/raw/`. Keep the downloaded file unchanged. Raw CSVs are ignored by Git and excluded from Docker builds.

The downloaded CSV has **2,666 observations, January 2, 2015–August 14, 2025**, with dates in strict `YYYY-MM-DD` format. These are observed endpoints, not the broader endpoints in the uploader's description. The 2025 series ends in August. Weekends, holidays, and potentially other missing sessions are not inserted. Coverage has not been certified against an exchange calendar.

The [uploader's metadata](https://www.kaggle.com/api/v1/datasets/view/mdanwarhossain200110/gold-price-2015-2025) identifies Yahoo Finance via yfinance as the upstream source and defines the columns as follows:

| Column | Meaning | Unit |
| --- | --- | --- |
| Date | Observation date | YYYY-MM-DD; no time-zone or closing-time field |
| SPX | S&P 500 daily close | Index points |
| GLD | SPDR Gold Shares ETF adjusted close | USD per share |
| USO | United States Oil Fund ETF adjusted close | USD per share |
| SLV | iShares Silver Trust ETF adjusted close | USD per share |
| EUR/USD | Euro to US dollar exchange rate | USD per EUR |

GLD is an ETF share price, not a spot-gold quote per ounce. Its [official listing](https://www.ssga.com/us/en/individual/etfs/spdr-gold-shares-gld) confirms USD trading currency. Adjustment conventions above are attributed to the uploader; its exact yfinance version and collection settings are not supplied. Each row aligns the six fields by its one date, but simultaneous market closing times cannot be established from this file. No extra price-range restrictions or silent corrections are applied.

Kaggle lists **CC BY-SA 4.0**, and the uploader describes research, analysis, and educational use. Preserve attribution and the applicable share-alike terms when redistributing adaptations; the upstream provider's terms may also apply. This repository distributes only a synthetic test fixture, not the raw dataset.

Blank or whitespace-only numeric cells mean missing data; textual tokens such as `NA`, `NaN`, or `null` are rejected as invalid numeric text. Missing dates are invalid. Additional columns are retained in threshold output but never become model features.
