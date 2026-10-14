"""Step 3: SILVER. Clean and standardize the bronze data.

Silver rules (each one is a decision you can explain in an interview):
  1. Give every column its proper type (bronze stored everything as text).
  2. Turn placeholder text like 'NULL' and 'NA' into real NULLs.
  3. Build a real arrival_date from the year, month name, and day columns.
  4. Add helper columns: total_nights and estimated_revenue (adr x nights).
  5. FLAG bad rows instead of deleting them, so nothing silently disappears.
     Gold decides which flagged rows to leave out.
"""
import duckdb

DB_PATH = "data/warehouse.duckdb"

SILVER_SQL = """
CREATE OR REPLACE TABLE silver.hotels AS
WITH typed AS (
    SELECT
        hotel,
        CAST(is_canceled AS INTEGER) = 1                     AS is_canceled,
        CAST(lead_time AS INTEGER)                           AS lead_time,
        CAST(arrival_date_year AS INTEGER)                   AS arrival_year,
        arrival_date_month                                   AS arrival_month_name,
        CAST(arrival_date_day_of_month AS INTEGER)           AS arrival_day,
        CAST(stays_in_weekend_nights AS INTEGER)             AS weekend_nights,
        CAST(stays_in_week_nights AS INTEGER)                AS week_nights,
        CAST(adults AS INTEGER)                              AS adults,
        COALESCE(TRY_CAST(NULLIF(children, 'NA') AS INTEGER), 0) AS children,
        CAST(babies AS INTEGER)                              AS babies,
        NULLIF(country, 'NULL')                              AS country,
        market_segment,
        distribution_channel,
        CAST(is_repeated_guest AS INTEGER) = 1               AS is_repeated_guest,
        reserved_room_type,
        assigned_room_type,
        deposit_type,
        customer_type,
        CAST(adr AS DOUBLE)                                  AS adr,
        CAST(total_of_special_requests AS INTEGER)           AS special_requests,
        reservation_status,
        CAST(reservation_status_date AS DATE)                AS reservation_status_date
    FROM bronze.hotels
),
dated AS (
    SELECT *,
        make_date(
            arrival_year,
            CASE arrival_month_name
                WHEN 'January' THEN 1  WHEN 'February' THEN 2  WHEN 'March' THEN 3
                WHEN 'April' THEN 4    WHEN 'May' THEN 5       WHEN 'June' THEN 6
                WHEN 'July' THEN 7     WHEN 'August' THEN 8    WHEN 'September' THEN 9
                WHEN 'October' THEN 10 WHEN 'November' THEN 11 WHEN 'December' THEN 12
            END,
            arrival_day
        ) AS arrival_date,
        weekend_nights + week_nights AS total_nights
    FROM typed
)
SELECT
    * EXCLUDE (arrival_month_name),
    ROUND(adr * total_nights, 2)                     AS estimated_revenue,
    adr >= 0                                         AS has_valid_rate,
    (adults + children + babies) > 0                 AS has_guests,
    total_nights > 0                                 AS has_nights,
    (adr >= 0 AND (adults + children + babies) > 0 AND total_nights > 0)
                                                     AS is_valid_booking
FROM dated
"""


def build_silver() -> dict:
    con = duckdb.connect(DB_PATH)
    con.execute("CREATE SCHEMA IF NOT EXISTS silver")
    con.execute(SILVER_SQL)
    total, valid = con.execute(
        "SELECT COUNT(*), COUNT(*) FILTER (WHERE is_valid_booking) FROM silver.hotels"
    ).fetchone()
    print(f"silver.hotels built: {total:,} rows, {valid:,} valid, {total - valid:,} flagged")
    con.close()
    return {"total": total, "valid": valid}


if __name__ == "__main__":
    build_silver()
