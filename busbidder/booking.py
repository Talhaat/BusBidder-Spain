# File for booking an offer: seat check, booking reference and taking the seats off

import logging
from datetime import datetime

from exceptions import NoSeatsError
from models import Booking

logger = logging.getLogger(__name__)

payment_status = "paid"

# The real buses behind an offer
def legs(offer, offers_by_id):
    buses = []
    for offer_id in offer.offer_id.split("+"):
        buses.append(offers_by_id[offer_id])
    return buses

# Seats left after booking
def seats_left(offer, offers_by_id):
    seats = []
    for bus in legs(offer, offers_by_id):
        seats.append(bus.seats)
    return min(seats)

# Make reference code
def make_reference(bookings):
    used = []
    for booking in bookings:
        used.append(booking.reference)
    number = 1
    reference = f"BB-{number:05d}"
    while reference in used:
        number += 1
        reference = f"BB-{number:05d}"
    return reference

# Check seats again right before booking
def book(offer, profile_name, bookings, offers_by_id):
    if seats_left(offer, offers_by_id) < 1:
        raise NoSeatsError(f"offer {offer.offer_id} has no free seats left")

    now = datetime.now()
    booking = Booking(
        make_reference(bookings),
        now.strftime("%Y-%m-%d %H:%M"),
        offer.offer_id,
        profile_name,
        1,
        offer.price,
        offer.changeable,
        offer.refundable,
        payment_status
    )

    # Reduce number of seats on offers
    for bus in legs(offer, offers_by_id):
        bus.seats -= 1
    # A transfer offer is its own object, keep its seat count the same as its buses
    offer.seats = seats_left(offer, offers_by_id)

    bookings.append(booking)
    return booking

# Booking is checked from preexisting file before generating offers
def apply_bookings(bookings, offers_by_id):
    kept = []
    for booking in bookings:
        buses = []
        for offer_id in booking.offer_id.split("+"):
            buses.append(offers_by_id[offer_id])

        # More seats booked than the bus has free: the booking does not fit, it is logged and skipped
        enough = True
        for bus in buses:
            if bus.seats < booking.seats:
                enough = False
        if not enough:
            logger.warning(f"bookings.csv: {booking.reference} skipped, offer {booking.offer_id} has fewer free seats than booked")
            continue

        for bus in buses:
            bus.seats -= booking.seats
        kept.append(booking)
    return kept
