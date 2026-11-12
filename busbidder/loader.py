# File for reading and writing the csv files

import os
import random
import csv
import logging

import validation
from exceptions import DataError
from models import Destination, Offer
from offers import make_offer

logger = logging.getLogger(__name__)

code_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.dirname(code_folder)
data_folder = os.path.join(project_folder, "data")

# Paths to our CSV files
dest_path = os.path.join(data_folder, "destination.csv")
map_dest_path = os.path.join(data_folder, "map_destination.csv")
company_path = os.path.join(data_folder, "company_profile.csv")
conn_path = os.path.join(data_folder, "bus_connections.csv")
prof_path = os.path.join(data_folder, "destination_profile.csv")
offers_path = os.path.join(data_folder, "offers.csv")

#---------------------------DESTINATIONS-------------------------------------------
def load_destinations():
    places = []
    with open(dest_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            places.append(row["destination"])
    return places

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
#---------------------------DESTINATIONS-------------------------------------------

#---------------------------MAP------------------------------------------
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
#---------------------------MAP-------------------------------------------


#---------------------------OFFERS-------------------------------------------

def load_or_gen_offers(companies, places, coordinates, madrid_x, madrid_y):
    # Use the saved file, so seats and times stay the same between runs
    if os.path.exists(offers_path):
        return load_offers(offers_path, companies, places)

    offers = make_offer(companies, coordinates, madrid_x, madrid_y)
    save_offers(offers)
    return offers

def load_offers(path, companies, places):
    by_name = {}
    for company in companies:
        by_name[company.name] = company

    offers = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Bad rows are logged and skipped, the rest of the file still loads
            try:
                validation.validate_offer_row(row, by_name, places)
            except (DataError, ValueError) as error:
                logger.warning(f"{os.path.basename(path)} line {reader.line_num}: rejected {row.get('offer_id')!r}: {error}")
                validation.save_error(error, os.path.basename(path), reader.line_num, row)
                continue
            offers.append(Offer.from_dict(row, by_name))
    logger.info(f"Loaded {len(offers)} offers from {os.path.basename(path)}")
    return offers

def save_offers(offers):
    with open(offers_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(validation.offer_columns)
        for offer in offers:
            writer.writerow(offer.to_row())
#---------------------------OFFERS-------------------------------------------
