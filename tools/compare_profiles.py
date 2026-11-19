# File for comparing the traveller profiles, run from the project folder with: uv run python tools/compare_profiles.py
# Runs the same search as the GUI for every profile in data/traveller_profile.csv, books the best offer
# of each in memory (data/bookings.csv is not changed) and saves the results in output/

import csv
import os
import sys
from datetime import datetime

# Let Python find the program code in busbidder/, one folder up from this file
project_folder = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(os.path.join(project_folder, "busbidder"))

import booking
import datagen
import journey
import ranking
import validation
from timing import to_minutes, to_time_text, to_duration_text

output_folder = os.path.join(project_folder, "output")

# Readable names for the criteria, like on the Selected offer page
criterion_names = {"price": "price", "duration": "travel time", "dep_time": "departure time", "flexibility": "flexibility"}

# The same must-have filters as apply_filters() in the GUI
def must_haves(offers, profile):
    if profile.luggage:
        offers = journey.luggage_allowed(offers)
    offers = journey.rating_allowed(offers, int(profile.min_rating))
    offers = journey.flexibility_allowed(offers, profile.change, profile.refund)
    if profile.max_price != "Any":
        offers = journey.price_allowed(offers, float(profile.max_price))
    if profile.max_hours != "Any":
        offers = journey.duration_allowed(offers, int(profile.max_hours) * 60)
    return offers

# The same steps as find_buses() in the GUI: direct buses first, transfers only if no direct bus is left
def search(data, profile):
    weights = ranking.make_weights(profile.importance)
    preff = to_minutes(profile.time)
    available = journey.seats_available(data["offers"])
    options = must_haves(journey.get_direct_offers(available, profile.start, profile.finish), profile)
    ranked = ranking.score_allowed(ranking.rank_offers(options, weights, preff), int(profile.min_score))
    if not ranked:
        options = must_haves(journey.get_transfer_options(available, profile.start, profile.finish), profile)
        ranked = ranking.score_allowed(ranking.rank_offers(options, weights, preff), int(profile.min_score))
    # Day 1 first, best score first inside each day, like the table in the GUI
    return weights, sorted(ranked, key=lambda item: item["offer"].departure // (24 * 60))

# The best offer of three different companies, like the Top 3 box in the GUI
def top_three(ranked):
    top = []
    used = []
    for item in ranked:
        names = []
        for company in item["offer"].companies:
            names.append(company.name)
        name_text = " -> ".join(names)
        if name_text not in used:
            used.append(name_text)
            top.append(item)
        if len(top) == 3:
            break
    return top

def offer_text(item):
    offer = item["offer"]
    names = []
    for company in offer.companies:
        names.append(company.name)
    day = offer.departure // (24 * 60) + 1
    arrival_day = offer.arrival // (24 * 60) + 1
    arrival_text = to_time_text(offer.arrival)
    if arrival_day != day:
        arrival_text = f"{arrival_text} (day {arrival_day})"
    wait_text = ""
    if offer.transfers > 0:
        wait_text = f", wait in Madrid {to_duration_text(offer.wait)}"
    scores = []
    for name in item["scores"]:
        scores.append(f"{criterion_names.get(name, name)} {item['scores'][name] * 10:.1f}")
    return f"{' -> '.join(names)}, day {day} {to_time_text(offer.departure)}-{arrival_text} ({to_duration_text(offer.arrival - offer.departure)}{wait_text}), {offer.price} EUR, score {item['total'] * 10:.1f} ({', '.join(scores)})"

def yes_no(value):
    if value:
        return "yes"
    return "no"

def main():
    data = datagen.generate_data()
    os.makedirs(output_folder, exist_ok=True)

    # A copy of the saved bookings, so the new references do not repeat them, and bookings.csv is not changed
    bookings = list(data["bookings"])
    lines = [f"Traveller profile comparison, {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
    rows = []
    booked = []

    for profile in data["traveller_profiles"].values():
        weights, ranked = search(data, profile)
        top = top_three(ranked)
        top_offers = []
        for item in top:
            top_offers.append(item["offer"])
        explanations = ranking.explain_top3(top_offers)

        weight_parts = []
        for name in weights:
            weight_parts.append(f"{criterion_names.get(name, name)} {weights[name]:.2f}")
        lines.append(f"== {profile.name}: {profile.description}")
        lines.append(f"Route {profile.start} -> {profile.finish}, preferred time {profile.time}")
        lines.append(f"Must have: luggage {yes_no(profile.luggage)}, changeable {yes_no(profile.change)}, refundable {yes_no(profile.refund)}, min rating {profile.min_rating}, max price {profile.max_price}, max hours {profile.max_hours}, min score {profile.min_score}")
        lines.append(f"Weights: {', '.join(weight_parts)}")
        lines.append(f"Offers that pass the must-haves: {len(ranked)}")
        lines.append("Top 3 for your choices:")
        for number in range(len(top)):
            lines.append(f"  {number + 1}. {offer_text(top[number])}")
            lines.append(f"     {explanations[number]}")
            offer = top[number]["offer"]
            rows.append([profile.name, number + 1, offer.offer_id, offer.companies[0].name, offer.departure // (24 * 60) + 1,
                         to_time_text(offer.departure), to_time_text(offer.arrival), offer.arrival - offer.departure, offer.price,
                         offer.changeable, offer.refundable, offer.seats, round(top[number]["total"] * 10, 1),
                         round(top[number]["scores"]["price"] * 10, 1), round(top[number]["scores"]["duration"] * 10, 1),
                         round(top[number]["scores"]["dep_time"] * 10, 1), round(top[number]["scores"]["flexibility"] * 10, 1),
                         explanations[number]])

        # Book the best offer in memory, like pressing Book this bus
        if top:
            best = top[0]["offer"]
            seats_before = booking.seats_left(best, data["offers_by_id"])
            new_booking = booking.book(best, profile.name, bookings, data["offers_by_id"])
            booked.append(new_booking)
            lines.append(f"Booked the best offer: {new_booking.reference}, offer {new_booking.offer_id}, {new_booking.price} EUR, {new_booking.payment}, changeable {yes_no(new_booking.changeable)}, refundable {yes_no(new_booking.refundable)}, seats {seats_before} -> {booking.seats_left(best, data['offers_by_id'])}")
        lines.append("")

    with open(os.path.join(output_folder, "profile_comparison.txt"), "w") as f:
        f.write("\n".join(lines))

    with open(os.path.join(output_folder, "profile_comparison.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["profile", "rank", "offer_id", "company", "day", "departure", "arrival", "duration", "price", "changeable", "refundable", "seats", "score", "price_score", "duration_score", "dep_time_score", "flexibility_score", "explanation"])
        writer.writerows(rows)

    with open(os.path.join(output_folder, "booking_example.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(validation.booking_columns)
        for new_booking in booked:
            writer.writerow(new_booking.to_row())

    print("\n".join(lines))
    print("Saved: output/profile_comparison.txt, output/profile_comparison.csv, output/booking_example.csv")

if __name__ == "__main__":
    main()
