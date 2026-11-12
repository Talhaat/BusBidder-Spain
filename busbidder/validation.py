# File for checking csv rows before they become objects
#Check if empty, is a number, not negative, in min/max range, time valid, whole number.

import csv
import logging
import os
import re
from datetime import datetime

from exceptions import DataError, MissingValueError, NegativePriceError, InvalidPriceRangeError, InvalidTimeError, InvalidBusCountError, InvalidSpeedError, InvalidSeatCountError
from exceptions import InvalidOfferIdError, UnknownCompanyError, UnknownDestinationError, InvalidDateError, ArrivalBeforeDepartureError, InvalidFareError, InvalidRatingError

project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
error_path = os.path.join(project_folder, "data", "error.csv")

# Regex for a time written as HH:MM, from 00:00 to 23:59
time_pattern = re.compile(r"^([01][0-9]|2[0-3]):[0-5][0-9]$")

# Regex for an offer id: 3 capital letters and a 5 digit number, like SOL-00001
offer_id_pattern = re.compile(r"^[A-Z]{3}-\d{5}$")

# Columns in offers.csv, same order as Offer.to_row() in models.py
offer_columns = ["offer_id",
                 "company",
                 "start",
                 "finish",
                 "day",
                 "departure",
                 "duration",
                 "price",
                 "changeable",
                 "refundable",
                 "seats"]

def validate_company_row(row):
    for column in ["company", "description", "min_price", "max_price", "start_time", "end_time", "buses_per_day", "speed_kmh", "max_seats", "rating", "change", "refund"]:
        if not row.get(column):
            raise MissingValueError(f"'{column}' is missing")

    min_price = float(row["min_price"])
    max_price = float(row["max_price"])
    if min_price < 0 or max_price < 0:
        raise NegativePriceError(f"price is negative (min {min_price}, max {max_price})")
    if min_price > max_price:
        raise InvalidPriceRangeError(f"min_price {min_price} is higher than max_price {max_price}")

    for column in ["start_time", "end_time"]:
        if not time_pattern.match(row[column]):
            raise InvalidTimeError(f"{column} '{row[column]}' is not a valid HH:MM time")

    # int() also rejects text and decimals like "five" or "2.5" with a ValueError
    buses_per_day = int(row["buses_per_day"])
    if buses_per_day < 1:
        raise InvalidBusCountError(f"buses_per_day is {buses_per_day}, must be at least 1")

    speed_kmh = float(row["speed_kmh"])
    if speed_kmh <= 0:
        raise InvalidSpeedError(f"speed_kmh is {speed_kmh}, must be above 0")

    max_seats = int(row["max_seats"])
    if max_seats < 1:
        raise InvalidSeatCountError(f"max_seats is {max_seats}, must be at least 1")

    rating = float(row["rating"])
    if rating < 0 or rating > 5:
        raise InvalidRatingError(f"rating is {rating}, must be between 0 and 5")

    # change: 1 = tickets can be changed, 0 = they can't
    if row["change"] not in ["0", "1"]:
        raise InvalidFareError(f"change is '{row['change']}', must be 0 or 1")

    # refund: 1 = tickets can be refunded, 0 = they can't
    if row["refund"] not in ["0", "1"]:
        raise InvalidFareError(f"refund is '{row['refund']}', must be 0 or 1")

def validate_offer_row(row, companies, places):
    for column in offer_columns:
        if not row.get(column):
            raise MissingValueError(f"'{column}' is missing")

    if not offer_id_pattern.match(row["offer_id"]):
        raise InvalidOfferIdError(f"offer_id '{row['offer_id']}' does not look like SOL-00001")

    # companies is a dict: company name -> Company object
    if row["company"] not in companies:
        raise UnknownCompanyError(f"company '{row['company']}' is not in company_profile.csv")

    for column in ["start", "finish"]:
        if row[column] not in places:
            raise UnknownDestinationError(f"{column} '{row[column]}' is not Madrid or a destination")

    # Day of the week, 1 to 7; int() rejects text and decimals with a ValueError
    day = int(row["day"])
    if day < 1 or day > 7:
        raise InvalidDateError(f"day is {day}, must be 1 to 7")

    if not time_pattern.match(row["departure"]):
        raise InvalidTimeError(f"departure '{row['departure']}' is not a valid HH:MM time")

    # Duration in minutes: 0 or less would mean arriving before (or when) the bus leaves
    duration = int(row["duration"])
    if duration <= 0:
        raise ArrivalBeforeDepartureError(f"duration is {duration}, must be above 0")

    price = float(row["price"])
    if price < 0:
        raise NegativePriceError(f"price is negative ({price})")

    for column in ["changeable", "refundable"]:
        if row[column] not in ["True", "False"]:
            raise InvalidFareError(f"{column} '{row[column]}' must be True or False")

    # 0 seats is allowed: the bus is full, the filter removes it later
    seats = int(row["seats"])
    if seats < 0:
        raise InvalidSeatCountError(f"seats is {seats}, can't be below 0")
    max_seats = companies[row["company"]].profile.max_seats
    if seats > max_seats:
        raise InvalidSeatCountError(f"seats is {seats}, more than {row['company']}'s max_seats {max_seats}")

def save_error(error, file, line, row):
    new_file = not os.path.exists(error_path)
    with open(error_path, "a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["file", "line", "company", "error"])
        writer.writerow([file, line, row.get("company"), error])

