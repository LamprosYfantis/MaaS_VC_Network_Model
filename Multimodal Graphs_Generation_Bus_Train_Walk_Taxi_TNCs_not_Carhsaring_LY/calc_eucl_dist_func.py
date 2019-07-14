import math


def haversine(coord1, coord2):
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


distance = haversine((51.549165, -0.221175), (51.551057, -0.222445))
# print(distance)


# Example points in 3-dimensional space...
x = (51.549165, -0.221175)
y = (51.551057, -0.222445)
distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(x, y)]))
# print("Euclidean distance from x to y: ", distance)
