# Loader - reads and writes all the project's csv files

import csv
import os
import random

from models import Destination

#Folder locations: the csv files live in data/, next to the busbidder/ code folder
data_folder = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"))
destination_path = os.path.join(data_folder, "destination.csv")
map_destination_path = os.path.join(data_folder, "map_destination.csv")
company_path = os.path.join(data_folder, "company_profile.csv")
connections_path = os.path.join(data_folder, "bus_connections.csv")
destination_profile_path = os.path.join(data_folder, "destination_profile.csv")


#Function to read destination names from destination.csv
# Input is none, return list of city names.
def load_destinations():
    with open(destination_path) as file:
        reader = csv.DictReader(file)
        return [row["destination"] for row in reader]


#Function to read company names from company_profile.csv
# Input is none, return list of company names.
def load_companies():
    with open(company_path) as file:
        reader = csv.DictReader(file)
        return [row["company"] for row in reader]


#Function to load saved connections if they exist, or make random ones per company
def load_or_generate_connections(companies, destinations, destination_counts, custom_destinations):
    if os.path.exists(connections_path):
        connections = {}
        with open(connections_path, newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                connections[row["company"]] = row["destinations"].split(";")
        return connections

    connections = {}
    for company in companies:
        required = custom_destinations.get(company, [])
        count = destination_counts.get(company, 5)
        remaining_count = max(count - len(required), 0)
        remaining_choices = [d for d in destinations if d not in required]
        extra = random.sample(remaining_choices, min(remaining_count, len(remaining_choices)))
        connections[company] = required + extra
    return connections


#Function to save connections into bus_connections.csv
# Input is dict of company name to list of destinations, return is none.
def save_connections(connections):
    with open(connections_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["company", "destinations"])
        for company, served in connections.items():
            writer.writerow([company, ";".join(served)])


#Function to load saved coordinates if they exist, or make random ones
# Input is list of city names and the canvas size, return dict of city name to (x, y).
def load_or_generate_coordinates(destinations, canvas_width, canvas_height):
    if os.path.exists(map_destination_path):
        coordinates = {}
        with open(map_destination_path, newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                coordinates[row["destination"]] = (int(row["x"]), int(row["y"]))
        return coordinates

    coordinates = {}
    for destination in destinations:
        x = random.randint(0, canvas_width)
        y = random.randint(0, canvas_height)
        coordinates[destination] = (x, y)
    return coordinates


#Function to save coordinates into map_destination.csv
# Input is dict of city name to (x, y), return is none.
def save_coordinates(coordinates):
    with open(map_destination_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["destination", "x", "y"])
        for destination, (x, y) in coordinates.items():
            writer.writerow([destination, x, y])


#Function to load saved destination profiles if they exist, or make them from destination_categories
# Input is list of destination names and dict of name to list of categories, return dict of name to Destination object.
def load_or_generate_destination_profiles(destinations, destination_categories):
    if os.path.exists(destination_profile_path):
        profiles = {}
        with open(destination_profile_path, newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                destination = Destination.from_dict(row)
                profiles[destination.name] = destination
        return profiles

    profiles = {}
    for name in destinations:
        profiles[name] = Destination(name, destination_categories.get(name, []))
    return profiles


#Function to save destination profiles into destination_profile.csv
# Input is dict of name to Destination object, return is none.
def save_destination_profiles(profiles):
    with open(destination_profile_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["destination", "categories"])
        for destination in profiles.values():
            writer.writerow(destination.to_row())
