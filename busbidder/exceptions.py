# File for the custom error types used when the csv data is invalid


class DataError(Exception):
    pass

class MissingValueError(DataError):
    pass

class NegativePriceError(DataError):
    pass

class InvalidPriceRangeError(DataError):
    pass

class InvalidTimeError(DataError):
    pass

class InvalidBusCountError(DataError):
    pass

class InvalidSpeedError(DataError):
    pass

class UnknownDestinationError(DataError):
    pass

class InvalidDateError(DataError):
    pass

class ArrivalBeforeDepartureError(DataError):
    pass

class InvalidRatingError(DataError):
    pass

class NoSeatsError(DataError):
    pass

class InvalidSeatCountError(DataError):
    pass

class InvalidOfferIdError(DataError):
    pass

class UnknownCompanyError(DataError):
    pass

class InvalidFareError(DataError):
    pass

class InvalidLuggageError(DataError):
    pass

class MissingFileError(DataError):
    pass

class InvalidProfileError(DataError):
    pass

class InvalidBookingError(DataError):
    pass
