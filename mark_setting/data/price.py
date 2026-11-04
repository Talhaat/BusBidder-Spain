# File to creat prices for destinations  for the user

import math


#Function to calculate the price for one destination, scaled between a company's min and max price
# Input is destination name, list of destinations that company serves, coordinates dict,
# Madrid's x and y, min_price and max_price. Return is the price as a float.
def calculate_price(destination, served_destinations, coordinates, madrid_x, madrid_y, min_price, max_price):
    # Calculate the Euclidean distance from Madrid for every destination this company serves
    distances = {d: math.dist(coordinates[d], (madrid_x, madrid_y)) for d in served_destinations}
    min_distance = min(distances.values())
    max_distance = max(distances.values())

    # Only one destination served, so there is no range to scale across
    if min_distance == max_distance:
        return round(min_price, 2)

    fraction = (distances[destination] - min_distance) / (max_distance - min_distance)
    price = min_price + fraction * (max_price - min_price)
    return round(price, 2)


#Function to get every company and price option for a given destination
# Input is destination name, connections dict, coordinates dict, Madrid's x and y, list of Company objects.
# Return is a list of (company name, price) options.
def get_options(destination, connections, coordinates, madrid_x, madrid_y, companies):
    options = []
    for company in companies:
        served_destinations = connections.get(company.name, [])
        if destination not in served_destinations:
            continue
        price = calculate_price(
            destination, served_destinations, coordinates, madrid_x, madrid_y,
            company.profile.min_price, company.profile.max_price
        )
        options.append((company.name, price))
    return options


#Function to get every company and price option for a journey between any two destinations
#Madrid stays the hub: a Madrid-involved journey is a direct leg, any other pair routes
#through Madrid (start -> Madrid -> finish), and only companies serving both ends qualify.
# Input is start name, finish name, connections dict, coordinates dict, Madrid's x and y, list of Company objects.
# Return is a list of (company name, price) options.
def get_route_options(start, finish, connections, coordinates, madrid_x, madrid_y, companies):
    if start == finish:
        return []

    if start == "Madrid":
        return get_options(finish, connections, coordinates, madrid_x, madrid_y, companies)

    if finish == "Madrid":
        return get_options(start, connections, coordinates, madrid_x, madrid_y, companies)

    options = []
    for company in companies:
        served_destinations = connections.get(company.name, [])
        if start not in served_destinations or finish not in served_destinations:
            continue

        price_to_madrid = calculate_price(
            start, served_destinations, coordinates, madrid_x, madrid_y,
            company.profile.min_price, company.profile.max_price
        )
        price_from_madrid = calculate_price(
            finish, served_destinations, coordinates, madrid_x, madrid_y,
            company.profile.min_price, company.profile.max_price
        )
        options.append((company.name, round(price_to_madrid + price_from_madrid, 2)))
    return options
