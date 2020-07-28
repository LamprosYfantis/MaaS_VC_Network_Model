import csv
import math
import time
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from mrt_graph_functions_with_hist_tt import gen_train_station_nodes, gen_train_route_nodes, gen_train_route_edges, gen_depart_and_arrival_timetable_data, gen_train_route_edge_tt, add_static_tt_to_missing_edge_tt, assign_route_edge_dep_timetable, gen_train_platform_transfer_edges, gen_assign_train_route_edge_distances, gen_assign_train_edge_distance_based_cost, gen_assign_train_edge_zone_to_zone_cost, assign_train_station_access_nodes
from networkx.classes.function import number_of_edges, number_of_nodes
from networkx.algorithms.operators.binary import union

train_graph = nx.DiGraph()

gen_train_station_nodes(train_graph)

gen_train_route_nodes(train_graph)

gen_train_route_edges(train_graph)

departure_timetable_dict, arrival_timetable_dict = gen_depart_and_arrival_timetable_data(train_graph)
# print(departure_timetable_dict)
# print(arrival_timetable_dict)

train_route_edges_tt_dict = gen_train_route_edge_tt(train_graph, departure_timetable_dict, arrival_timetable_dict)
# print(train_route_edges_tt_dict)

train_route_edges_tt_dict = add_static_tt_to_missing_edge_tt(train_graph, train_route_edges_tt_dict)
# print(train_route_edges_tt_dict)

# assign the list of travel times for each edge in our graph
nx.set_edge_attributes(train_graph, train_route_edges_tt_dict)  # at this point the travel times of the last edge of each line are missing because journeytime.csv doen't include the arrival times of the last node in each line, this info have to be taken from the station to station travel times csv

# assign the list of departure times for each edge in our graph
assign_route_edge_dep_timetable(train_graph, departure_timetable_dict)

gen_train_platform_transfer_edges(train_graph)

gen_assign_train_route_edge_distances(train_graph)

gen_assign_train_edge_distance_based_cost(train_graph)

gen_assign_train_edge_zone_to_zone_cost(train_graph)

assign_train_station_access_nodes(train_graph)

# train_graph_succ = train_graph._succ
# train_graph_succ = train_graph.neighbors
# # print(train_graph_succ['SC1'])
# # for n, data in train_graph_succ['SC1'].items():
# #     print(n, data)
# ignore_nodes = None

# if ignore_nodes:
#     def filter_iter(succ_nodes_dict):
#         def iterate(v):
#             for w, data in succ_nodes_dict[v].items():
#                 if w not in ignore_nodes:
#                     yield w, data
#         return iterate
#     train_graph_succ = filter_iter(train_graph_succ)

# yfa = train_graph_succ


# for n in yfa('SC1_1'):
#     print(n)


# print(train_graph['SC1']['SC1_1'])

# for node in train_graph:
#     if train_graph.nodes[node]['node_type'] == 'station_node':
#         print(train_graph.nodes[node]['access_links_id'])
# # for n in train_graph.successors('SC1'):
# #     print(n)

# print(train_graph_succ)

# for n, n_data in train_graph._succ['SC5'].items():
#     print(n, n_data)


# print(train_graph.nodes(data=True))
# print('The total number of nodes in G is {}'.format(number_of_nodes(train_graph)))
# print('The total number of edges in G is {}'.format(number_of_edges(train_graph)))
print(train_graph.edges(data=True))
# for e in train_graph.edges:
#     if train_graph[e[0]][e[1]]['edge_type'] == 'pt_route_edge':
#         print(e, train_graph[e[0]][e[1]]['distance'])

# print(train_graph.edges(data=True))
# plot_train_graph(train_graph)
# print(train_graph.nodes['NS4_1']['zone'])

# for e in train_graph.edges:
#     if train_graph[e[0]][e[1]]['edge_type'] == 'pt_route_edge':
#         print(train_graph[e[0]][e[1]]['departure_time'])
#         print('\n')

# origin = 'NS2/SC2'
# destination = 'NS4/SC4'    # 'w55' w93
# request_time_sec = 28920                # 28920 is 9am, 64800 is 6pm
# # # # h = str(request_time_sec / 3600) if request_time_sec / 3600 >= 10 else '0' + str(request_time_sec / 3600)
# # # # m = str(request_time_sec % 3600 / 60) if request_time_sec % 3600 / 60 >= 10 else '0' + str(request_time_sec % 3600 / 60)
# # # # s = str(request_time_sec % 3600 % 60) if request_time_sec % 3600 % 60 >= 10 else '0' + str(request_time_sec % 3600 % 60)
# # # # request_time = h + ':' + m + ':' + s
# # start = time.time()
# # best_weight, best_path, best_in_veh_tt, best_wait_time, best_walk_tt, best_distance, best_cost, best_num_line_transfers, best_num_mode_transfers, path_in_veh_tt_data, path_wait_time_data, path_walk_tt_data, path_distance_data, path_cost_data, path_line_trf_data, path_mode_trf_data = LY_shortest_path_with_attrs(int_train_bus_walk_graph, origin, destination, request_time_sec, in_vehicle_tt='in_vehicle_tt', walk_tt='walk_tt', distance='distance', distance_based_cost='distance_based_cost', zone_to_zone_cost='zone_to_zone_cost', timetable='departure_time', edge_type='edge_type', node_type='node_type', fare_scheme='distance_based')
# # end = time.time()
# # print('Algorithm path Running time: %f sec' % (end - start))

# start = time.time()
# for path in k_shortest_paths_LY(train_graph, origin, destination, request_time_sec, k=4, in_vehicle_tt='in_vehicle_tt', walk_tt='walk_tt', distance='distance', distance_based_cost='distance_based_cost', zone_to_zone_cost='zone_to_zone_cost', timetable='departure_time', edge_type='edge_type', node_type='node_type', fare_scheme='distance_based'):
#     print(path)
# end = time.time()
# print('Algorithm path Running time: %f sec' % (end - start))
# # eat_sec = nx.dijkstra_path_length(train_graph, origin, destination, request_time_sec, weight='weight', timetable='departure_time', edge_type='edge_type')
# # # # h = str(eat_sec / 3600) if eat_sec / 3600 >= 10 else '0' + str(eat_sec / 3600)
# # # m = str(eat_sec % 3600 / 60) if eat_sec % 3600 / 60 >= 10 else '0' + str(eat_sec % 3600 / 60)
# # # s = str(eat_sec % 3600 % 60) if eat_sec % 3600 % 60 >= 10 else '0' + str(eat_sec % 3600 % 60)
# # # arrival_time = h + ':' + m + ':' + s
# # #     # time.sleep(2)
# # # # print(timer.duration_in_seconds())

# print('The shortest path is {} with weight {}'.format(best_path, best_weight))
# print('If a traveller leaves from {} to {} at {}, the earliest arrival time is {}'.format(origin, destination, request_time_sec, eat_sec))
# print(best_weight)
# print(best_path)
# print(sp_data)
