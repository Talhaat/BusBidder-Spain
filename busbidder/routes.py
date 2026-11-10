# Routes - minimum spanning tree and unassigned destination handling

import math


#Function to build a minimum spanning tree connecting a set of named points
# Input is dict of name to (x, y), return list of (name1, name2) edges with no crossings back and forth.
def minimum_spanning_tree(points):
    names = list(points.keys())
    connected = {names[0]}
    remaining = set(names[1:])
    edges = []

    while remaining:
        best_edge = None
        best_distance = None
        for a in connected:
            for b in remaining:
                distance = math.dist(points[a], points[b])
                if best_distance is None or distance < best_distance:
                    best_distance = distance
                    best_edge = (a, b)

        a, b = best_edge
        edges.append((a, b))
        connected.add(b)
        remaining.remove(b)

    return edges


#Function to attach destinations with no company to whichever company has the nearest point
# Input is connections dict, list of all destinations, coordinates dict, Madrid's x and y. Changes connections in place.
def assign_unassigned_destinations(connections, destinations, coordinates, madrid_x, madrid_y):
    assigned_destinations = set()
    for served_destinations in connections.values():
        assigned_destinations.update(served_destinations)

    unassigned_destinations = set(destinations) - assigned_destinations

    if unassigned_destinations:
        print("Unassigned destinations:", unassigned_destinations)
        for destination in unassigned_destinations:
            best_company = None
            best_distance = None
            for company, served_destinations in connections.items():
                points = [(madrid_x, madrid_y)] + [coordinates[d] for d in served_destinations]
                for point in points:
                    distance = math.dist(coordinates[destination], point)
                    if best_distance is None or distance < best_distance:
                        best_distance = distance
                        best_company = company
            connections[best_company].append(destination)
            print(f"Assigned {destination} to {best_company} (nearest point was {round(best_distance, 1)} away)")
