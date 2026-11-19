# Test to check for normal, invalid, missing-data and boundary cases

import csv
import os
import sys
from datetime import datetime

# Let Python find the program code in the busbidder/ folder
tests_folder = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(tests_folder, "..", "busbidder"))

import booking
import validation
from exceptions import DataError, MissingFileError, NoSeatsError, InvalidBookingError
from models import Company, Profile, Offer, load_companies

data_folder = os.path.join(tests_folder, "data")
app_data_folder = os.path.join(tests_folder, "..", "data")

# Every csv check is saved here with date and time, new rows are added on each run
check_log_path = os.path.join(data_folder, "testlog.csv")

# Clean copies of the invalid_ files (bad rows removed) are written here as check_valid_<file>
data_check_folder = os.path.join(tests_folder, "data_check")

# Cities the test offers may use, together with the test SolRuta from make_test_companies()
test_places = ["Madrid", "Zaragoza"]

data_files = [
    ["destination.csv", "destination", ""],
    ["company_profile.csv", "company", ""],
    ["bus_connections.csv", "company", "destinations"],
    ["map_destination.csv", "destination", ""],
    ["destination_profile.csv", "destination", "categories"],
    ["offers.csv", "offer_id", ""],
    ["traveller_profile.csv", "profile", ""],
]

#---------------------------DATA CSV FILES-------------------------------------------

# One problem per row
def name_problems(path, column):
    problems = []
    seen = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get(column) or "").strip()
            if name == "":
                problems.append((reader.line_num, name, f"{column} is empty"))
            elif name in seen:
                problems.append((reader.line_num, name, f"listed twice (first on line {seen[name]})"))
            else:
                seen[name] = reader.line_num
    return problems

# One problem per item that is repeated
def list_problems(path, name_column, list_column):
    problems = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get(name_column) or "").strip()
            seen = []
            for item in (row.get(list_column) or "").split(";"):
                item = item.strip()
                if item in seen:
                    problems.append((reader.line_num, name, f"'{item}' is listed twice in {list_column}"))
                else:
                    seen.append(item)
    return problems

# All duplicate and empty problems in one csv file
def file_problems(path, unique_column, list_column):
    problems = name_problems(path, unique_column)
    if list_column:
        problems = problems + list_problems(path, unique_column, list_column)
    problems.sort()
    return problems

# One problem per company row that validation rejects
def company_row_problems(path):
    problems = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                validation.validate_company_row(row)
            except (DataError, ValueError) as error:
                problems.append((reader.line_num, row.get("company") or "", str(error)))
    return problems

# Own test SolRuta with 15 seats, so the offer tests do not depend on data/company_profile.csv
def make_test_companies():
    profile = Profile("Test company", 10, 25, 360, 840, 20, 70, 15, 0, 0, 3.8, 0, 0)
    return {"SolRuta": Company("SolRuta", profile, 1)}

# One problem per offer row
def offer_row_problems(path):
    companies = make_test_companies()
    problems = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                validation.validate_offer_row(row, companies, test_places)
            except (DataError, ValueError) as error:
                problems.append((reader.line_num, row.get("offer_id") or "", str(error)))
    return problems

# One problem per traveller profile row 
def profile_row_problems(path, places):
    problems = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                validation.validate_profile_row(row, places)
            except (DataError, ValueError) as error:
                problems.append((reader.line_num, row.get("profile") or "", str(error)))
    return problems

# Madrid and every city in destination.csv
def real_places():
    places = ["Madrid"]
    with open(os.path.join(app_data_folder, "destination.csv"), newline="") as f:
        for row in csv.DictReader(f):
            places.append(row["destination"])
    return places

# One row per problem,
def save_check(file_name, problems):
    new_file = not os.path.exists(check_log_path)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(check_log_path, "a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["time", "file", "line", "name", "problem"])
        if not problems:
            writer.writerow([time, file_name, "", "", "OK"])
        for line, name, problem in problems:
            writer.writerow([time, file_name, line, name, problem])

def show(file_name, problems):
    lines = []
    for line, name, problem in problems:
        if line == "":
            lines.append(f"{file_name}: {problem}")
        else:
            lines.append(f"{file_name} line {line}: '{name}' {problem}")
    return lines

# Every invalid_ file is broken on purpose
def test_check_finds_problems():
    for file_name, unique_column, list_column in data_files:
        invalid_name = "invalid_" + file_name
        problems = file_problems(os.path.join(data_folder, invalid_name), unique_column, list_column)
        save_check(invalid_name, problems)
        for text in show(invalid_name, problems):
            print(text)
        # A broken file where the check finds nothing means the check (or the file) is wrong
        assert problems != [], f"{invalid_name}: the check found no problems"
    print("Duplicate check passed on all invalid_ test files")

# The real data files after datagen.py
def test_data_files():
    texts = []
    for file_name, unique_column, list_column in data_files:
        path = os.path.join(app_data_folder, file_name)
        if not os.path.exists(path) and file_name == "traveller_profile.csv":
            save_check(file_name, [("", "", "not there - optional, only Custom search")])
            continue
        if not os.path.exists(path):
            problems = [("", "", "file is missing - run datagen.py first")]
        else:
            problems = file_problems(path, unique_column, list_column)
            if file_name == "company_profile.csv":
                problems = problems + company_row_problems(path)
            if file_name == "traveller_profile.csv":
                problems = problems + profile_row_problems(path, real_places())
        # Saved before the assert, so a failing run is in the file too
        save_check(file_name, problems)
        texts = texts + show(file_name, problems)
    assert texts == [], "problems in the data files:\n" + "\n".join(texts)
    print("Data files passed:", len(data_files), "files in data/")

#---------------------------CLEAN COPIES-------------------------------------------

# Empty and duplicate names, plus the app's own validation for companies and offers
def problems_to_remove(path, file_name, unique_column, list_column):
    problems = file_problems(path, unique_column, list_column)
    if file_name == "company_profile.csv":
        problems = problems + company_row_problems(path)
    if file_name == "offers.csv":
        problems = problems + offer_row_problems(path)
    if file_name == "traveller_profile.csv":
        problems = problems + profile_row_problems(path, test_places)
    problems.sort()
    return problems

# Copies every row except the bad lines, returns (rows kept, rows in the file)
def write_clean_copy(path, clean_path, bad_lines):
    rows = []
    total = 0
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        for row in reader:
            total += 1
            if reader.line_num not in bad_lines:
                rows.append(row)
    with open(clean_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return len(rows), total

# Bad rows are removed from every invalid_ file, the rest is saved as tests/data_check/check_valid_<file>
def test_clean_copies():
    os.makedirs(data_check_folder, exist_ok=True)
    for file_name, unique_column, list_column in data_files:
        path = os.path.join(data_folder, "invalid_" + file_name)
        bad_lines = []
        for line, name, problem in problems_to_remove(path, file_name, unique_column, list_column):
            if line not in bad_lines:
                bad_lines.append(line)

        clean_name = "check_valid_" + file_name
        clean_path = os.path.join(data_check_folder, clean_name)
        kept, total = write_clean_copy(path, clean_path, bad_lines)
        note = f"kept {kept} of {total} rows, removed lines {bad_lines}"
        save_check(clean_name, [("", "", note)])
        print(f"{clean_name}: {note}")

        # The clean copy must have no problems left
        left = problems_to_remove(clean_path, file_name, unique_column, list_column)
        assert left == [], f"{clean_name} still has problems: {left}"
    print("Clean copies passed: saved in tests/data_check/")

#---------------------------VALIDATION-------------------------------------------

# Each row says what should happen in "expected": OK or the name of the error
def check_rows(path, validate):
    counts = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                validate(row)
                result = "OK"
            except (DataError, ValueError) as error:
                result = type(error).__name__
            assert result == row["expected"], f"{os.path.basename(path)} line {reader.line_num} ({row['description']}): expected {row['expected']}, got {result}"
            counts[row["case"]] = counts.get(row["case"], 0) + 1
    return counts

def test_company_rows():
    path = os.path.join(data_folder, "invalid_company_profile.csv")
    counts = check_rows(path, validation.validate_company_row)
    print("Company rows passed:", counts)

def test_offer_rows():
    companies = make_test_companies()
    path = os.path.join(data_folder, "invalid_offers.csv")
    counts = check_rows(path, lambda row: validation.validate_offer_row(row, companies, test_places))
    print("Offer rows passed:", counts)

#---------------------------MISSING FILES-------------------------------------------

# A base csv file that does not exist must give MissingFileError, not a crash
def test_missing_file():
    try:
        load_companies(os.path.join(data_folder, "does_not_exist.csv"))
        assert False, "a missing file should raise MissingFileError"
    except MissingFileError:
        pass
    print("Missing file passed")

#---------------------------BOOKING-------------------------------------------

# Two test buses (2 seats and 1 seat) and a transfer made of both, nothing is read from data/
def make_test_offers():
    solruta = make_test_companies()["SolRuta"]
    first = Offer("SOL-00001", [solruta], "Zaragoza", "Madrid", 360, 460, 14.2, False, False, 2)
    second = Offer("SOL-00002", [solruta], "Madrid", "Toledo", 480, 540, 9.5, True, True, 1)
    transfer = Offer("SOL-00001+SOL-00002", [solruta, solruta], "Zaragoza", "Toledo", 360, 540, 23.7, False, False, 1, 20)
    offers_by_id = {"SOL-00001": first, "SOL-00002": second}
    return first, second, transfer, offers_by_id

# Only in memory: book() never writes bookings.csv, the GUI saves with loader.save_booking
def test_booking():
    first, second, transfer, offers_by_id = make_test_offers()
    bookings = []

    direct = booking.book(first, "Budget", bookings, offers_by_id)
    assert first.seats == 1, "a direct booking takes one seat"
    assert validation.booking_ref_pattern.fullmatch(direct.reference), f"bad reference {direct.reference}"
    assert direct.changeable == first.changeable and direct.refundable == first.refundable, "fare conditions are stored"

    both = booking.book(transfer, "Budget", bookings, offers_by_id)
    assert first.seats == 0 and second.seats == 0 and transfer.seats == 0, "a transfer takes a seat on both buses"
    assert both.reference != direct.reference, "every booking gets its own reference"

    try:
        booking.book(first, "Budget", bookings, offers_by_id)
        assert False, "a full bus must give NoSeatsError"
    except NoSeatsError:
        pass
    assert len(bookings) == 2, "the failed booking is not added"
    print("Booking passed: seats, transfer, references, full bus")

# At startup the saved bookings take their seats off; one that does not fit is skipped
def test_apply_bookings():
    first, second, transfer, offers_by_id = make_test_offers()
    bookings = []
    booking.book(first, "Budget", bookings, offers_by_id)
    booking.book(transfer, "Budget", bookings, offers_by_id)

    # Fresh offers, like the next time the app starts
    first, second, transfer, offers_by_id = make_test_offers()
    kept = booking.apply_bookings(bookings, offers_by_id)
    assert first.seats == 0 and second.seats == 0, "saved bookings take their seats off"
    assert len(kept) == 2

    first, second, transfer, offers_by_id = make_test_offers()
    second.seats = 0
    kept = booking.apply_bookings(bookings, offers_by_id)
    assert len(kept) == 1 and first.seats == 1, "a booking on a bus with no seats left is skipped"
    print("Apply bookings passed")

# The app's own check for rows in bookings.csv
def test_booking_rows():
    offers_by_id = make_test_offers()[3]
    row = {"reference": "BB-00001", "time": "2026-11-18 13:10", "offer_id": "SOL-00001+SOL-00002", "profile": "Budget", "seats": "1", "price": "23.7", "changeable": "False", "refundable": "False", "payment": "paid (simulated)"}
    validation.validate_booking_row(row, offers_by_id)

    bad_rows = [
        ["reference", "BB-1", InvalidBookingError],
        ["reference", "XBB-00001", InvalidBookingError],
        ["reference", "BB-20261118-0001", InvalidBookingError],
        ["offer_id", "SOL-99999", InvalidBookingError],
        ["seats", "0", DataError],
        ["seats", "one", ValueError],
        ["price", "", DataError],
    ]
    for column, value, error in bad_rows:
        broken = dict(row)
        broken[column] = value
        try:
            validation.validate_booking_row(broken, offers_by_id)
            assert False, f"{column} '{value}' should be rejected"
        except error:
            pass
    print("Booking rows passed")

if __name__ == "__main__":
    test_check_finds_problems()
    test_clean_copies()
    test_data_files()
    test_company_rows()
    test_offer_rows()
    test_missing_file()
    test_booking()
    test_apply_bookings()
    test_booking_rows()
    print("All tests passed")
