# File to create prices for destinations for the user

import math

def price_from_distance(distance, min_distance, max_distance, min_price, max_price):
    # No range to scale across (e.g. only one possible path)
    if min_distance == max_distance:
        return round(min_price, 2)

    fraction = (distance - min_distance) / (max_distance - min_distance)
    price = min_price + fraction * (max_price - min_price)
    return round(price, 2)

def path_distance(start, finish, points, edges):
    graph = {}
    for name1, name2 in edges:
        edge_distance = math.dist(points[name1], points[name2])
        graph.setdefault(name1, []).append((name2, edge_distance))
        graph.setdefault(name2, []).append((name1, edge_distance))

    # BFS: a tree has only one path between two points
    visited = {start}
    queue = [(start, 0)]
    while queue:
        current, total = queue.pop(0)
        if current == finish:
            return total
        for neighbor, edge_distance in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, total + edge_distance))

    return None
