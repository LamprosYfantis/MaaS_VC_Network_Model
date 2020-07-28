# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 14:30:07 2019

@author: Fran
"""

import networkx as nx
from ehail_functions import gen_taxi_dist_dict, gen_taxi_cost_dict, gen_taxi_wt_dict, gen_taxi_tt_dict, gen_on_demand_taxi_single_wt_dict, gen_on_demand_taxi_single_tt_dict, gen_on_demand_taxi_shared_wt_dict, gen_on_demand_taxi_shared_tt_dict, add_taxi_nodes, add_taxi_edges, add_on_demand_taxi_single_nodes, add_on_demand_taxi_single_edges, add_on_demand_taxi_shared_nodes, add_on_demand_taxi_shared_edges
import time


#------------------------------------------- Taxi Graph Generation------------------------------------------------


start = time.time()

taxi_graph = nx.DiGraph()


taxi_taz_wt_dict = gen_taxi_wt_dict()  # Dict of waiting times for the 288 5min interval of the 24 zones
taxi_taz_tt_dict = gen_taxi_tt_dict()  # Dict of travel times for the 288 5min interval of the 576 pairs between zones
taxi_taz_dist_dict = gen_taxi_dist_dict('taxi')  # Dict of distances in km of the 576 pairs between zones
taxi_taz_cost_dict = gen_taxi_cost_dict(taxi_taz_tt_dict, taxi_taz_dist_dict, 'taxi')  # Dict of cost of the 576 pairs between zones

# print(ehail_taz_wt_dict)
# print(ehail_taz_tt_dict)
# print(ehail_taz_dist_dict)
# print(taxi_taz_cost_dict)

add_taxi_nodes(taxi_graph, taxi_taz_wt_dict)  # Add the 48 nodes (2 per zone, i: indicates incoming node, o: indicates outgoing) with the zone_id as an attribute)
add_taxi_edges(taxi_graph, taxi_taz_tt_dict, taxi_taz_wt_dict, taxi_taz_dist_dict, taxi_taz_cost_dict)  # Add the 576 edges between incoming and outgoing nodes with the travel time, waiting time, distance and cost as attributes
# for n, data in taxi_graph.adjacency():
#     for adj_node in data:
#         print(n, adj_node)
# end = time.time()
# print('Taxi graph generation time is {}min'.format((end - start) / 60))

print(taxi_graph['taxit1i']['taxit1o']['taxi_fares'])

#------------------------------------------- On-demand taxi single Graph Generation------------------------------------------------


# start = time.time()

# on_demand_taxi_single_graph = nx.DiGraph()


# on_demand_taxi_single_taz_wt_dict = gen_on_demand_taxi_single_wt_dict()  # Dict of waiting times for the 288 5min interval of the 24 zones
# on_demand_taxi_single_taz_tt_dict = gen_on_demand_taxi_single_tt_dict()  # Dict of travel times for the 288 5min interval of the 576 pairs between zones
# on_demand_taxi_single_taz_dist_dict = gen_taxi_dist_dict('single_taxi')  # Dict of distances in km of the 576 pairs between zones
# on_demand_taxi_single_taz_cost_dict = gen_taxi_cost_dict(on_demand_taxi_single_taz_tt_dict, on_demand_taxi_single_taz_dist_dict, 'single_taxi')  # Dict of cost of the 576 pairs between zones


# add_on_demand_taxi_single_nodes(on_demand_taxi_single_graph, on_demand_taxi_single_taz_wt_dict)  # Add the 48 nodes (2 per zone, i: indicates incoming node, o: indicates outgoing) with the zone_id as an attribute)
# add_on_demand_taxi_single_edges(on_demand_taxi_single_graph, on_demand_taxi_single_taz_tt_dict, on_demand_taxi_single_taz_wt_dict, on_demand_taxi_single_taz_dist_dict, on_demand_taxi_single_taz_cost_dict)  # Add the 576 edges between incoming and outgoing nodes with the travel time, waiting time, distance and cost as attributes

# # print(ehail_graph.edges(data=True))
# end = time.time()
# print('On-demand taxi single graph generation time is {}min'.format((end - start) / 60))

# print(on_demand_taxi_single_graph['SMSsin23i']['SMSsin19o']['taxi_fares'])
# print(on_demand_taxi_single_graph['SMSsin23i']['SMSsin19o']['distance'])

# #------------------------------------------- On-demand taxi shared Graph Generation------------------------------------------------


# # start = time.time()


# # on_demand_taxi_shared_graph = nx.DiGraph()


# # on_demand_taxi_shared_wt_dict = gen_on_demand_taxi_shared_wt_dict()  # Dict of waiting times for the 288 5min interval of the 24 zones
# # on_demand_taxi_shared_taz_tt_dict = gen_on_demand_taxi_shared_tt_dict()  # Dict of travel times for the 288 5min interval of the 576 pairs between zones
# # on_demand_taxi_shared_taz_dist_dict = gen_taxi_dist_dict('shared_taxi')  # Dict of distances in km of the 576 pairs between zones
# # on_demand_taxi_shared_taz_cost_dict = gen_taxi_cost_dict(on_demand_taxi_shared_taz_tt_dict, on_demand_taxi_shared_taz_dist_dict, 'shared_taxi')  # Dict of cost of the 576 pairs between zones

# # # print(ehail_taz_wt_dict)
# # # print(ehail_taz_tt_dict)
# # # print(ehail_taz_dist_dict)
# # # print(ehail_taz_cost_dict)

# # add_on_demand_taxi_shared_nodes(on_demand_taxi_shared_graph, on_demand_taxi_shared_wt_dict)  # Add the 48 nodes (2 per zone, i: indicates incoming node, o: indicates outgoing) with the zone_id as an attribute)
# # add_on_demand_taxi_shared_edges(on_demand_taxi_shared_graph, on_demand_taxi_shared_taz_tt_dict, on_demand_taxi_shared_wt_dict, on_demand_taxi_shared_taz_dist_dict, on_demand_taxi_shared_taz_cost_dict)  # Add the 576 edges between incoming and outgoing nodes with the travel time, waiting time, distance and cost as attributes

# # # print(ehail_graph.edges(data=True))
# # end = time.time()
# # print('On-demand taxi shared graph generation time is {}min'.format((end - start) / 60))
# # print(on_demand_taxi_shared_graph.nodes(data=True))
