# File for the Profile, Company and Destination classes

import csv
import logging
import math
import os
import random
from datetime import datetime

import price
import routes
import validation
from exceptions import DataError
from time_utils import to_minutes, to_time_text

logger = logging.getLogger(__name__)

# Map scale: one pixel on the 3000x2000 map canvas counts as this many km
km_per_pixel = 0.4

#---------------------------CLASSES/DICT-------------------------------------------

class Profile:
    def __init__(self, description, min_price, max_price, start_time, end_time, buses_per_day, speed_kmh):
        self.description = description
        self.min_price = min_price
        self.max_price = max_price
        self.start_time = start_time
        self.end_time = end_time
        self.buses_per_day = buses_per_day
        self.speed_kmh = speed_kmh

    def departure_times(self):
        # First bus at start_time, last bus at end_time, the rest evenly in between
        start = to_minutes(self.start_time)
        end = to_minutes(self.end_time)
        window = (end - start) % (24 * 60)      # % makes overnight windows like 22:00-06:00 work too
        if self.buses_per_day == 1:
            return [self.start_time]
        gap = window / (self.buses_per_day - 1)
        times = []
        for number in range(self.buses_per_day):
            times.append(to_time_text(round(start + number * gap)))
        return times

    def minutes_until_next_bus(self, from_minutes):
        return min((to_minutes(time_text) - from_minutes) % (24 * 60) for time_text in self.departure_times())

    def random_price(self):
        return round(random.uniform(self.min_price, self.max_price), 2)

    def runs_at(self, travel_time):
        start = datetime.strptime(self.start_time, "%H:%M").time()
        end = datetime.strptime(self.end_time, "%H:%M").time()
        time = datetime.strptime(travel_time, "%H:%M").time()
        # Normal window, like 06:00-14:00
        if start <= end:
            return start <= time <= end
        # Window crosses midnight, like 22:00-06:00
        return time >= start or time <= end

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

    def travel_minutes(self, start, finish, coordinates, madrid_x, madrid_y):
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

#---------------------------CLASSES/DICT-------------------------------------------

def load_destinations(path):
    destinations = []
    with open(path, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            destinations.append(Destination.from_dict(row))
    return destinations

def load_companies(path):
    companies = []
    with open(path, newline="") as file:
        reader = csv.DictReader(file)
        for index, row in enumerate(reader, start=1):
            # Bad rows are logged and skipped, the rest of the file still loads
            try:
                validation.validate_company_row(row)
            except (DataError, ValueError) as error:
                logger.warning(f"{os.path.basename(path)} line {reader.line_num}: rejected {row.get('company')!r}: {error}")
                continue
            profile = Profile(row["description"], float(row["min_price"]), float(row["max_price"]), row["start_time"], row["end_time"], int(row["buses_per_day"]), float(row["speed_kmh"]))
            companies.append(Company(row["company"], profile, index))
    logger.info(f"Loaded {len(companies)} companies from {os.path.basename(path)}")
    return companies

