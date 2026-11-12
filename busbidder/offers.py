# File for making the offers: one offer for every bus of every trip of every company

import random

from models import Offer

def timetable(profile):
    times = []
    for days in range(2):
        for time in profile.departure_times():
            times.append(days * 24 * 60 + time)
    return times

def offer_id(company, number):
    id = company.name[:3].upper()
    return f"{id}-{number:05d}"

def trip(company):
    destinations = ["Madrid"] + company.destinations
    trips = []
    for start in destinations:
        for finish in destinations:
            if start != finish:
                trips.append((start, finish))
    return trips

def trip_offer(company,
               start,
               finish,
               dep,
               number,
               coords,
               madrid_x,
               madrid_y):
    arr = dep + company.travel_minutes(start, finish, coords, madrid_x, madrid_y)

    price = company.price_between(start, finish,coords, madrid_x, madrid_y)
    seats = random.randint(0, company.profile.max_seats)

    return Offer(
        offer_id(company, number),
        [company],
        start,
        finish,
        dep,
        arr,
        price,
        # changeable and refundable come from the company's "change" and "refund" columns
        company.profile.change == 1,
        company.profile.refund == 1,
        seats,
    )

def make_offer(companies, coords, madrid_x, madrid_y):
    offers = []
    for company in companies:
        n = 0
        for start, finish in trip(company):
            for dep in timetable(company.profile):
                n+=1
                offers.append(trip_offer(company, start, finish, dep, n, coords, madrid_x, madrid_y))
    return offers
