# Code for weighted offer ranking

# Registry: criterion name -> the function that scores it
criteria = {}

def criterion(function):
    # Decorator: @criterion above a function adds it to the criteria dict
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

#Function for flexibility, neither = 0, changeble or refundeble = 0.5 and both = 1
@criterion
def flexibility(offer, offers, preff):
    score = 0
    if offer.changeable:
        score += 0.5
    if offer.refundable:
        score += 0.5
    return score


# Total score: each criterion score (0-1) times its weight, weights come from make_weights
def score(price, duration, time, flex, weights):
    return weights["price"]*price + weights["duration"]*duration + weights["dep_time"]*time + weights["flexibility"]*flex

# Customer importance 0-10 per criterion -> weights that always add up to 1.0
def make_weights(importance):
    total = sum(importance.values())
    if total == 0:
        raise ValueError("At least one criterion must be above 0")
    weights = {}
    for name, value in importance.items():
        weights[name] = value/total
    return weights

# Score every offer with every criterion in the registry, then sort: best total first
def rank_offers(offers, weights, preff):
    ranked = []
    for offer in offers:
        # One score per criterion (0-1), kept so the GUI can show them
        scores = {}
        for name in criteria:
            scores[name] = criteria[name](offer, offers, preff)
        total = score(scores["price"], scores["duration"], scores["dep_time"], scores["flexibility"], weights)
        # Scores are kept here, not saved on the offer: the offers are reused for every search
        ranked.append({"offer": offer, "scores": scores, "total": total})
    ranked.sort(key=lambda row: row["total"], reverse=True)
    return ranked

# Must have: remove offers with a total score under the minimum (the GUI shows the score 0-10)
def score_allowed(ranked, min_score):
    kept = []
    for row in ranked:
        # total is 0-1, times 10 and rounded like the GUI shows it, so 7.0 on screen passes "7"
        if round(row["total"] * 10, 1) >= min_score:
            kept.append(row)
    return kept

#---------------------------EXPLANATION-------------------------------------------
# Short explanation for the top 3: each offer compared with the other two on price, travel time and flexibility

def compare(value, values, name):
    # Where one value is among the top 3: lowest, medium or highest
    if min(values) == max(values):
        return f"same {name}"
    if value == min(values):
        return f"lowest {name}"
    if value == max(values):
        return f"highest {name}"
    return f"medium {name}"

def explain_top3(offers):
    # offers = the top 3 Offer objects (can be fewer if only 1 or 2 are left)
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

# Function to map max value/min value to 1-0
def scale_mapping(val, low, high):
    # Lowest value = 1, highest = 0
    # All values the same: nobody is better, everyone gets full score
    if high == low:
        return 1
    return (high-val)/(high-low)

def min_from_preff(offer,preff):
    difference = abs(offer.departure % 1440 - preff)
    return min(difference,1440-difference)