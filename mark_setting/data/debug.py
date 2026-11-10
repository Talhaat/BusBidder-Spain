# Code to debug
import csv

from marketplace.marketplace import load_companies


with open('destination.csv', mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    total_destinations = list(reader) 
print(total_destinations)

dest_used = set()
with open('bus_connections.csv', newline="",encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        dest_used.update(row["destinations"].split(";"))
print(dest_used)

total_destinations_flat = set(row[0] for row in total_destinations[1:])
not_dest = total_destinations_flat - dest_used
print("\n")
print("DESTINATION NOT INCLUDED IN BUS ROUTE:",not_dest)

from marketplace.marketplace import load_companies

for company in load_companies():
    print(company.name, vars(company.profile))

# Test validation with the broken test file: only the valid rows should load,
# every bad row should be printed as a WARNING with the reason
import logging
import models

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
print("\n")
test_companies = models.load_companies("test_data/invalid_company_profile.csv")
print("Accepted from test file:", [company.name for company in test_companies])

# Show the schedule: departure times for every real company and the test boundary rows
print("\n")
for company in models.load_companies("company_profile.csv") + test_companies:
    print(company.name, company.profile.departure_times())


