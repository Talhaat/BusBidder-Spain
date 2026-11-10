# File for reading and writing the csv files

import os
import random
import csv
from models import Destination

code_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.dirname(code_folder)
data_folder = os.path.join(project_folder, "data")

# Paths to our CSV files
dest_path = os.path.join(data_folder, "destination.csv")
map_dest_path = os.path.join(data_folder, "map_destination.csv")
company_path = os.path.join(data_folder, "company_profile.csv")
conn_path = os.path.join(data_folder, "bus_connections.csv")
prof_path = os.path.join(data_folder, "destination_profile.csv")

def load_destinations():
    places = []
    with open(dest_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            places.append(row["destination"])
    return places

def load_companies():
    companies = []
    with open(company_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            companies.append(row["company"])
    return companies

def load_or_gen_conn(companies, destinations, dest_counts, custom_dests):
    conn_map = {}

    # Check if we have saved connections
    if os.path.exists(conn_path):
        with open(conn_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                conn_map[row["company"]] = row["destinations"].split(";")
        return conn_map

    # Generate new connections
    for company in companies:
        # What's required vs what we need
        required = custom_dests.get(company, [])
        total = dest_counts.get(company, 5)

        # Available choices (excluding required ones)
        pool = [d for d in destinations if d not in required]

        # Calculate extra destinations needed to meet the total count for company
        extra_needed = total - len(required)
        if extra_needed < 0:
            extra_needed = 0
        if extra_needed > len(pool):
            extra_needed = len(pool)

        extra = random.sample(pool, extra_needed)
        conn_map[company] = required + extra
    return conn_map

def save_conn(conn_map):
    with open(conn_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["company", "destinations"])
        for key, val in conn_map.items():
            writer.writerow([key, ";".join(val)])

def load_or_gen_coords(cities, w, h):
    coords = {}

    if os.path.exists(map_dest_path):
        with open(map_dest_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                x = int(row["x"])
                y = int(row["y"])
                coords[row["destination"]] = (x, y)
        return coords

    # Random placement for new setup
    for city in cities:
        x = random.randint(0, w)
        y = random.randint(0, h)
        coords[city] = (x, y)
    return coords

def save_coords(coords):
    with open(map_dest_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["destination", "x", "y"])
        for name, (x, y) in coords.items():
            writer.writerow([name, x, y])

def load_or_gen_profiles(names, categories):
    
    profiles = {}

    if os.path.exists(prof_path):
        with open(prof_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                dest = Destination.from_dict(row)
                profiles[dest.name] = dest
        return profiles

    # Build from categories
    for n in names:
        cats = categories.get(n, [])
        profiles[n] = Destination(n, cats)
    return profiles

def save_profiles(profs):
    with open(prof_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["destination", "categories"])
        for name, dest in profs.items():
            writer.writerow(dest.to_row())
