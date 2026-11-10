# BusBidder Spain - design sketch

Working plan for the classes. Update it when the code changes. At the end it becomes
the Task 1 section of the report (class diagram + justification).

## Classes

| Class | Responsibility | Holds / uses | Status |
|---|---|---|---|
| `Company` | prices trips on its own route tree (`price_between`) | has a `Profile`, list of its destinations | done |
| `Profile` | description, price range, time window, buses per day, speed; answers `runs_at`, makes `departure_times()`, `minutes_until_next_bus()` | - | done |
| `Destination` | name + categories (coastal, historic, ...) | - | exists, not used yet |
| `Offer` | one trip a traveller can buy | one or two `Company` objects, start, finish, price, transfers, departure, arrival, wait in Madrid | done, needs date, seats, flexibility |
| `Marketplace` | holds everything, loads/creates offers | companies, destinations, offers | planned |
| `TravelRequest` | hard constraints: from, to, date, budget, max transfers | checks an `Offer` | planned |
| `TravellerProfile` | ranking weights (budget, business, flexible) | - | planned |
| `Ranker` | scores each criterion 0-100, applies weights, explains top offer | criteria registered with a decorator | planned |
| `Booking` | booking reference, seats, fare conditions, saved to file | one `Offer` | planned |

## How they work together

Marketplace -> offers -> TravelRequest removes unacceptable offers
-> Ranker sorts the rest with TravellerProfile weights -> user picks one -> Booking

## Open decisions

- Offers: generate once and save to `offers.csv`, then load + validate every run
  (recommended, matches Task 2), or keep calculating them live?
- `Marketplace` class goes in `busbidder/marketplace.py` (the old duplicate `Company` there was removed).

## Folders

| Folder | Holds |
|---|---|
| `main.py` | entry point: `uv run main.py` |
| `busbidder/` | all program code, `gui/` inside |
| `data/` | csv input files (`destination.csv`, `company_profile.csv`) and generated + saved files |
| `tests/` | automated tests (later) and `tests/data/` with deliberately broken csv files |
| `tools/` | `debug.py` for manual checks |
| `output/` | example output for the report: logs, rankings, screenshots |
| `report/` | this sketch, flowchart, tables |

## Build order

1. Task 2 basics: `exceptions.py`, logging, validate company + destination CSVs
   (done: exceptions, logging, company CSV + test file; left: destinations/connections)
2. `offers.csv`: generate, load, validate; `Offer` gets date, times, seats, flexibility
3. `Marketplace` class
4. Task 3: `TravelRequest` + filtering
5. Task 5: `Ranker` + decorator registry
6. Task 6: traveller profiles, explanation, `Booking`
7. Tests + README
8. Task 1 final: class diagram + justification
