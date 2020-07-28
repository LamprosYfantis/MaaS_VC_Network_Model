# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 14:29:06 2019

@author: Francisco
"""


# %matplotlib qt
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from functions import PathTT, import_data, dict_tt, add_edges, add_nodes, add_nodes_dual, graph, add_dummy_nodes, import_tt_turnings, add_dummy_edges, add_dual_edges, k_shortest_paths, dummy_dict, add_edge_attributes, update_dicts_tt  # update_dummy_tt, , update_tt
from networkx.classes.function import number_of_edges, number_of_nodes
import time

# 1.IMPORTING THE DATA

start = time.time()
nodes, l = import_data()


tt, tt_u = import_tt_turnings()


dict_tt = dict_tt(tt, tt_u)
dum_dict_tt = dummy_dict(tt, l)
end = time.time()
print('Running time: %f min' % ((end - start) / 60))
# 2. BUILDING THE ORIGINAL GRAPH (G)

G = nx.DiGraph()

# G=nx.MultiDiGraph()
# Adding the nodes with coordinates
add_nodes(G, nodes)


# Adding the edges with the id, travel time and length
add_edges(G, l)

# Graph of the network
# %matplotlib qt
# graph(G)


print(number_of_nodes(G))  # nodes = 95
print(number_of_edges(G))  # edges = 254


# 3. BUILDING THE DUAL GRAPH (H)
H = nx.DiGraph()

# adding the links of G as nodes of H
add_nodes_dual(H, l)

# Adding the nodes of G as H dummy nodes for origin and destination
H = add_dummy_nodes(H, nodes)  # functions

# add_dummy_nodes(H) ## functions 2

# Updating the tt
# start=time.time()
# dict_tt=update_tt(dict_tt,tt,'07:02:00',120,5)
dict_tt, dum_dict_tt = update_dicts_tt(dict_tt, dum_dict_tt, tt, '08:02:00', 0, 5)
# INPUT: dict_tt, tt:df with all the i min interval per link,
#                                 # t: time at the update is done, H: time horizon to update in min
#                                   # y: interval of the travel time per links in minutes
# end=time.time()
#print('Running time: %f s' %(end-start))

# dum_dict_tt=update_dummy_tt(dum_dict_tt,tt,'07:02:00',30,5)

# Adding the edges that links the dummy origins with the H  nodes (G edges)
# Adding the edges that links the the H  nodes (G edges) with the dummy destinations with the minimum travel time of the preceding G link (node in our case)
add_dummy_edges(H, l, tt_u)  # functions

# add_dual_edges(H) ## functions 2
#
# add_dummy_edges(H) ## functions 2


add_dual_edges(H, tt_u)  # functions


add_edge_attributes(H, dict_tt, dum_dict_tt)

# for n in H:
#     if H.nodes[n]['node_type'] == 'orig_dummy_node' or H.nodes[n]['node_type'] == 'dest_dummy_node':
#         print(H.nodes[n])

# TEST
#
# H.clear()
# H=nx.DiGraph()
#
# adding the links of G as nodes of H
# add_nodes_dual(H)
#
# Adding the nodes of G as H dummy nodes for origin and destination
#
# add_dummy_nodes(H)
#
#
# add_dual_edges(H)
#
# add_dummy_edges(H)
#
#
# add_edge_attributes(H)

# H.edges.data()

# print(G.number_of_nodes()) ## nodes = 95
# print(G.number_of_edges()) ## edges = 254
#
# print(H.number_of_nodes()) ## nodes = 444
# print(H.number_of_edges()) ## edges = 1029
#

for n in H.successors('105o'):
    print(n)
# print(nx.dijkstra_path(G,96,17,28000, weight='weight', timetable='departure_time'))##[80, 79]
# print(nx.dijkstra_path_length(G,96,17,28000, weight='weight', timetable='departure_time')) ##34.57
# start=time.time()
print(nx.dijkstra_path(H, '41o', '23d', 32400, weight='weight', timetable='departure_time', edge_type='edge_type'))  # [80, 79]
print(nx.dijkstra_path_length(H, '41o', '23d', 32400, weight='weight', timetable='departure_time', edge_type='edge_type'))  # 34.57
# end=time.time()
# print('Running time: %f min' %((end-start)/60))
#
#x=k_shortest_paths(G, 96, 17, 1000,weight='weight')
#
#
#
#PathTT(k_shortest_paths(G, 96, 17, 1000, weight='weight'),l,G)
#
#
