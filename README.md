# Hotel Bookings: Bronze, Silver, Gold Pipeline

A small personal project that builds a medallion-style data pipeline on a public
hotel bookings dataset (about 119,000 bookings from a city hotel and a resort hotel).
It takes raw data to business-ready tables, with automatic quality checks, and runs
with one command.

## Pipeline

| Layer | What it does | Output |
|---|---|---|
| **Extract** | Downloads the raw CSV exactly as published | `data/raw/hotels.csv` |
| **Bronze** | Loads the raw data unchanged, everything as text, with a load timestamp | `bronze.hotels` |
| **Silver** | Fixes types, turns placeholder text (`NULL`, `NA`) into real NULLs, builds a real arrival date, adds nights and estimated revenue, and flags rows that break business rules | `silver.hotels` |
| **Gold** | Builds four business-ready tables, using only valid rows | `gold.*` |
| **Quality checks** | Ten automatic checks that stop the run if the numbers do not add up | `src/quality_checks.py` |

### Gold tables
- `monthly_performance`: bookings, cancellations, cancellation rate, average daily rate and estimated revenue by month and hotel
- `rate_by_season_segment`: average daily rate by hotel, season and booking channel
- `cancellation_by_segment`: cancellation rate by booking channel and deposit type
- `lead_time_buckets`: average rate and cancellation rate by how far ahead guests book

## Status
- [x] Extract: download the raw file
- [x] Bronze: load raw data unchanged
- [x] Silver: clean and standardize
- [x] Gold: business-ready tables
- [x] Data quality tests
- [x] One-command run

## How to run
```
pip install -r requirements.txt
python run_pipeline.py
```
Add `--skip-download` to reuse a file you already downloaded.
On Windows with several Python versions installed, use `py -3.13 run_pipeline.py`.

Expected result: bronze 119,390 rows, silver 118,564 valid and 826 flagged, four gold tables, and `10/10 checks passed`.

## Example finding
Cancellations rise steadily with lead time, while the average daily rate rises, plateaus and then falls. Price alone does not explain the cancellation pattern.

| Lead time | Bookings | Avg daily rate | Cancellation rate |
|---|---|---|---|
| 0-7 days | 19,246 | 91.65 | 9.7% |
| 8-30 days | 18,848 | 105.39 | 28.0% |
| 31-90 days | 29,437 | 104.47 | 37.8% |
| 91-180 days | 26,384 | 106.52 | 44.8% |
| 181+ days | 24,649 | 97.19 | 57.1% |

These are associations in observed data, not proof of cause. A natural next step would be to break the long-lead group down by deposit type and booking channel.

## Design decisions and limitations
- **Flag, do not delete.** Silver marks bad rows (negative rate, zero guests, zero nights) instead of removing them, so nothing disappears silently. Gold decides what to exclude.
- **Duplicates were kept.** About 32,000 rows are exact copies of another row. The dataset has no booking ID, so true duplicates cannot be told apart from separate bookings that look the same, and none were removed.
- **Revenue is an estimate.** `estimated_revenue` is average daily rate times nights, counted only for stays that were not cancelled.
- **Some patterns look odd.** For example, non-refundable bookings from some channels show cancellation rates above 90%. This is worth investigating and may be a data quirk.

## Tools
Python 3.13, DuckDB, SQL. Code was drafted and debugged with AI assistance (Claude).

## Data
Hotel Booking Demand dataset, published via TidyTuesday (2020-02-11).
