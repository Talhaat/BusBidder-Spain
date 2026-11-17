# File for booking

class Recomnedation:
    def __init__(self,offer, score, total):
        self.offer = offer
        self.score = score
        self.total = total

    def explain(self):


def compare(value,values, name):
    if min(values) == max(values):
        return f"same {name}"
    if value == min(values):
        return f"lowest {name}"
    if value == max(values):
        return f"highest {name}"
    return f"medium {name}"

def short_expl(offers):
    price = []
    durations = []
    flex = []

    for n in offers:
        price.append(n.arrival - offer.departure)
        flex.append(offer.changeble + offer.refundeble)

    lines = []
    for m in range(len(offers)):
        offer = offers[number]
        price_txt = compare()