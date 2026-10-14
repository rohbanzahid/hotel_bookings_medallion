# Hotel Bookings: Bronze, Silver, Gold Pipeline

A small personal project that builds a medallion-style data pipeline on a public
hotel bookings dataset (about 119,000 bookings from two hotels).

## Status
- [x] Extract: download the raw file
- [x] Bronze: load raw data unchanged
- [x] Silver: clean and standardize
- [ ] Gold: business-ready tables
- [ ] Data quality tests
- [ ] One-command run

## How to run
```
pip install -r requirements.txt
python src/extract.py
python src/bronze.py
```

## Data
Hotel Booking Demand dataset, published via TidyTuesday (2020-02-11).
