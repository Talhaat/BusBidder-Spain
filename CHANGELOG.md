# Changelog

Entries added as work happens, newest within each section at the top.

## Data files
- `destination.csv` — the 15 official destinations (from the assignment PDF).
- `company_profile.csv` — 5 companies, description, and a `min_price`/`max_price` range each.
- `map_destination.csv` — (x, y) position per destination for the map. Random on first run, then saved and reused.
- `bus_connections.csv` — which destinations each company serves. Random on first run (count per company set in `destination_counts`, forced picks in `custom_destinations`), then saved and reused.
- `destination_profile.csv` — category tags per destination (major city, coastal, beach, etc.), from the `destination_categories` dict in `datagen.py`.

## models.py
- `Destination` — name + categories list. `from_dict()` classmethod, `to_row()` for CSV.
- `Company` — name, `Profile`, ID. `Profile` — description + price range + `random_price()`.
- `load_destinations()` / `load_companies()` — build these objects straight from the CSVs.

## Layout fix
- `bus_gui.py`'s Start/Finish dropdowns are now side by side (were stacked vertically), with a "→" arrow label between them, using a row frame containing two column frames.

## Start/finish routing (new)
- `price.get_route_options(start, finish, ...)` — journeys between any two points, not just from Madrid. Madrid stays the hub: a Madrid-involved journey is a direct leg (reuses `get_options`), any other pair routes through Madrid (start → Madrid → finish), only counting companies that serve both ends, summing their two leg prices.
- `bus_gui.py`'s search page now has two dropdowns (Start, defaults to Madrid; Finish) instead of one, both listing Madrid + all 15 destinations.

## main.py + GUI app (new)
- `main.py` (repo root) is now the real entry point: sets up `sys.path` to reach `mark_setting/data/`, then calls `gui.bus_gui.run()`.
- `datagen.py` refactored: `generate_data()` now loads/generates everything and returns it as a dict, instead of auto-opening the map. Still runnable standalone (`python3 datagen.py` opens the map directly) via `if __name__ == "__main__":`.
- New `gui/` package (`mark_setting/data/gui/`): `map_view.py` (moved here, unchanged) and `bus_gui.py` (new) — a sidebar app with "Map" (opens the existing map window) and "Bus Search" (destination dropdown → shows company/price options via `price.get_options`).
- Known leftovers not yet cleaned up: old empty `mark_setting/data/GUI/bus_gui.py` (capital-G, superseded by lowercase `gui/`), and `mark_setting/data/map_destination/positions.csv` (stray folder from an earlier approach).

## price.py (new)
- `calculate_price(destination, served_destinations, coordinates, madrid_x, madrid_y, min_price, max_price)` — scales a destination's price linearly between a company's min and max price, based on how long that route is relative to the shortest/longest route *that company* runs. Shortest route = min_price, longest = max_price.
- `get_options(destination, connections, coordinates, madrid_x, madrid_y, companies)` — returns every (company, price) pair for a given destination, by calling `calculate_price` once per company that serves it.
- Not wired into `datagen.py` yet. Needs `companies` to be full `Company` objects (`models.load_companies()`, not `loader.load_companies()` which only returns name strings) to access `.profile.min_price`/`.max_price`.

## Module split
`datagen.py` was one 337-line file; split into 4 modules by responsibility, matching the project's "multiple modules" requirement:
- `loader.py` — all CSV reading/writing (the load-if-exists-else-generate-and-save functions)
- `routes.py` — `minimum_spanning_tree()`, `assign_unassigned_destinations()` (pure algorithm, no I/O/drawing)
- `map_view.py` — `show_map()`, the tkinter/customtkinter window, drawing and hover highlighting
- `datagen.py` — now just a 77-line orchestrator: config dicts + calls into the above

## datagen.py (history, now split across the files above)
- Destinations no company serves (random generation doesn't guarantee full coverage) now get auto-assigned to whichever company has the nearest point (Madrid or one of its existing destinations), via `assign_unassigned_destinations()`. Runs before the drawing loop so it actually affects the map.
- Routes are now drawn as a minimum spanning tree per company (Madrid + its destinations), instead of connecting them in CSV list order — lines take the shortest sensible path instead of jumping around the map. `minimum_spanning_tree()` is a small Prim's implementation using `math.dist`, fine at this scale (max 9 points per company).
- Fixed route hover only highlighting the nearest segments instead of the whole route: lines carried both a company tag and bare station-name tags, so hovering a line fired both `highlight_route` and `highlight_station`, and the station one ran last and won. Lines now use separate `touch-<name>` tags (lookup only, never bound to events) so the two hovers can't interfere.
- Hovering a destination dot (or Madrid) highlights every line directly touching that station and dims the rest.
- Hovering a bus route highlights it (thicker, raised above other lines) and dims every other route (thinner, grey). Each line segment is tagged by company so the whole route reacts, not just the segment under the cursor.
- Generates/loads all the CSVs above (load-if-exists-else-generate-and-save pattern, same for each file).
- Opens a map window: Madrid as a fixed hub in the center, one destination dot per city, one colored connected route per company (like a tram line) passing through its destinations in order.
- Styled with `customtkinter` (dark mode) — window and background only; the map itself is still a plain `tk.Canvas`, since customtkinter has no canvas widget.

## debug.py
- `find_unused_destinations()` — compares `destination.csv` against `bus_connections.csv`, prints any destination no company serves.

## GitHub
- Pushed to `github.com/Talhaat/BusBidder-Spain`.
- Only one commit so far ("Start, data generation, map") — everything above this line in the changelog is **not committed yet**.

## Known issues / not done yet
- No `offers` dataset — the actual priced, scheduled bus tickets (PDF's "Offer information": date, times, duration, price, transfers, luggage, changeability, refundability, seats, rating). This is the biggest missing piece.
- The real BusBidder application (filtering, ranking, booking, traveller profiles) hasn't been started — everything so far is data generation + a map visualization.
- Stray leftovers to clean up: a file/folder named `-1`, and an old `map_destination/positions.csv` left over from an earlier approach (current data lives in `map_destination.csv` instead).
- `mark_setting/` folder name was discussed for renaming but never actually changed.
