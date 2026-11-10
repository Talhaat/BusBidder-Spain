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

#Map scale: one pixel on the 3000x2000 map canvas counts as this many km
km_per_pixel = 0.4

#---------------------------CLASSES/DICT-------------------------------------------

#Class for a company's profile, description text, a price range, a departure window,
#how many buses leave per day on each route and how fast the buses drive
class Profile:
    def __init__(self, description, min_price, max_price, start_time, end_time, buses_per_day, speed_kmh):
        self.description = description
        self.min_price = min_price
        self.max_price = max_price
        self.start_time = start_time
        self.end_time = end_time
        self.buses_per_day = buses_per_day
        self.speed_kmh = speed_kmh

    #Function to spread this company's departures evenly over its time window,
    #first bus at start_time and last bus at end_time
    # Input is none, return list of departure times as "HH:MM" text.
    def departure_times(self):
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

    #Function to find how long until this company's next bus leaves, wrapping to the next day
    # Input is a time in minutes after midnight, return minutes to wait (0 if a bus leaves right then).
    def minutes_until_next_bus(self, from_minutes):
        return min((to_minutes(time_text) - from_minutes) % (24 * 60) for time_text in self.departure_times())

    #Function to generate a random price inside this company's price range
    # Input is none, return a random price as a float.
    def random_price(self):
        return round(random.uniform(self.min_price, self.max_price), 2)

    #Function to check if this company has buses at a given time
    # Input is time as "HH:MM" text, return True or False.
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
    # F
    def price_between(self, start, finish, coordinates, madrid_x, madrid_y):
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

    #Function to build this company's route tree: Madrid plus every destination it serves
    # Input is coordinates dict, Madrid's x and y. Return is (dict of name to (x, y), list of tree edges).
    def route_tree(self, coordinates, madrid_x, madrid_y):
        points = {"Madrid": (madrid_x, madrid_y)}
        for destination in self.destinations:
            points[destination] = coordinates[destination]
        return points, routes.minimum_spanning_tree(points)

    #Function to work out how long this company's bus takes between two points on its route tree
    # Input is start name, finish name, coordinates dict, Madrid's x and y.
    # Return is the travel time in whole minutes.
    def travel_minutes(self, start, finish, coordinates, madrid_x, madrid_y):
        points, edges = self.route_tree(coordinates, madrid_x, madrid_y)
        km = price.path_distance(start, finish, points, edges) * km_per_pixel
        return round(km / self.profile.speed_kmh * 60)
    
#Class for a destination, name plus a list of categories like major city, coastal, beach
class Destination:
    def __init__(self, name, categories):
        self.name = name
        self.categories = categories

    #Classmethod constructor: builds a Destination from a csv row dict
    @classmethod
    def from_dict(cls, data):
        categories = data["categories"].split(";") if data["categories"] else []
        return cls(data["destination"], categories)

    #Function to turn this destination into a list ready to write as a csv row
    def to_row(self):
        return [self.name, ";".join(self.categories)]

#---------------------------CLASSES/DICT-------------------------------------------


#Function to load destinations from destination_profile.csv
# Input is path to the csv file, return list of Destination objects.
def load_destinations(path):
    destinations = []
    with open(path, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            destinations.append(Destination.from_dict(row))
    return destinations


#Function to load companies from company_profile.csv
# Input is path to the csv file, return list of Company objects.
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


