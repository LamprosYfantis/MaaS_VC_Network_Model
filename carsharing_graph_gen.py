# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 14:29:06 2019

@author: Francisco
"""


# %matplotlib qt

import networkx as nx
from carsharing_functions import import_data, dicts_tt, import_tt, dist, gen_station_stock, gen_sta_dict, gen_cs_cost_dicts, add_cs_dummy_nodes, add_cs_station_nodes, add_cs_dual_nodes, add_cs_dummy_edges, add_cs_dual_edges, add_cs_station_access_edges
import time


#------------------------------------------- Car-sharing Graph Generation------------------------------------------------

# 1.IMPORTING THE DATA

start = time.time()
nodes, l, l_dum = import_data()  # nodes: dict that contains Virtual City nodes data
# l: dict that contains VC links data
# l_dum: same as l but with the id of the from_nodes and to_nodes change to indicate the dual graph dummy nodes

tt = import_tt()  # tt: DF that contains the 24 h travel time per link and turning every 5 mins (source: simulator)
# NOTE: there is no information about some links at some time interval
# meaning that no car transverse this link at those time intervals.
# There are also some turnings that are not included in the 521 turning groups (CHECK THIS)
# They are generated during the simulation by Simmobility in case there is
# no path between OD, due to network misspecification , in order to allow a
# car to come back to the origin ( CHECK THIS)


# 2. Car sharing graph
cs_graph = nx.DiGraph()

cs_dual_tt_dict, cs_dum_tt_dict = dicts_tt(tt)  # tt_dual: offline dict that contains the travel times of the 521 turnings for the 288
# 5 min intervals with the default travel time as base
# tt_dum: offline dict that contains the travel times of the 254
# dummy destination edges for the 288 5 min intervals with the default
# travel time of the previous link as base

cs_dual_dist_dict, cs_dum_dist_dict = dist()
cs_sta_stock_level_dict = gen_station_stock()
cs_sta_dict = gen_sta_dict()

cs_dual_cost_dict, cs_dum_cost_dict = gen_cs_cost_dicts(cs_dual_tt_dict, cs_dum_tt_dict)

add_cs_dummy_nodes(cs_graph, nodes, cs_sta_dict)
add_cs_station_nodes(cs_graph, cs_sta_dict, cs_sta_stock_level_dict)

add_cs_dual_nodes(cs_graph, l_dum)

add_cs_dummy_edges(cs_graph, l_dum, cs_dum_tt_dict, cs_dum_dist_dict, cs_dum_cost_dict, cs_sta_dict)

add_cs_dual_edges(cs_graph, cs_dual_tt_dict, cs_dual_dist_dict, cs_dual_cost_dict)

add_cs_station_access_edges(cs_graph,cs_sta_dict, nodes,cs_dum_tt_dict, l ) 
end = time.time()
print('Running time: %f min' % ((end - start) / 60))

for node in cs_graph:
    if cs_graph.nodes[node]['node_type'] == 'car_sharing_station_node':
        print(node)
cs_graph.nodes()
print(cs_graph.number_of_nodes())  # 278 nodes : 8 station  nodes, 16 dummy nodes, 254 dual nodes
print(cs_graph.number_of_edges())  # 587 edges: 16 station access edges, 521 turnings/dual edges + 50 dummy edges

for e in cs_graph.edges:
    if cs_graph[e[0]][e[1]]['edge_type'] == 'car_sharing_orig_dummy_edge' or cs_graph[e[0]][e[1]]['edge_type'] == 'car_sharing_dest_dummy_edge' or cs_graph[e[0]][e[1]]['edge_type'] == 'car_sharing_dual_edge':
        print(cs_graph[e[0]][e[1]]['car_sharing_fares'])
