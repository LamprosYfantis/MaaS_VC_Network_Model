import networkx as nx
import matplotlib.pyplot as plt
import numpy.matlib
import numpy as np
import math
from sympy import Point, Line, Segment, Rational
from numpy.linalg import norm
from shapely.geometry import Point, LineString
import itertools

import math

from numpy.linalg import norm


def find_proj(point1=[], line_point1=[], line_point2=[]):
    point = Point(point1)
    line = LineString([line_point1, line_point2])

    x = np.array(point.coords[0])
    # print(x)

    u = np.array(line.coords[0])
    # print(u)
    v = np.array(line.coords[len(line.coords) - 1])
    # print(v)

    n = v - u
    # print(n)
    n /= np.linalg.norm(n, 2)

    P = u + n * np.dot(x - u, n)
    return(P)  # 0.2 1.


G = nx.DiGraph()

G.add_node('A', pos=[367331.249, 144005.3029])
G.add_node('B', pos=[366370.4542, 143969.6704])
G.add_node('Train', pos=[367055.7313, 144039.1658])
G.add_node('Bus', pos=[366918.5285, 143964.592])
G.add_edge('A', 'B')

proj = find_proj(G.nodes['Train']['pos'], G.nodes['A']['pos'], G.nodes['B']['pos'])
print(proj)
G.add_node('Proj', pos=proj)
dist_upstr = math.sqrt(sum([(a - b) ** 2 for a, b in zip(G.nodes['A']['pos'], proj)]))
print(dist_upstr)
dist_dstr = math.sqrt(sum([(a - b) ** 2 for a, b in zip(G.nodes['B']['pos'], proj)]))
print(dist_dstr)
print(math.sqrt(sum([(a - b) ** 2 for a, b in zip(G.nodes['B']['pos'], G.nodes['A']['pos'])])))
# G.add_node('A', pos=[370487.1528, 144024.4326])
# G.add_node('B', pos=[370518.9677, 143813.3622])
# G.add_node('C', pos=[370521.3343, 143448.4101])
# G.add_node('D', pos=[370466.5122, 143254.8797])
# G.add_node('E', pos=[370458.0543, 143038.335])
# G.add_node('F', pos=[370496.0977, 142771.4685])
# G.add_node('Bus', pos=[370528.447, 143607.8695])
# G.add_node('Train', pos=[370543.8614, 143687.5028])

# G.add_edge('A', 'B')
# G.add_edge('B', 'C')
# G.add_edge('C', 'D')
# G.add_edge('D', 'E')
# G.add_edge('E', 'F')

# ab = np.array([G.nodes['A']['pos'], G.nodes['B']['pos']])
# print(ab)
# ag = np.array([G.nodes['A']['pos'], G.nodes['Train']['pos']])
# proj = (ab * (np.dot(ag, ab) / np.dot(ab, ab)))  # G.nodes['A']['pos'] +
# ab = np.array([G.nodes['B']['pos'], G.nodes['A']['pos']])
# ag = np.array([G.nodes['B']['pos'], G.nodes['Train']['pos']])
# proj_dstr = ab * (np.dot(ag, ab) / np.dot(ab, ab))
# dist = math.sqrt(sum([(a - b) ** 2 for a, b in zip(proj[0], proj[1])]))
# dist_dstr = math.sqrt(sum([(a - b) ** 2 for a, b in zip(proj_dstr[0], proj_dstr[1])]))
# dist_2 = math.sqrt(sum([(a - b) ** 2 for a, b in zip(G.nodes['A']['pos'], G.nodes['B']['pos'])]))
# print(proj, proj_dstr)
# print(dist, dist_dstr, dist_2)

# print(math.sqrt(np.dot(proj, proj)))

# G.add_node('Proj', pos=[366912.57087494, 144182.60575952])
# G.add_node('Proj_dstr', pos=[367157.84216728, 143937.25390122])
pos = nx.get_node_attributes(G, 'pos')
nx.draw_networkx(G, pos)  # Graph with node attributes
plt.show()


# G = nx.DiGraph()


# import numpy as np
# from shapely.geometry import Point
# from shapely.geometry import LineString

# p1, p2, p3 = Point(0, 0), Point(1, 1), Point(Rational(1, 2), 0)
# >>> l1 = Line(p1, p2)
# >>> l1.projection(p3)
# point = Point(370543.8614, 143687.5028)
# line = LineString([(370492.4714, 142753.898), (370476.4156, 144039.822)])

# x = np.array(point.coords[0])

# u = np.array(line.coords[0])
# v = np.array(line.coords[len(line.coords) - 1])

# n = v - u
# n /= np.linalg.norm(n, 2)

# P = u + n * np.dot(x - u, n)
# print(P)  # 0.2 1.

# A = [1, 2]
# B = [2, 4]
# G = [1, 1]
# ab = np.array([A, B])
# ag = np.array([A, G])
# proj = A + np.dot(ag, ab) / np.dot(ab, ab) * ab
# print(proj[1])

# x = [1, 1]
# x.append(1)
# print(x)
# # V = {'1': 10, '2': 11}
# for i in range(len(V) - 1):
#     print(V[i])

# # import networkx as nx
# # from itertools import islice
# import math

# # G = nx.DiGraph()


# # G.add_edge('C', 'D', weight=3)
# # G.add_edge('C', 'E', weight=2)
# # G.add_edge('E', 'D', weight=1)
# # G.add_edge('E', 'F', weight=2)
# # G.add_edge('E', 'G', weight=3)
# # G.add_edge('D', 'F', weight=4)
# # G.add_edge('F', 'G', weight=2)
# # G.add_edge('F', 'H', weight=1)
# # G.add_edge('G', 'H', weight=2)


# # def k_shortest_paths(G, source, target, k, weight=None):
# #     return list(islice(nx.shortest_simple_paths(G, source, target, weight=weight), k))


# # for path in k_shortest_paths(G, 'C', 'H', 3):
# #     print(path)


# xlm = {'a': 12, 'b': 14, 'c': 18}

# xls = {'a': 20, 'd': 60, 'f': 90}

# xlm.update(xls)

# final = xlm.update(xls)

# print(final)
# B = {'1': 2, '2': 10}

# A = B
# print(A)

# A = ['1']

# B = A + ['2']

# print(B)

# A = [1, 2, 3]

# B = [1, 2, 3, 4]

# # A.insert(0, B)
# # print(A)

# A[:0] = B
# print(A)

# print(math.ceil(10))

# # lam = random.getrandbits(128)

# print(math.inf)

# print(1000000000000000000000000000000000000000000000000000000000000000000 < math.inf)
