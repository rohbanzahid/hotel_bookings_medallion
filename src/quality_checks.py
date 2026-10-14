"""Step 5: DATA QUALITY CHECKS. Automatic tests that run after the pipeline.

Each check is a SQL question that should return TRUE. If any check fails,
the pipeline stops with an error instead of quietly producing bad numbers.
"""
import sys
import duckdb

DB_PATH = "data/warehouse.duckdb"

CHECKS = [
    # name, SQL that returns a single TRUE/FALSE
    ("bronze has rows",
     "SELECT COUNT(*) > 0 FROM bronze.hotels"),
    ("silver keeps every bronze row (nothing silently dropped)",
     "SELECT (SELECT COUNT(*) FROM silver.hotels) = (SELECT COUNT(*) FROM bronze.hotels)"),
    ("silver: no missing arrival dates",
     "SELECT COUNT(*) = 0 FROM silver.hotels WHERE arrival_date IS NULL"),
    ("silver: no missing hotel names",
     "SELECT COUNT(*) = 0 FROM silver.hotels WHERE hotel IS NULL"),
    ("silver: valid + flagged rows add up to total",
     "SELECT COUNT(*) FILTER (WHERE is_valid_booking) + COUNT(*) FILTER (WHERE NOT is_valid_booking) = COUNT(*) FROM silver.hotels"),
    ("gold: monthly bookings add up to silver valid rows",
     "SELECT (SELECT SUM(bookings) FROM gold.monthly_performance) = (SELECT COUNT(*) FROM silver.hotels WHERE is_valid_booking)"),
    ("gold: lead-time buckets add up to silver valid rows",
     "SELECT (SELECT SUM(bookings) FROM gold.lead_time_buckets) = (SELECT COUNT(*) FROM silver.hotels WHERE is_valid_booking)"),
    ("gold: cancellation rates are between 0 and 1",
     "SELECT COUNT(*) = 0 FROM gold.monthly_performance WHERE cancellation_rate < 0 OR cancellation_rate > 1"),
    ("gold: no negative average rates",
     "SELECT COUNT(*) = 0 FROM gold.rate_by_season_segment WHERE avg_daily_rate < 0"),
    ("gold: one row per year, month and hotel",
     "SELECT COUNT(*) = 0 FROM (SELECT arrival_year, arrival_month, hotel FROM gold.monthly_performance GROUP BY ALL HAVING COUNT(*) > 1)"),
]


def run_checks() -> bool:
    con = duckdb.connect(DB_PATH, read_only=True)
    failures = 0
    for name, sql in CHECKS:
        passed = bool(con.execute(sql).fetchone()[0])
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
        failures += 0 if passed else 1
    con.close()
    print(f"{len(CHECKS) - failures}/{len(CHECKS)} checks passed")
    return failures == 0


if __name__ == "__main__":
    sys.exit(0 if run_checks() else 1)
