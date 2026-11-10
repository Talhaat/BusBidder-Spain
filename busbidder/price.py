# File to creat prices for destinations  for the user

import math

from offer import Offer
from time_utils import to_minutes


#Function to turn a distance into a price, scaled between a company's min and max price
# Input is the distance to price, the min and max distance possible for that company's
# network, and the company's min_price/max_price. Return is the price as a float.
def price_from_distance(distance, min_distance, max_distance, min_price, max_price):
    # No range to scale across (e.g. only one possible path)
    if min_distance == max_distance:
        return round(min_price, 2)

    fraction = (distance - min_distance) / (max_distance - min_distance)
    price = min_price + fraction * (max_price - min_price)
    return round(price, 2)


#Function to find the one path between two points in a tree, and its total distance
#BFS, since a tree has exactly one path between any two points - no competing routes.
# Input is start name, finish name, dict of name to (x, y), list of (name1, name2) edges.
# Return is the total distance along that path, or None if not connected.
def path_distance(start, finish, points, edges):
    graph = {}
    for name1, name2 in edges:
        edge_distance = math.dist(points[name1], points[name2])
        graph.setdefault(name1, []).append((name2, edge_distance))
        graph.setdefault(name2, []).append((name1, edge_distance))

    visited = {start}
    queue = [(start, 0)]
    while queue:
        current, total = queue.pop(0)
        if current == finish:
            return total
        for neighbor, edge_distance in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, total + edge_distance))

    return None


#Function to get every company and price option for a journey between any two points
#Each company prices the trip itself, see Company.price_between in models.py.
#Each offer takes the company's first bus at or after the chosen travel time.
# Input is start name, finish name, coordinates dict, Madrid's x and y, list of Company objects,
# travel time as "HH:MM". Return is a list of direct Offer objects, one per company that serves the trip.
def get_route_options(start, finish, coordinates, madrid_x, madrid_y, companies, travel_time):
    if start == finish:
        return []

    start_minutes = to_minutes(travel_time)
    options = []
    for company in companies:
        company_price = company.price_between(start, finish, coordinates, madrid_x, madrid_y)
        if company_price is not None:
            departure = start_minutes + company.profile.minutes_until_next_bus(start_minutes)
            arrival = departure + company.travel_minutes(start, finish, coordinates, madrid_x, madrid_y)
            options.append(Offer([company], start, finish, company_price, departure, arrival))
    return options


