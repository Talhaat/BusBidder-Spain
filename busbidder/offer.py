# Offer - one bus trip a traveller can buy, direct or with a transfer via Madrid

from time_utils import to_time_text, to_duration_text


#Class for one offer: the companies used (one for a direct bus, two for a transfer
#via Madrid), where it goes from and to, the total price and the times.
#Times are minutes after midnight on the travel day, and can go past 24 * 60 for the next day.
class Offer:
    def __init__(self, companies, start, finish, price, departure, arrival, wait=0):
        self.companies = companies
        self.start = start
        self.finish = finish
        self.price = price
        self.transfers = len(companies) - 1
        self.departure = departure
        self.arrival = arrival
        self.wait = wait  # minutes waiting in Madrid, 0 for a direct bus

    #Function to check if the first bus of this offer leaves at a given time
    # Input is time as "HH:MM" text, return True or False.
    def runs_at(self, travel_time):
        return self.companies[0].profile.runs_at(travel_time)

    #Function to decide what print() shows for this offer
    # Input is none, return a string like
    # "SolRuta -> Madrid (wait 25 min) -> CostaLink: 30.5 EUR, departs 08:40, arrives 14:05".
    def __str__(self):
        if self.transfers == 0:
            route = self.companies[0].name
        else:
            route = f"{self.companies[0].name} -> Madrid (wait {to_duration_text(self.wait)}) -> {self.companies[1].name}"
        next_day = " (next day)" if self.arrival >= 24 * 60 else ""
        return f"{route}: {self.price} EUR, departs {to_time_text(self.departure)}, arrives {to_time_text(self.arrival)}{next_day}"
