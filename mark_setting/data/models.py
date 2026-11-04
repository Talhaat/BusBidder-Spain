import csv
import random

#---------------------------CLASSES/DICT-------------------------------------------

#Class for a company's profile, description text plus a price range
class Profile:
    def __init__(self, description, min_price, max_price):
        self.description = description
        self.min_price = min_price
        self.max_price = max_price

    #Function to generate a random price inside this company's price range
    # Input is none, return a random price as a float.
    def random_price(self):
        return round(random.uniform(self.min_price, self.max_price), 2)


#Class for a bus company, has a Profile
class Company:
    def __init__(self, name, profile, ID):
        self.name = name
        self.profile = profile
        self.ID = ID


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
            profile = Profile(row["description"], float(row["min_price"]), float(row["max_price"]))
            companies.append(Company(row["company"], profile, index))
    return companies


