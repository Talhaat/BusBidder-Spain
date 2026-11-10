# File for the Offer class: one bus trip a traveller can buy

from time_utils import to_time_text, to_duration_text

class Offer:
    def __init__(self, companies, start, finish, price, departure, arrival, wait=0):
        # One company for a direct bus, two for a transfer via Madrid
        self.companies = companies
        self.start = start
        self.finish = finish
        self.price = price
        self.transfers = len(companies) - 1
        # Times are minutes after midnight on the travel day, past 24 * 60 means the next day
        self.departure = departure
        self.arrival = arrival
        self.wait = wait  # minutes waiting in Madrid, 0 for a direct bus

    def runs_at(self, travel_time):
        return self.companies[0].profile.runs_at(travel_time)

    def __str__(self):
        if self.transfers == 0:
            route = self.companies[0].name
        else:
            route = f"{self.companies[0].name} -> Madrid (wait {to_duration_text(self.wait)}) -> {self.companies[1].name}"
        next_day = " (next day)" if self.arrival >= 24 * 60 else ""
        return f"{route}: {self.price} EUR, departs {to_time_text(self.departure)}, arrives {to_time_text(self.arrival)}{next_day}"
