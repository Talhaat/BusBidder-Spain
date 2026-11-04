# Code to debug
import csv

with open('destination.csv', mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    total_destinations = list(reader) 
print(total_destinations)

dest_used = set()
with open('bus_connections.csv', newline="",encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        dest_used.update(row["destinations"].split(";"))
print(dest_used)

total_destinations_flat = set(row[0] for row in total_destinations[1:])
not_dest = total_destinations_flat - dest_used
print("\n")
print("DESTINATION NOT INCLUDED IN BUS ROUTE:",not_dest)

