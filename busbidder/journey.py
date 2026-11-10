# File for calculating journeys and transfers
from offer import Offer
from price import get_route_options

# Shortest time to change bus in Madrid
min_change_minutes = 10

def get_transfer_options(start, finish, coordinates, madrid_x, madrid_y, companies, travel_time):
    if start == finish:
        return []
    first_segment = get_route_options(start, "Madrid", coordinates, madrid_x, madrid_y, companies, travel_time)
    second_segment = get_route_options("Madrid", finish, coordinates, madrid_x, madrid_y, companies, travel_time)
    options = []
    for first_leg in first_segment:
        for second_leg in second_segment:
            if first_leg.companies != second_leg.companies:
                second_company = second_leg.companies[0]
                # Second bus: the first one leaving at least min_change_minutes after arriving
                ready = first_leg.arrival + min_change_minutes
                wait = min_change_minutes + second_company.profile.minutes_until_next_bus(ready)
                second_departure = first_leg.arrival + wait
                second_travel_minutes = second_leg.arrival - second_leg.departure
                companies_used = first_leg.companies + second_leg.companies
                total_price = first_leg.price + second_leg.price
                options.append(Offer(companies_used, start, finish, total_price,
                                     first_leg.departure, second_departure + second_travel_minutes, wait))
    return options

def find_best_transfer(start, finish, coordinates, madrid_x, madrid_y, companies, travel_time):
    direct_options = get_route_options(start, finish, coordinates, madrid_x, madrid_y, companies, travel_time)
    if direct_options:
        return direct_options

    return get_transfer_options(start, finish, coordinates, madrid_x, madrid_y, companies, travel_time)

def filter_by_time(options, travel_time):
    return [offer for offer in options if offer.runs_at(travel_time)]
