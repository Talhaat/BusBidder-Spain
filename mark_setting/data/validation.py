# Validation - checks rows from the csv files before they become objects

import re

from exceptions import MissingValueError, NegativePriceError, InvalidPriceRangeError, InvalidTimeError, InvalidBusCountError, InvalidSpeedError

#Regex for a time written as HH:MM, from 00:00 to 23:59
time_pattern = re.compile(r"^([01][0-9]|2[0-3]):[0-5][0-9]$")


#Function to check one row from company_profile.csv
# Input is a csv row dict, return is none.
# Raises a DataError subclass if the row is invalid, or ValueError if a number is not a number.
def validate_company_row(row):
    for column in ["company", "description", "min_price", "max_price", "start_time", "end_time", "buses_per_day", "speed_kmh"]:
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
