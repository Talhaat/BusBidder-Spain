# BusBidder Spain

Final project in ACIT4420 Problem-solving with scripting, OsloMet,  2026. A bus marketplace with 5 fictional companies and 15 destinations in Spain. The traveler sets must-haves and preferences, the program removes the offers that break a must-have, ranks the rest with a weighted score and lets the traveller book a seat.

## Prerequisites

- Python 3.14
- uv Python package and project manager
- customtkinter
- tkinter

## Install

```sh
git clone https://github.com/Talhaat/BusBidder-Spain.git
cd BusBidder-Spain
uv sync
```

## Usage

```sh
uv run main.py
```

## Run tests

```sh
uv run tests/test.py
```

## Reproduce the traveller profile results

```sh
uv run python tools/compare_profiles.py
```

Runs every profile in `data/traveller_profile.csv` and saves the results in `output/`. `data/bookings.csv` is not changed.

## Input files (data/)

| File | |
|---|---|
| `destination.csv`, `company_profile.csv` | Base data, needed to run |
| `traveller_profile.csv` | Optional, fills the Traveller profile dropdown |
| `bus_connections.csv`, `map_destination.csv`, `destination_profile.csv`, `offers.csv` | Generated if missing. Delete one to get new random data |
| `bookings.csv` | Saved bookings, written by the program |
| `error.csv` | Rows that failed validation |

The log file `busbidder.log` is written in the project folder.

## Data files
## Data files: what can be deleted

| File | Can be deleted? | What happens |
|---|---|---|
| `data/destination.csv`, `data/company_profile.csv` | No | Base data. The program stops with a message if one is missing |
| `data/traveller_profile.csv` | Yes | Written by hand, not made again. Only "Custom" is left in the search page |
| `data/destination_profile.csv` | Yes | Made again from the categories in `datagen.py` |
| `data/bus_connections.csv`, `data/map_destination.csv`, `data/offers.csv` | Only all together | New random routes, map and offers. Rankings will be different from the report |
| `data/bookings.csv` | Yes | All bookings are gone and every seat is free again |
| `data/error.csv`, `busbidder.log` | Yes | Made again when the program runs |
| `output/` files | Yes | Made again by `tools/compare_profiles.py` |
| `tests/data/testlog.csv`, `tests/data_check/` | Yes | Made again by `tests/test.py` |
| `tests/data/invalid_*.csv` | No | Input for the tests |

To make a new random setup:
1. Delete `bus_connections.csv`, `map_destination.csv`, `offers.csv` and `bookings.csv` in `data/`.
2. Run `uv run main.py`.
3. Open **Map** once, so the new map is saved to `map_destination.csv`.

## Known issue

On Ubuntu the GUI can be very slow because of ibus. Run `ibus restart` and start the program again.

## Author

Thomas Talha Løberg
