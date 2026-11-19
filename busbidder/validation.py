# File for checking csv rows before they become objects
#Check if empty, is a number, not negative, in min/max range, time valid, whole number.

import csv
import logging
import os
import re
from datetime import datetime

from exceptions import DataError, MissingValueError, NegativePriceError, InvalidPriceRangeError, InvalidTimeError, InvalidBusCountError, InvalidSpeedError, InvalidSeatCountError
from exceptions import InvalidOfferIdError, UnknownCompanyError, UnknownDestinationError, InvalidDateError, ArrivalBeforeDepartureError, InvalidFareError, InvalidRatingError
from exceptions import InvalidLuggageError, InvalidProfileError, InvalidBookingError

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

# Regex for a booking reference
booking_ref_pattern = re.compile(r"BB-\d{5}")

# Columns in bookings.csv
booking_columns = ["reference",
                   "time",
                   "offer_id",
                   "profile",
                   "seats",
                   "price",
                   "changeable",
                   "refundable",
                   "payment"]

# Choices in the search page dropdowns
hour_choices = [f"{hour:02d}:00" for hour in range(24)]
rating_choices = ["0", "1", "2", "3", "4", "5"]
price_choices = ["Any", "20", "30", "40", "60", "80"]
duration_choices = ["Any", "2", "4", "8", "12", "24"]
score_choices = [str(number) for number in range(11)]
importance_choices = [str(number) for number in range(11)]

# Columns in traveller_profile.csv
profile_columns = ["profile",
                   "description",
                   "start",
                   "finish",
                   "time",
                   "luggage",
                   "change",
                   "refund",
                   "min_rating",
                   "max_price",
                   "max_hours",
                   "min_score",
                   "price",
                   "duration",
                   "dep_time",
                   "flexibility"]

def validate_company_row(row):
    for column in ["company", "description", "min_price", "max_price", "start_time", "end_time", "luggage", "luggage_price", "buses_per_day", "speed_kmh", "max_seats", "rating", "change", "refund"]:
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

    # int also rejects text and decimals like "five" or "2.5" with a ValueError
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

    if row["change"] not in ["0", "1"]:
        raise InvalidFareError(f"change is '{row['change']}', must be 0 or 1")

    if row["refund"] not in ["0", "1"]:
        raise InvalidFareError(f"refund is '{row['refund']}', must be 0 or 1")

    if row["luggage"] not in ["0", "1"]:
        raise InvalidLuggageError(f"luggage is '{row['luggage']}', must be 0 or 1")
    luggage_price = float(row["luggage_price"])
    if luggage_price < 0:
        raise InvalidLuggageError(f"luggage_price is {luggage_price}, can't be below 0")

def validate_offer_row(row, companies, places):
    for column in offer_columns:
        if not row.get(column):
            raise MissingValueError(f"'{column}' is missing")

    if not offer_id_pattern.match(row["offer_id"]):
        raise InvalidOfferIdError(f"offer_id '{row['offer_id']}' does not look like SOL-00001")

    # companies is a dict
    if row["company"] not in companies:
        raise UnknownCompanyError(f"company '{row['company']}' is not in company_profile.csv")

    for column in ["start", "finish"]:
        if row[column] not in places:
            raise UnknownDestinationError(f"{column} '{row[column]}' is not Madrid or a destination")

    # Day of the week
    day = int(row["day"])
    if day < 1 or day > 7: 
        raise InvalidDateError(f"day is {day}, must be 1 to 7")

    if not time_pattern.match(row["departure"]):
        raise InvalidTimeError(f"departure '{row['departure']}' is not a valid HH:MM time")

    # Duration in minutes
    duration = int(row["duration"])
    if duration <= 0:
        raise ArrivalBeforeDepartureError(f"duration is {duration}, must be above 0")

    price = float(row["price"])
    if price < 0:
        raise NegativePriceError(f"price is negative ({price})")

    for column in ["changeable", "refundable"]:
        if row[column] not in ["True", "False"]:
            raise InvalidFareError(f"{column} '{row[column]}' must be True or False")

    # 0 seats is allowed
    seats = int(row["seats"])
    if seats < 0:
        raise InvalidSeatCountError(f"seats is {seats}, can't be below 0")
    max_seats = companies[row["company"]].profile.max_seats
    if seats > max_seats:
        raise InvalidSeatCountError(f"seats is {seats}, more than {row['company']}'s max_seats {max_seats}")

def validate_profile_row(row, places):
    for column in profile_columns:
        if not row.get(column):
            raise MissingValueError(f"'{column}' is missing")

    for column in ["start", "finish"]:
        if row[column] not in places:
            raise UnknownDestinationError(f"{column} '{row[column]}' is not Madrid or a destination")
    if row["start"] == row["finish"]:
        raise InvalidProfileError(f"start and finish are both '{row['start']}'")

    # The search page only offers whole hours
    if row["time"] not in hour_choices:
        raise InvalidTimeError(f"time '{row['time']}' is not a whole hour like 08:00")

    # Must have boxes
    if row["luggage"] not in ["0", "1"]:
        raise InvalidLuggageError(f"luggage is '{row['luggage']}', must be 0 or 1")
    for column in ["change", "refund"]:
        if row[column] not in ["0", "1"]:
            raise InvalidFareError(f"{column} is '{row[column]}', must be 0 or 1")

    # Each limit must be a value its dropdown can show
    choices = {"min_rating": rating_choices, "max_price": price_choices, "max_hours": duration_choices, "min_score": score_choices}
    for column in choices:
        if row[column] not in choices[column]:
            raise InvalidProfileError(f"{column} is '{row[column]}', must be one of {' '.join(choices[column])}")

    total = 0
    for column in ["price", "duration", "dep_time", "flexibility"]:
        if row[column] not in importance_choices:
            raise InvalidProfileError(f"{column} importance is '{row[column]}', must be 0 to 10")
        total += int(row[column])
    if total == 0:
        raise InvalidProfileError("all four importances are 0")

def validate_booking_row(row, offers_by_id):
    for column in booking_columns:
        if not row.get(column):
            raise MissingValueError(f"'{column}' is missing")

    #The whole reference must have the format, not only the start
    if not booking_ref_pattern.fullmatch(row["reference"]):
        raise InvalidBookingError(f"reference '{row['reference']}' does not look like BB-00001")

    # A transfer is booked as both offer ids joined
    for offer_id in row["offer_id"].split("+"):
        if offer_id not in offers_by_id:
            raise InvalidBookingError(f"offer '{offer_id}' is not in offers.csv")

    seats = int(row["seats"])
    if seats < 1:
        raise InvalidSeatCountError(f"seats is {seats}, a booking needs at least 1")

    price = float(row["price"])
    if price < 0:
        raise NegativePriceError(f"price is negative ({price})")

    for column in ["changeable", "refundable"]:
        if row[column] not in ["True", "False"]:
            raise InvalidFareError(f"{column} '{row[column]}' must be True or False")

def save_error(error, file, line, row):
    new_file = not os.path.exists(error_path)
    with open(error_path, "a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["file", "line", "company", "error"])
        writer.writerow([file, line, row.get("company"), error])

