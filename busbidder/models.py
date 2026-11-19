# File for the Profile, Company, Destination and Offer classes

import csv
import logging
import math
import os
import random

import price
import routes
import validation
from exceptions import DataError, MissingFileError
from timing import to_minutes, to_time_text, to_duration_text

logger = logging.getLogger(__name__)

# Map scale: one pixel on the 3000x2000 map canvas counts as this many km
km_per_pixel = 0.4

#---------------------------CLASSES/DICT-------------------------------------------

class Profile:
    def __init__(self, description, min_price, max_price, start_time, end_time, buses_per_day, speed_kmh, max_seats, luggage, luggage_price, rating, change, refund):
        self.description = description
        self.min_price = min_price
        self.max_price = max_price
        # Minutes after midnight, like 360 for 06:00
        self.start_time = start_time
        self.end_time = end_time
        self.buses_per_day = buses_per_day
        self.speed_kmh = speed_kmh
        self.max_seats = max_seats
        self.luggage = luggage
        self.luggage_price = luggage_price
        self.rating = rating
        self.change = change
        self.refund = refund


    # First bus at start_time, last bus at end_time, the rest evenly in between
    # Times are minutes after midnight, like 510 for 08:30
    def departure_times(self):
        start = self.start_time
        end = self.end_time
        window = (end - start) % (24 * 60)      # % makes overnight windows like 22:00-06:00 work too
        if self.buses_per_day == 1:
            return [start]
        gap = window / (self.buses_per_day - 1)
        times = []
        for number in range(self.buses_per_day):
            # % keeps buses after midnight between 0 and 1439
            times.append(round(start + number * gap) % (24 * 60))
        return times

    def min_til_next_bus(self, start_min):
        return min((time - start_min) % (24 * 60) for time in self.departure_times())
    
class Company:
    def __init__(self, name, profile, ID):
        self.name = name
        self.profile = profile
        self.ID = ID
        self.destinations = []

    def price_between(self, start, finish, coordinates, madrid_x, madrid_y):
        # This company doesn't stop at both points
        if start != "Madrid" and start not in self.destinations:
            return None
        if finish != "Madrid" and finish not in self.destinations:
            return None

        points, edges = self.route_tree(coordinates, madrid_x, madrid_y)
        distance = price.path_distance(start, finish, points, edges)

        edge_distances = [math.dist(points[a], points[b]) for a, b in edges]
        min_distance = min(edge_distances)
        max_distance = sum(edge_distances)  # longest possible path: the whole tree

        return price.price_from_distance(
            distance, min_distance, max_distance,
            self.profile.min_price, self.profile.max_price
        )

    def route_tree(self, coordinates, madrid_x, madrid_y):
        points = {"Madrid": (madrid_x, madrid_y)}
        for destination in self.destinations:
            points[destination] = coordinates[destination]
        return points, routes.minimum_spanning_tree(points)

    def travel_min(self, start, finish, coordinates, madrid_x, madrid_y):
        points, edges = self.route_tree(coordinates, madrid_x, madrid_y)
        km = price.path_distance(start, finish, points, edges) * km_per_pixel
        return round(km / self.profile.speed_kmh * 60)
    
class Destination:
    def __init__(self, name, categories):
        self.name = name
        self.categories = categories

    # Build a Destination from a csv row dict
    @classmethod
    def from_dict(cls, data):
        categories = data["categories"].split(";") if data["categories"] else []
        return cls(data["destination"], categories)

    def to_row(self):
        return [self.name, ";".join(self.categories)]

class TravellerProfile:
    def __init__(self, name, description, start, finish, time, luggage, change, refund, min_rating, max_price, max_hours, min_score, importance):
        self.name = name
        self.description = description
        self.start = start
        self.finish = finish
        self.time = time
        # Must have boxes: True = ticked
        self.luggage = luggage
        self.change = change
        self.refund = refund
        # Kept as text, they are dropdown choices like "Any" or "40"
        self.min_rating = min_rating
        self.max_price = max_price
        self.max_hours = max_hours
        self.min_score = min_score
        # Preferences: criterion name -> importance 0-10, the same names as the ranking registry
        self.importance = importance

    # Build a TravellerProfile from a csv row dict
    @classmethod
    def from_dict(cls, data):
        importance = {}
        for name in ["price", "duration", "dep_time", "flexibility"]:
            importance[name] = int(data[name])
        return cls(
            data["profile"],
            data["description"],
            data["start"],
            data["finish"],
            data["time"],
            data["luggage"] == "1",
            data["change"] == "1",
            data["refund"] == "1",
            data["min_rating"],
            data["max_price"],
            data["max_hours"],
            data["min_score"],
            importance
        )

class Booking:
    def __init__(self, reference, time, offer_id, profile, seats, price, changeable, refundable, payment):
        self.reference = reference
        self.time = time
        # One offer id for a direct bus, two joined with + for a transfer
        self.offer_id = offer_id
        self.profile = profile
        self.seats = seats
        self.price = price
        # Fare conditions are stored with the booking, like the spec asks
        self.changeable = changeable
        self.refundable = refundable
        self.payment = payment

    # Build a Booking from a csv row dict
    @classmethod
    def from_dict(cls, data):
        return cls(
            data["reference"],
            data["time"],
            data["offer_id"],
            data["profile"],
            int(data["seats"]),
            float(data["price"]),
            data["changeable"] == "True",
            data["refundable"] == "True",
            data["payment"]
        )

    def to_row(self):
        return [
            self.reference,
            self.time,
            self.offer_id,
            self.profile,
            self.seats,
            self.price,
            self.changeable,
            self.refundable,
            self.payment
        ]

#---------------------------CLASSES/DICT-------------------------------------------

def load_destinations(path):
    destinations = []
    with open(path, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            destinations.append(Destination.from_dict(row))
    return destinations

def load_companies(path):
    # company_profile.csv is base data: it can't be generated, so stop with a clear error
    if not os.path.exists(path):
        raise MissingFileError(f"{os.path.basename(path)} is missing from the data folder")
    companies = []
    with open(path, newline="") as file:
        reader = csv.DictReader(file)
        for index, row in enumerate(reader, start=1):
            # Bad rows are logged and skipped, the rest of the file still loads
            try:
                validation.validate_company_row(row)
            except (DataError, ValueError) as error:
                logger.warning(f"{os.path.basename(path)} line {reader.line_num}: rejected {row.get('company')!r}: {error}")
                validation.save_error(error, os.path.basename(path), reader.line_num, row)
                continue
            profile = Profile(row["description"], 
                            float(row["min_price"]), 
                            float(row["max_price"]), 
                            to_minutes(row["start_time"]), to_minutes(row["end_time"]),
                            int(row["buses_per_day"]), 
                            float(row["speed_kmh"]), 
                            int(row["max_seats"]), 
                            int(row["luggage"]), 
                            float(row["luggage_price"]), 
                            float(row["rating"]),
                            int(row["change"]),
                            int(row["refund"])
                            )
                            

            companies.append(Company(row["company"], profile, index))
    logger.info(f"Loaded {len(companies)} companies from {os.path.basename(path)}")
    return companies


#---------------------------OFFERS-------------------------------------------

class Offer:
    def __init__(self, offer_id, companies, start, finish, departure, arrival, price, changeable, refundable, seats, wait=0):
        self.offer_id = offer_id
        # One company for a direct bus, two for a transfer via Madrid
        self.companies = companies
        self.start = start
        self.finish = finish
        # Minutes since the start of the week, like 3390 for day 3 at 08:30
        self.departure = departure
        self.arrival = arrival
        self.price = price
        self.changeable = changeable
        self.refundable = refundable
        self.seats = seats
        self.transfers = len(companies) - 1
        self.wait = wait  # minutes waiting in Madrid, 0 for a direct bus

    @classmethod
    def from_dict(cls, data, companies):
        day = int(data["day"])
        departure = (day - 1) * 24 * 60 + to_minutes(data["departure"])
        arrival = departure + int(data["duration"])
        return cls(
            data["offer_id"],
            [companies[data["company"]]],
            data["start"],
            data["finish"],
            departure,
            arrival,
            float(data["price"]),
            data["changeable"] == "True",
            data["refundable"] == "True",
            int(data["seats"])
        )

    def to_row(self):
        day = self.departure // (24 * 60) + 1
        duration = self.arrival - self.departure
        return [
            self.offer_id,
            self.companies[0].name,
            self.start,
            self.finish,
            day,
            to_time_text(self.departure),
            duration,
            self.price,
            self.changeable,
            self.refundable,
            self.seats
        ]

    def __str__(self):
        if self.transfers == 0:
            route = self.companies[0].name
        else:
            route = f"{self.companies[0].name} -> Madrid (wait {to_duration_text(self.wait)}) -> {self.companies[1].name}"
        departs = to_time_text(self.departure)
        arrives = to_time_text(self.arrival)
        return f"{route}: {self.price} EUR, departs {departs}, arrives {arrives}, {self.seats} seats left"

