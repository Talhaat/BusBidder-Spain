
# File for calculating journe/transfare
from offer import Offer
from price import get_route_options

#Shortest time a traveller needs to change bus in Madrid
min_change_minutes = 10


#Function to combine a bus to Madrid and a bus from Madrid (two different companies) into transfer offers.
#The second bus is that company's first bus leaving at least min_change_minutes after the first bus arrives.
# Input is start name, finish name, coordinates dict, Madrid's x and y, list of Company objects,
# travel time as "HH:MM". Return is a list of transfer Offer objects.
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
                ready = first_leg.arrival + min_change_minutes
                wait = min_change_minutes + second_company.profile.minutes_until_next_bus(ready)
                second_departure = first_leg.arrival + wait
                second_travel_minutes = second_leg.arrival - second_leg.departure
                companies_used = first_leg.companies + second_leg.companies
                total_price = first_leg.price + second_leg.price
                options.append(Offer(companies_used, start, finish, total_price,
                                     first_leg.departure, second_departure + second_travel_minutes, wait))
    return options


# FUnction to find best transfare option
def find_best_transfer(start, finish, coordinates, madrid_x, madrid_y, companies, travel_time):
    direct_options = get_route_options(start, finish, coordinates, madrid_x, madrid_y, companies, travel_time)
    if direct_options:
        return direct_options

    return get_transfer_options(start, finish, coordinates, madrid_x, madrid_y, companies, travel_time)


#Function to keep only the offers whose first bus leaves at the chosen time
# Input is list of Offer objects, time as "HH:MM".
# Return is the filtered list.
def filter_by_time(options, travel_time):
    return [offer for offer in options if offer.runs_at(travel_time)]
