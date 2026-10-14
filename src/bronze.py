"""Step 2: BRONZE. Load the raw file into DuckDB with no cleaning.

Bronze rule: keep the data exactly as it arrived. Cleaning happens in silver.
"""
import duckdb

DB_PATH = "data/warehouse.duckdb"
RAW_PATH = "data/raw/hotels.csv"


def build_bronze() -> int:
    con = duckdb.connect(DB_PATH)
    con.execute("CREATE SCHEMA IF NOT EXISTS bronze")
    # all_varchar keeps every column as text, so nothing is changed or dropped
    con.execute(
        f"""
        CREATE OR REPLACE TABLE bronze.hotels AS
        SELECT *, CAST(current_timestamp AS TIMESTAMP) AS _loaded_at
        FROM read_csv_auto('{RAW_PATH}', all_varchar=true)
        """
    )
    rows = con.execute("SELECT COUNT(*) FROM bronze.hotels").fetchone()[0]
    print(f"bronze.hotels loaded: {rows:,} rows")
    con.close()
    return rows


if __name__ == "__main__":
    build_bronze()
