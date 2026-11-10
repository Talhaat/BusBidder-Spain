# File for the custom error types used when the csv data is invalid

class DataError(Exception):
    # Base class: every error below is a DataError
    pass

class MissingValueError(DataError):
    # A required field that is empty, like a row with no company name
    pass

class NegativePriceError(DataError):
    # A price below zero, like min_price = -5
    pass

class InvalidPriceRangeError(DataError):
    # A min_price higher than the max_price, like 30 and 20
    pass

class InvalidTimeError(DataError):
    # A time that does not exist or is not written as HH:MM, like 24:00 or 0600
    pass

class InvalidBusCountError(DataError):
    # A number of buses per day below 1, like 0 or -2
    pass

class InvalidSpeedError(DataError):
    # A bus speed of zero or below, like 0 or -50 km/h
    pass

class UnknownDestinationError(DataError):
    # A destination name that is not in destination.csv, like "Madird"
    pass

class InvalidDateError(DataError):
    # A date that does not exist or has the wrong format, like 2026-07-32
    pass

class ArrivalBeforeDepartureError(DataError):
    # An arrival time earlier than the departure time on the same trip
    pass

class InvalidRatingError(DataError):
    # A customer rating outside the chosen scale, like 7 on a 1-5 scale
    pass

class NoSeatsError(DataError):
    # An offer with zero or fewer available seats
    pass
