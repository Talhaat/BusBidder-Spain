# Code for weighted offer ranking

# Registry
criteria = {}

# Decorator
def criterion(function):
    criteria[function.__name__] = function
    return function


@criterion
def price(offer, offers, preff):
    prices = []
    for n in offers:
        prices.append(n.price)
    min_price = min(prices)
    max_price = max(prices)
    return scale_mapping(offer.price, min_price, max_price)

@criterion
def duration(offer, offers, preff):
    durations = []
    for n in offers:
        durations.append(n.arrival - n.departure)
    min_duration = min(durations)
    max_duration = max(durations)
    return scale_mapping(offer.arrival - offer.departure, min_duration, max_duration)

@criterion
def dep_time(offer,offers,preff):
    difference = []
    for n in offers:
        difference.append(min_from_preff(n,preff))
    max_diff = max(difference)

    return scale_mapping(min_from_preff(offer,preff),0, max_diff)

#Function for flexibility
@criterion
def flexibility(offer, offers, preff):
    score = 0
    if offer.changeable:
        score += 0.5
    if offer.refundable:
        score += 0.5
    return score


# Customer importance 0-10 per criterion
def make_weights(importance):
    total = sum(importance.values())
    if total == 0:
        raise ValueError("At least one criterion must be above 0")
    weights = {}
    for name, value in importance.items():
        weights[name] = value/total
    return weights

# Score every offer with every criterion in the registry
def rank_offers(offers, weights, preff):
    ranked = []
    for offer in offers:
        # One score per criterion
        scores = {}
        for name in criteria:
            scores[name] = criteria[name](offer, offers, preff)
        # Total score
        total = 0
        for name in criteria:
            total += weights[name] * scores[name]
        ranked.append({"offer": offer, "scores": scores, "total": total})
    ranked.sort(key=lambda row: row["total"], reverse=True)
    return ranked

# Must-have
def score_allowed(ranked, min_score):
    kept = []
    for row in ranked:
        if round(row["total"] * 10, 1) >= min_score:
            kept.append(row)
    return kept

#---------------------------EXPLANATION-------------------------------------------
# Short explanation for the top 3: each offer compared with the other two on price, travel time and flexibility

# Where one value is among the top 3: lowest, medium or highest
def compare(value, values, name):
    if min(values) == max(values):
        return f"same {name}"
    if value == min(values):
        return f"lowest {name}"
    if value == max(values):
        return f"highest {name}"
    return f"medium {name}"

# offers = the top 3 Offer objects (can be fewer if only 1 or 2 are left)
def explain_top3(offers):
    # Only one offer: nothing to compare it with
    if len(offers) == 1:
        return ["the only offer that matches your choices"]

    prices = []
    durations = []
    flexibility = []
    for offer in offers:
        prices.append(offer.price)
        durations.append(offer.arrival - offer.departure)
        # True counts as 1: neither = 0, one of them = 1, both = 2
        flexibility.append(offer.changeable + offer.refundable)

    # One text per offer, the GUI puts the company name and score in front
    texts = []
    for number in range(len(offers)):
        price_text = compare(prices[number], prices, "price")
        duration_text = compare(durations[number], durations, "travel time")
        flex_text = compare(flexibility[number], flexibility, "flexibility")
        texts.append(f"{price_text}, {duration_text}, {flex_text}")
    return texts

# Function to map max/min value
def scale_mapping(val, low, high):
    if high == low:
        return 1
    return (high-val)/(high-low)

def min_from_preff(offer,preff):
    difference = abs(offer.departure % 1440 - preff)
    return min(difference,1440-difference)