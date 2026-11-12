

# File for finding direct offers and transfers in the loaded offers, and filtering them

from models import Offer

# Shortest time to change bus in Madrid
min_change_minutes = 10

def get_direct_offers(offers, start, finish):
    found = []
    for offer in offers:
        if offer.start == start and offer.finish == finish:
            found.append(offer)
    return found

def get_transfer_options(offers, start, finish):
    if start == finish:
        return []
    first_legs = get_direct_offers(offers, start, "Madrid")
    madrid_legs = get_direct_offers(offers, "Madrid", finish)

    options = []
    for first_leg in first_legs:
        ready = first_leg.arrival + min_change_minutes

        # Second bus: for every other company, its first bus leaving Madrid after ready
        next_legs = {}
        for second_leg in madrid_legs:
            name = second_leg.companies[0].name
            if name == first_leg.companies[0].name:
                continue
            if second_leg.departure < ready:
                continue
            if name not in next_legs or second_leg.departure < next_legs[name].departure:
                next_legs[name] = second_leg

        for second_leg in next_legs.values():
            wait = second_leg.departure - first_leg.arrival
            options.append(Offer(
                first_leg.offer_id + "+" + second_leg.offer_id,
                first_leg.companies + second_leg.companies,
                start,
                finish,
                first_leg.departure,
                second_leg.arrival,
                round(first_leg.price + second_leg.price, 2),
                first_leg.changeable and second_leg.changeable,
                first_leg.refundable and second_leg.refundable,
                min(first_leg.seats, second_leg.seats),
                wait,
            ))
    return options

def find_best_transfer(offers, start, finish):
    direct_options = get_direct_offers(offers, start, finish)
    if direct_options:
        return direct_options

    return get_transfer_options(offers, start, finish)

#---------------------------FILTERS-------------------------------------------
# The traveller's hard rules: offers that break one are removed before ranking

def luggage(luggage, price):
    if luggage == 1:
        return price
    return None

def luggage_allowed(offers):
    luggage_companies = []
    for offer in offers:
        allowed = True
        for company in offer.companies:
            if company.profile.luggage == 0:
                allowed = False
        if allowed:
            luggage_companies.append(offer)
    return luggage_companies

def rating_allowed(offers, min_rating):
    kept = []
    for offer in offers:
        # A transfer needs both companies to be good enough
        good = True
        for company in offer.companies:
            if company.profile.rating < min_rating:
                good = False
        if good:
            kept.append(offer)
    return kept
