# Exceptions - custom error types for invalid data found in the csv files


#Base class for every data error. All errors below inherit from it,
#so one "except DataError" catches any of them, while tests can still check the exact type.
class DataError(Exception):
    pass


#A required field that is empty, like a row with no company name
class MissingValueError(DataError):
    pass


#A price below zero, like min_price = -5
class NegativePriceError(DataError):
    pass


#A min_price higher than the max_price, like 30 and 20
class InvalidPriceRangeError(DataError):
    pass


#A time that does not exist or is not written as HH:MM, like 24:00 or 0600
class InvalidTimeError(DataError):
    pass


#A number of buses per day below 1, like 0 or -2
class InvalidBusCountError(DataError):
    pass


#A bus speed of zero or below, like 0 or -50 km/h
class InvalidSpeedError(DataError):
    pass


#A destination name that is not in destination.csv, like "Madird"
class UnknownDestinationError(DataError):
    pass


#A date that does not exist or has the wrong format, like 2026-07-32
class InvalidDateError(DataError):
    pass


#An arrival time earlier than the departure time on the same trip
class ArrivalBeforeDepartureError(DataError):
    pass


#A customer rating outside the chosen scale, like 7 on a 1-5 scale
class InvalidRatingError(DataError):
    pass


#An offer with zero or fewer available seats
class NoSeatsError(DataError):
    pass
