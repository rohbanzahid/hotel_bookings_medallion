"""Step 4: GOLD. Build business-ready tables from the cleaned silver data.

Gold rules:
  1. Only use rows that passed silver's checks (is_valid_booking = true).
  2. Each table answers one business question, so a dashboard can read it directly.
  3. Revenue only counts stays that actually happened (not cancelled).
     estimated_revenue = adr (average daily rate) x nights, so it is an estimate.
"""
import duckdb

DB_PATH = "data/warehouse.duckdb"

TABLES = {
    # Q1: How are bookings, cancellations and revenue trending each month?
    "monthly_performance": """
        SELECT
            arrival_year,
            MONTH(arrival_date)                                   AS arrival_month,
            hotel,
            COUNT(*)                                              AS bookings,
            COUNT(*) FILTER (WHERE is_canceled)                   AS cancellations,
            ROUND(COUNT(*) FILTER (WHERE is_canceled) * 1.0 / COUNT(*), 3)
                                                                  AS cancellation_rate,
            ROUND(AVG(adr) FILTER (WHERE NOT is_canceled), 2)     AS avg_daily_rate,
            ROUND(SUM(estimated_revenue) FILTER (WHERE NOT is_canceled), 0)
                                                                  AS estimated_revenue
        FROM silver.hotels
        WHERE is_valid_booking
        GROUP BY arrival_year, MONTH(arrival_date), hotel
        ORDER BY arrival_year, arrival_month, hotel
    """,
    # Q2: How does the nightly rate change by season and booking channel?
    "rate_by_season_segment": """
        SELECT
            hotel,
            CASE
                WHEN MONTH(arrival_date) IN (6, 7, 8)   THEN 'Summer'
                WHEN MONTH(arrival_date) IN (12, 1, 2)  THEN 'Winter'
                WHEN MONTH(arrival_date) IN (3, 4, 5)   THEN 'Spring'
                ELSE 'Fall'
            END                                                   AS season,
            market_segment,
            COUNT(*)                                              AS stays,
            ROUND(AVG(adr), 2)                                    AS avg_daily_rate
        FROM silver.hotels
        WHERE is_valid_booking AND NOT is_canceled
        GROUP BY hotel, season, market_segment
        HAVING COUNT(*) >= 30
        ORDER BY hotel, season, avg_daily_rate DESC
    """,
    # Q3: Which booking types cancel the most?
    "cancellation_by_segment": """
        SELECT
            market_segment,
            deposit_type,
            COUNT(*)                                              AS bookings,
            COUNT(*) FILTER (WHERE is_canceled)                   AS cancellations,
            ROUND(COUNT(*) FILTER (WHERE is_canceled) * 1.0 / COUNT(*), 3)
                                                                  AS cancellation_rate
        FROM silver.hotels
        WHERE is_valid_booking
        GROUP BY market_segment, deposit_type
        HAVING COUNT(*) >= 100
        ORDER BY cancellation_rate DESC
    """,
    # Q4: How do rate and cancellations change with how far ahead people book?
    "lead_time_buckets": """
        SELECT
            CASE
                WHEN lead_time <= 7   THEN '1. 0-7 days'
                WHEN lead_time <= 30  THEN '2. 8-30 days'
                WHEN lead_time <= 90  THEN '3. 31-90 days'
                WHEN lead_time <= 180 THEN '4. 91-180 days'
                ELSE                       '5. 181+ days'
            END                                                   AS lead_time_bucket,
            COUNT(*)                                              AS bookings,
            ROUND(AVG(adr) FILTER (WHERE NOT is_canceled), 2)     AS avg_daily_rate,
            ROUND(COUNT(*) FILTER (WHERE is_canceled) * 1.0 / COUNT(*), 3)
                                                                  AS cancellation_rate
        FROM silver.hotels
        WHERE is_valid_booking
        GROUP BY lead_time_bucket
        ORDER BY lead_time_bucket
    """,
}


def build_gold() -> dict:
    con = duckdb.connect(DB_PATH)
    con.execute("CREATE SCHEMA IF NOT EXISTS gold")
    counts = {}
    for name, sql in TABLES.items():
        con.execute(f"CREATE OR REPLACE TABLE gold.{name} AS {sql}")
        counts[name] = con.execute(f"SELECT COUNT(*) FROM gold.{name}").fetchone()[0]
        print(f"gold.{name}: {counts[name]:,} rows")
    con.close()
    return counts


if __name__ == "__main__":
    build_gold()
