import csv
import pandas as pd
import networkx as nx
import csv
import matplotlib.pyplot as plt
import time
from networkx.classes.function import number_of_edges, number_of_nodes
from bus_graph_gen_funct_with_hist_tt import gen_bus_stop_nodes, gen_bus_route_nodes, gen_bus_route_edges, gen_bus_dep_arr_timetable, gen_bus_route_edge_tt, gen_bus_route_node_transfer_edges, assign_bus_stop_access_nodes, assign_bus_edge_dep_timetable, gen_assign_bus_edge_zone_to_zone_cost, gen_assign_bus_route_edge_distances, gen_assign_bus_edge_distance_based_cost, plot_bus_graph, assign_bus_stop_access_nodes
from networkx.algorithms.shortest_paths.weighted import LY_shortest_path_with_attrs, _LY_dijkstra


bus_graph = nx.DiGraph()

csv_file_path = 'Bus_stops_coord.csv'
gen_bus_stop_nodes(bus_graph, csv_file_path)

csv_file_path1 = 'Bus_stops_coord.csv'
csv_file_path2 = 'journeytime.csv'
gen_bus_route_nodes(bus_graph, csv_file_path1, csv_file_path2)

gen_bus_route_edges(bus_graph)

csv_file_path = 'journeytime.csv'
bus_dep_times, bus_arr_times = gen_bus_dep_arr_timetable(bus_graph, csv_file_path)

assign_bus_edge_dep_timetable(bus_graph, bus_dep_times)

bus_route_edge_tts = gen_bus_route_edge_tt(bus_graph, bus_dep_times, bus_arr_times)

nx.set_edge_attributes(bus_graph, bus_route_edge_tts)

gen_bus_route_node_transfer_edges(bus_graph)

gen_assign_bus_route_edge_distances(bus_graph)

gen_assign_bus_edge_distance_based_cost(bus_graph)

gen_assign_bus_edge_zone_to_zone_cost(bus_graph)

assign_bus_stop_access_nodes(bus_graph)


# print(bus_graph.nodes['53009,2_1,1']['section_id'])
# print(bus_graph.nodes['52,2_1,2']['section_id'])
# for n in bus_graph:
#     if bus_graph.nodes[n]['node_type'] == 'stop_node':
#         print(n, bus_graph.nodes[n]['access_nodes_id'])
# for e in bus_graph.edges:
#     if bus_graph[e[0]][e[1]]['edge_type'] == 'pt_route_edge':
#         print(e)
# for n in bus_graph:
#     print(n)
# print(bus_graph['10,1_2,6']['7,1_2,7'])
# print(bus_graph.edges(data=True))
# # plot_bus_graph(bus_graph)
# origin = 'b57009'
# destination = 'b1009'
# request_time_sec = 20000
# # # # h = str(request_time_sec / 3600) if request_time_sec / 3600 >= 10 else '0' + str(request_time_sec / 3600)
# # # # m = str(request_time_sec % 3600 / 60) if request_time_sec % 3600 / 60 >= 10 else '0' + str(request_time_sec % 3600 / 60)
# # # # s = str(request_time_sec % 3600 % 60) if request_time_sec % 3600 % 60 >= 10 else '0' + str(request_time_sec % 3600 % 60)
# # # # request_time = h + ':' + m + ':' + s

# # # # # # timer = Timer()

# # # # print("hello")
# start = time.time()
# # # # # # with timer:
# best_weight, best_path, best_in_veh_tt, best_wait_time, best_walk_tt, best_distance, best_cost, best_num_line_transfers, best_num_mode_transfers, path_in_veh_tt_data, path_wait_time_data, path_walk_tt_data, path_distance_data, path_cost_data, path_line_trf_data, path_mode_trf_data = LY_shortest_path_with_attrs(bus_graph, origin, destination, request_time_sec, in_vehicle_tt='in_vehicle_tt', walk_tt='walk_tt', distance='distance', distance_based_cost='distance_based_cost', zone_to_zone_cost='zone_to_zone_cost', timetable='departure_time', edge_type='edge_type', node_type='node_type', fare_scheme='distance_based')  # init_in_vehicle_tt = 0, init_wait_time = 0, init_walking_tt = 0, init_distance = 0, init_cost = 0, init_num_line_trfs = 0, init_num_mode_trfs = 0, last_edge_type=None, last_pt_veh_run_id=None, last_edge_cost=0, pt_trip_orig_zone=None, pred=None, paths=None, cutoff=None)
# end = time.time()
# print(end - start)
# # eat_sec = nx.dijkstra_path_length(train_graph, origin, destination, request_time_sec, weight='weight', timetable='departure_time', edge_type='edge_type')
# # # # h = str(eat_sec / 3600) if eat_sec / 3600 >= 10 else '0' + str(eat_sec / 3600)
# # # # m = str(eat_sec % 3600 / 60) if eat_sec % 3600 / 60 >= 10 else '0' + str(eat_sec % 3600 / 60)
# # # # s = str(eat_sec % 3600 % 60) if eat_sec % 3600 % 60 >= 10 else '0' + str(eat_sec % 3600 % 60)
# # # # arrival_time = h + ':' + m + ':' + s
# # # #     # time.sleep(2)
# # # # # print(timer.duration_in_seconds())

# print('The shortest path is {} with weight {}'.format(best_path, best_weight))
# print('If a traveller leaves from {} to {} at {}, the earliest arrival time is {}'.format(origin, destination, request_time_sec, eat_sec))
# print(best_weight)
# print(best_path)
# print(sp_data)
