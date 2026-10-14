"""Run the whole pipeline with one command:

    py -3.13 run_pipeline.py

Order: extract -> bronze -> silver -> gold -> quality checks.
Add --skip-download to reuse the raw file you already downloaded.
"""
import sys
from src.extract import extract, RAW_PATH
from src.bronze import build_bronze
from src.silver import build_silver
from src.gold import build_gold
from src.quality_checks import run_checks


def main() -> int:
    if "--skip-download" in sys.argv and RAW_PATH.exists():
        print("1/5 Extract: skipped (using existing file)")
    else:
        print("1/5 Extract")
        extract()
    print("2/5 Bronze")
    build_bronze()
    print("3/5 Silver")
    build_silver()
    print("4/5 Gold")
    build_gold()
    print("5/5 Quality checks")
    if not run_checks():
        print("Pipeline finished, but quality checks FAILED.")
        return 1
    print("Pipeline finished. All quality checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
