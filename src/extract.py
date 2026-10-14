"""Step 1: EXTRACT. Download the raw hotel bookings file, exactly as published."""
from pathlib import Path
import requests

URL = (
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/"
    "master/data/2020/2020-02-11/hotels.csv"
)
RAW_PATH = Path("data/raw/hotels.csv")


def extract() -> Path:
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(URL, timeout=60)
    response.raise_for_status()  # stop loudly if the download failed
    RAW_PATH.write_bytes(response.content)
    print(f"Downloaded {len(response.content):,} bytes to {RAW_PATH}")
    return RAW_PATH


if __name__ == "__main__":
    extract()
