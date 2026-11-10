# Code to debug - run from the project folder with: uv run python tools/debug.py
import csv
import os
import sys

# Let Python find the program code in busbidder/, one folder up from this file
project_folder = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(os.path.join(project_folder, "busbidder"))

import loader
import models


with open(loader.destination_path, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    total_destinations = list(reader)
print(total_destinations)

dest_used = set()
with open(loader.connections_path, newline="",encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        dest_used.update(row["destinations"].split(";"))
print(dest_used)

total_destinations_flat = set(row[0] for row in total_destinations[1:])
not_dest = total_destinations_flat - dest_used
print("\n")
print("DESTINATION NOT INCLUDED IN BUS ROUTE:",not_dest)

for company in models.load_companies(loader.company_path):
    print(company.name, vars(company.profile))

# Test validation with the broken test file: only the valid rows should load,
# every bad row should be printed as a WARNING with the reason
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
print("\n")
test_path = os.path.join(project_folder, "tests", "data", "invalid_company_profile.csv")
test_companies = models.load_companies(test_path)
print("Accepted from test file:", [company.name for company in test_companies])

# Show the schedule: departure times for every real company and the test boundary rows
print("\n")
for company in models.load_companies(loader.company_path) + test_companies:
    print(company.name, company.profile.departure_times())
