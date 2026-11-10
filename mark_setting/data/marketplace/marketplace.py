# File for marketplace. Importds data from company_profile.csv and 
# creates Company objects for each row. Each Company has a Profile object.

import csv
import os

from models import Profile

#Path to company_profile.csv, one folder up from this file
company_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "company_profile.csv")


#Class for a bus company, has a Profile
class Company:
    def __init__(self, name, profile):
        self.name = name
        self.profile = profile


#Function to make one Company object for every row in company_profile.csv
# Input is none, return list of Company objects.
def load_companies():
    companies = []
    with open(company_path, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            profile = Profile(row["description"], float(row["min_price"]), float(row["max_price"]), row["start_time"], row["end_time"], int(row["buses_per_day"]), float(row["speed_kmh"]))
            companies.append(Company(row["company"], profile))
    return companies
