import csv
import math
import time
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pedest_graph_gen_with_infra_funct import find_proj, gen_walk_graph_nodes_with_infra, gen_walk_graph_edges_with_attrs
from mrt_graph_functions_with_hist_tt import gen_train_station_nodes, gen_train_route_nodes, gen_train_route_edges, gen_depart_and_arrival_timetable_data, gen_train_route_edge_tt, add_static_tt_to_missing_edge_tt, assign_route_edge_dep_timetable, gen_train_platform_transfer_edges, gen_assign_train_route_edge_distances, gen_assign_train_edge_distance_based_cost, gen_assign_train_edge_zone_to_zone_cost, assign_train_station_access_nodes
from bus_graph_gen_funct_with_hist_tt import gen_bus_stop_nodes, gen_bus_route_nodes, gen_bus_route_edges, gen_bus_dep_arr_timetable, gen_bus_route_edge_tt, gen_bus_route_node_transfer_edges, assign_bus_stop_access_nodes, assign_bus_edge_dep_timetable, gen_assign_bus_edge_zone_to_zone_cost, gen_assign_bus_route_edge_distances, gen_assign_bus_edge_distance_based_cost, plot_bus_graph
from ehail_functions import gen_taxi_dist_dict, gen_taxi_cost_dict, gen_taxi_wt_dict, gen_taxi_tt_dict, gen_on_demand_taxi_single_wt_dict, gen_on_demand_taxi_single_tt_dict, gen_on_demand_taxi_shared_wt_dict, gen_on_demand_taxi_shared_tt_dict, add_taxi_nodes, add_taxi_edges, add_on_demand_taxi_single_nodes, add_on_demand_taxi_single_edges, add_on_demand_taxi_shared_nodes, add_on_demand_taxi_shared_edges
from networkx.classes.function import number_of_edges, number_of_nodes
from networkx.algorithms.operators.binary import union
from networkx.algorithms.simple_paths import k_shortest_paths_LY, shortest_simple_paths_LY, LY_shortest_path_with_attrs, _LY_dijkstra


#-----------------------------------Walk Graph Generation-------------------------------------------
start = time.time()

ped_graph = nx.DiGraph()

gen_walk_graph_nodes_with_infra(ped_graph)

gen_walk_graph_edges_with_attrs(ped_graph)

end = time.time()
print('Walk graph generation time: %f sec' % (end - start))

#------------------------------------------- Train Graph Generation------------------------------------------------
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
# print(train_graph.edges(data=True))
# print('The total number of nodes in G is {}'.format(number_of_nodes(train_graph)))
# print('The total number of edges in G is {}'.format(number_of_edges(train_graph)))
end = time.time()
print('Train graph generation time is {}sec'.format(end - start))

#------------------------------------------------------------------------------------------------------------

#---------------------------------------------Bus Graph Generation--------------------------------------
start = time.time()

bus_graph = nx.DiGraph()

gen_bus_stop_nodes(bus_graph)

gen_bus_route_nodes(bus_graph)

gen_bus_route_edges(bus_graph)

bus_dep_times, bus_arr_times = gen_bus_dep_arr_timetable(bus_graph)

assign_bus_edge_dep_timetable(bus_graph, bus_dep_times)

bus_route_edge_tts = gen_bus_route_edge_tt(bus_graph, bus_dep_times, bus_arr_times)

nx.set_edge_attributes(bus_graph, bus_route_edge_tts)

gen_bus_route_node_transfer_edges(bus_graph)

gen_assign_bus_route_edge_distances(bus_graph)

gen_assign_bus_edge_distance_based_cost(bus_graph)

gen_assign_bus_edge_zone_to_zone_cost(bus_graph)

end = time.time()
print('Bus graph generation time is {}sec'.format(end - start))
#----------------------------------------------------------------------------------------------------------------------------------

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
# print(ehail_taz_cost_dict)

add_taxi_nodes(taxi_graph, taxi_taz_wt_dict)  # Add the 48 nodes (2 per zone, i: indicates incoming node, o: indicates outgoing) with the zone_id as an attribute)
add_taxi_edges(taxi_graph, taxi_taz_tt_dict, taxi_taz_wt_dict, taxi_taz_dist_dict, taxi_taz_cost_dict)  # Add the 576 edges between incoming and outgoing nodes with the travel time, waiting time, distance and cost as attributes

# print(ehail_graph.edges(data=True))
end = time.time()
print('Taxi graph generation time is {}min'.format((end - start) / 60))


#------------------------------------------- On-demand single taxi Graph Generation------------------------------------------------

start = time.time()

on_demand_taxi_single_graph = nx.DiGraph()


on_demand_taxi_single_taz_wt_dict = gen_on_demand_taxi_single_wt_dict()  # Dict of waiting times for the 288 5min interval of the 24 zones
on_demand_taxi_single_taz_tt_dict = gen_on_demand_taxi_single_tt_dict()  # Dict of travel times for the 288 5min interval of the 576 pairs between zones
on_demand_taxi_single_taz_dist_dict = gen_taxi_dist_dict('single_taxi')  # Dict of distances in km of the 576 pairs between zones
on_demand_taxi_single_taz_cost_dict = gen_taxi_cost_dict(on_demand_taxi_single_taz_tt_dict, on_demand_taxi_single_taz_dist_dict, 'single_taxi')  # Dict of cost of the 576 pairs between zones


add_on_demand_taxi_single_nodes(on_demand_taxi_single_graph, on_demand_taxi_single_taz_wt_dict)  # Add the 48 nodes (2 per zone, i: indicates incoming node, o: indicates outgoing) with the zone_id as an attribute)
add_on_demand_taxi_single_edges(on_demand_taxi_single_graph, on_demand_taxi_single_taz_tt_dict, on_demand_taxi_single_taz_wt_dict, on_demand_taxi_single_taz_dist_dict, on_demand_taxi_single_taz_cost_dict)  # Add the 576 edges between incoming and outgoing nodes with the travel time, waiting time, distance and cost as attributes

# print(ehail_graph.edges(data=True))
end = time.time()
print('On-demand taxi single graph generation time is {}min'.format((end - start) / 60))


#------------------------------------------- On-demand shared taxi Graph Generation------------------------------------------------

start = time.time()


on_demand_taxi_shared_graph = nx.DiGraph()


on_demand_taxi_shared_wt_dict = gen_on_demand_taxi_shared_wt_dict()  # Dict of waiting times for the 288 5min interval of the 24 zones
on_demand_taxi_shared_taz_tt_dict = gen_on_demand_taxi_shared_tt_dict()  # Dict of travel times for the 288 5min interval of the 576 pairs between zones
on_demand_taxi_shared_taz_dist_dict = gen_taxi_dist_dict('shared_taxi')  # Dict of distances in km of the 576 pairs between zones
on_demand_taxi_shared_taz_cost_dict = gen_taxi_cost_dict(on_demand_taxi_shared_taz_tt_dict, on_demand_taxi_shared_taz_dist_dict, 'shared_taxi')  # Dict of cost of the 576 pairs between zones

# print(ehail_taz_wt_dict)
# print(ehail_taz_tt_dict)
# print(ehail_taz_dist_dict)
# print(ehail_taz_cost_dict)

add_on_demand_taxi_shared_nodes(on_demand_taxi_shared_graph, on_demand_taxi_shared_wt_dict)  # Add the 48 nodes (2 per zone, i: indicates incoming node, o: indicates outgoing) with the zone_id as an attribute)
add_on_demand_taxi_shared_edges(on_demand_taxi_shared_graph, on_demand_taxi_shared_taz_tt_dict, on_demand_taxi_shared_wt_dict, on_demand_taxi_shared_taz_dist_dict, on_demand_taxi_shared_taz_cost_dict)  # Add the 576 edges between incoming and outgoing nodes with the travel time, waiting time, distance and cost as attributes

# print(ehail_graph.edges(data=True))
end = time.time()
print('On-demand taxi shared graph generation time is {}min'.format((end - start) / 60))
############################----------------------------------------------------------#########################################


#---------------------------------------Integrated Multilayer Graph Generation------------------------------------------


# ------------- generation of access edges between walk graph and train graph------------------------

start = time.time()
int_train_walk_graph = union(train_graph, ped_graph, rename=(None, None), name=None)

for train_station in train_graph:
    if train_graph.nodes[train_station]['node_type'] == 'station_node':
        for walk_node in ped_graph:
            if walk_node == 'w_train_stop' + train_station:
                int_train_walk_graph.add_edge(train_station, 'w_train_stop' + train_station, edge_type='access_edge')
                int_train_walk_graph.add_edge('w_train_stop' + train_station, train_station, edge_type='access_edge')
                break

end = time.time()
print('Running time for walk_graph and train_graph integration: %f sec' % ((end - start)))

# #----------------------------generation of access edges between walk graph and bus graph----------------------------------

start = time.time()
int_train_bus_walk_graph = union(int_train_walk_graph, bus_graph, rename=(None, None), name=None)
for bus_stop in bus_graph:
    if bus_graph.nodes[bus_stop]['node_type'] == 'stop_node':
        for walk_node in ped_graph:
            if walk_node == 'w_bus_stop' + bus_graph.nodes[bus_stop]['id']:
                int_train_bus_walk_graph.add_edge(bus_stop, 'w_bus_stop' + bus_graph.nodes[bus_stop]['id'], edge_type='access_edge')
                int_train_bus_walk_graph.add_edge('w_bus_stop' + bus_graph.nodes[bus_stop]['id'], bus_stop, edge_type='access_edge')
                break

end = time.time()
print('Running time for walk_graph and train_graph integration: %f sec' % ((end - start)))

# i = 0
# for e in int_train_bus_walk_graph.edges:
#     if int_train_bus_walk_graph[e[0]][e[1]]['edge_type'] == 'access_edge':
#         i += 1
#         print(e)
# print(i)

# #------------------------generation of access edges between walk graph and taxi graph-------------------------------
int_trn_bus_walk_taxi_graph = union(int_train_bus_walk_graph, taxi_graph, rename=(None, None), name=None)

for walk_node in ped_graph:
    if not(ped_graph.nodes[walk_node]['is_mode_dupl']):  # connect only the walk nodes and not the rest infrastructure; this may change later on to be discussed
        for taxi_node in taxi_graph:
            if taxi_graph.nodes[taxi_node]['zone'] == 't' + ped_graph.nodes[walk_node]['zone']:
                if taxi_graph.nodes[taxi_node]['node_type'] == 'in_taxi_node':
                    int_trn_bus_walk_taxi_graph.add_edge(walk_node, taxi_node, edge_type='access_edge')
                elif taxi_graph.nodes[taxi_node]['node_type'] == 'out_taxi_node':
                    int_trn_bus_walk_taxi_graph.add_edge(taxi_node, walk_node, edge_type='access_edge')
# #----------------------------generation of access edges between walk graph and on-demand single graph----------------------------------

int_trn_bus_walk_taxi_ondemsngtx_graph = union(int_trn_bus_walk_taxi_graph, on_demand_taxi_single_graph, rename=(None, None), name=None)

for walk_node in ped_graph:
    if not(ped_graph.nodes[walk_node]['is_mode_dupl']):  # connect only the walk nodes and not the rest infrastructure; this may change later on to be discussed
        for taxi_node in on_demand_taxi_single_graph:
            if on_demand_taxi_single_graph.nodes[taxi_node]['zone'] == 'sin' + ped_graph.nodes[walk_node]['zone']:
                if on_demand_taxi_single_graph.nodes[taxi_node]['node_type'] == 'in_on_demand_taxi_single_node':
                    int_trn_bus_walk_taxi_ondemsngtx_graph.add_edge(walk_node, taxi_node, edge_type='access_edge')
                elif on_demand_taxi_single_graph.nodes[taxi_node]['node_type'] == 'out_on_demand_taxi_single_node':
                    int_trn_bus_walk_taxi_ondemsngtx_graph.add_edge(taxi_node, walk_node, edge_type='access_edge')

# #----------------------------generation of access edges between walk graph and on-demand-shared graph----------------------------------

pt_walk_TNCs_graph = union(int_trn_bus_walk_taxi_ondemsngtx_graph, on_demand_taxi_shared_graph, rename=(None, None), name=None)

for walk_node in ped_graph:
    if not(ped_graph.nodes[walk_node]['is_mode_dupl']):  # connect only the walk nodes and not the rest infrastructure; this may change later on to be discussed
        for taxi_node in on_demand_taxi_shared_graph:
            if on_demand_taxi_shared_graph.nodes[taxi_node]['zone'] == 'shar' + ped_graph.nodes[walk_node]['zone']:
                if on_demand_taxi_shared_graph.nodes[taxi_node]['node_type'] == 'in_on_demand_taxi_shared_node':
                    pt_walk_TNCs_graph.add_edge(walk_node, taxi_node, edge_type='access_edge')
                elif on_demand_taxi_shared_graph.nodes[taxi_node]['node_type'] == 'out_on_demand_taxi_shared_node':
                    pt_walk_TNCs_graph.add_edge(taxi_node, walk_node, edge_type='access_edge')

# print(bus_graph.number_of_nodes())
# print(train_graph.number_of_nodes())
# print(ped_graph.number_of_nodes())
# print(taxi_graph.number_of_nodes())
# print(on_demand_taxi_single_graph.number_of_nodes())
# print(on_demand_taxi_shared_graph.number_of_nodes())
#print(pt_walk_TNCs_graph.number_of_nodes())
#print(pt_walk_TNCs_graph.number_of_edges())
#for e in pt_walk_TNCs_graph.edges:
#    if pt_walk_TNCs_graph[e[0]][e[1]]['edge_type'] == 'access_edge':
#        print(e)
# i = 0
# for e in pt_walk_TNCs_graph.edges:
#     if pt_walk_TNCs_graph[e[0]][e[1]]['edge_type'] == 'access_edge':
#         i += 1
#         print(e)
# print(i)
# #############----------following script is for the connection with the dual road graph but it might need to be modified------------##############
# # # road_gr_orig_dest_dum_nodes = []
# # # for road_node in H:
# # #     if H.nodes[road_node]['node_type'] == 'orig_dummy_node' or H.nodes[road_node]['node_type'] == 'dest_dummy_node':
# # #         road_gr_orig_dest_dum_nodes.append(road_node)
# # # print(road_gr_orig_dest_dum_nodes, len(road_gr_orig_dest_dum_nodes))

# # # for walk_node in ped_graph:
# # #     for road_node in road_gr_orig_dest_dum_nodes:
# # #         if str(ped_graph.nodes[walk_node]['id']) == str(H.nodes[road_node]['id']):
# # #             int_train_bus_walk_road_graph.add_edge(walk_node, road_node, weight=0.001, timetable=None, edge_type='access_edge')
# # #             int_train_bus_walk_road_graph.add_edge(road_node, walk_node, weight=0.001, timetable=None, edge_type='access_edge')

# # end = time.time()
# # print('Multimodal graph generation time is {}sec'.format(end - start))
# # start = time.time()
# #
# #
# ########=---------- example if we receive a specific request from A to B and test the k-shortest path---------#######
origin = 'w60'  # 'SC1'  #
destination = 'w96'  # 'NS2/SC2'  # 'w6'    # 'w55' w93
request_time_sec = 28920                # 28920 is 9am, 64800 is 6pm
walk_attrs_weights = [1, 1, 0, 0, 0] ## weight of tt, wt, dist, cost, line trans, mode transf
bus_attrs_weights = [1, 1, 0, 0, 0]
train_attrs_weights = [1, 1, 0, 0, 0]
taxi_attrs_weights = [1, 1, 0, 0, 0]
sms_attrs_weight = [1, 1, 0, 0, 0]
sms_pool_attrs_weights = [1, 1, 0, 0, 0]
mode_trf_weights = 0

# # # h = str(request_time_sec / 3600) if request_time_sec / 3600 >= 10 else '0' + str(request_time_sec / 3600)
# # # m = str(request_time_sec % 3600 / 60) if request_time_sec % 3600 / 60 >= 10 else '0' + str(request_time_sec % 3600 / 60)
# # # s = str(request_time_sec % 3600 % 60) if request_time_sec % 3600 % 60 >= 10 else '0' + str(request_time_sec % 3600 % 60)
# # # request_time = h + ':' + m + ':' + s

start = time.time()

# best_weight, best_path, best_tt, best_wtt, best_dist, best_cost, best_num_line_transfers, best_num_mode_transfers, path_tt_data, path_wtt_data, path_dist_data, path_cost_data, path_line_trf_data, path_mode_trf_data, path_weight_labels, previous_edge_type_labels, previous_upstr_node_graph_type_labels, last_pt_vehicle_run_id_labels, current_time_labels, previous_edge_cost_labels, pt_trip_start_zone_labels, previous_edge_mode_labels = LY_shortest_path_with_attrs(pt_walk_TNCs_graph, origin, destination, request_time_sec, travel_time='travel_time', distance='distance', pt_additive_cost='pt_distance_based_cost', pt_non_additive_cost='pt_zone_to_zone_cost', taxi_fares='taxi_fares', taxi_wait_time='taxi_wait_time', timetable='departure_time', edge_type='edge_type', node_type='node_type', node_graph_type='node_graph_type', fare_scheme='distance_based', current_time=request_time_sec, walk_attrs_w=walk_attrs_weights, bus_attrs_w=bus_attrs_weights, train_attrs_w=train_attrs_weights, taxi_attrs_w=taxi_attrs_weights, sms_attrs_w=sms_attrs_weight, sms_pool_attrs_w=sms_pool_attrs_weights, mode_transfer_weight=mode_trf_weights)

# print(best_weight, best_path, best_tt, best_wtt, best_dist, best_cost, best_num_line_transfers, best_num_mode_transfers)
##distance_based
for path, data in k_shortest_paths_LY(pt_walk_TNCs_graph, origin, destination, request_time_sec, 10, travel_time='travel_time', distance='distance', pt_additive_cost='pt_distance_based_cost', pt_non_additive_cost='pt_zone_to_zone_cost', taxi_fares='taxi_fares', taxi_wait_time='taxi_wait_time', timetable='departure_time', edge_type='edge_type', node_type='node_type', node_graph_type='node_graph_type', fare_scheme='zone_to_zone', walk_attrs_w=walk_attrs_weights, bus_attrs_w=bus_attrs_weights, train_attrs_w=train_attrs_weights, taxi_attrs_w=taxi_attrs_weights, sms_attrs_w=sms_attrs_weight, sms_pool_attrs_w=sms_pool_attrs_weights, mode_transfer_weight=mode_trf_weights).items():
    print(path, data)
end = time.time()
print('Algorithm path Running time: %f sec' % (end - start))

#
#['w60', 'SMSsin23i', 'SMSsin19o', 'w96'] [952.0, 580.0, 372.0, 11.1533771941, 110.78, 0, 0]
#[path][sum of all the att, tt, wt, dist, cost, line trans, mode trans]




# # #------------------------------------------Road Graph Generation-----------------------------------
# # start = time.time()
# # # 1.IMPORTING THE DATA

# # # start = time.time()
# # nodes, l = import_data()

# # tt, tt_u = import_tt_turnings()


# # dict_tt = dict_tt(tt, tt_u)
# # dum_dict_tt = dummy_dict(tt, l)
# # # end = time.time()
# # # print('Running time: %f min' % ((end - start) / 60))
# # # # 2. BUILDING THE ORIGINAL GRAPH(G)

# # # G = nx.DiGraph()

# # # # G=nx.MultiDiGraph()
# # # # Adding the nodes with coordinates
# # # add_nodes(G, nodes)


# # # # Adding the edges with the id, travel time and length
# # # add_edges(G, l)

# # # print(G.nodes(data=True))
# # # # Graph of the network
# # # # %matplotlib qt
# # # # graph(G)


# # # # G.number_of_nodes()  # nodes = 95
# # # # G.number_of_edges()  # edges = 254

# # # test = union(train_graph, G, rename=(None, None), name=None)

# # # plot_train_graph(test)
# # # 3. BUILDING THE DUAL GRAPH (H)
# # H = nx.DiGraph()

# # # adding the links of G as nodes of H
# # add_nodes_dual(H, l)

# # # Adding the nodes of G as H dummy nodes for origin and destination
# # H = add_dummy_nodes(H, nodes)  # functions

# # # add_dummy_nodes(H) ## functions 2

# # # Updating the tt
# # # start=time.time()
# # # dict_tt = update_tt(dict_tt, tt, '07:02:00', 120, 5)
# # dict_tt, dum_dict_tt = update_dicts_tt(dict_tt, dum_dict_tt, tt, '08:02:00', 0, 5)
# # # INPUT: dict_tt, tt:df with all the i min interval per link,
# # #                                 # t: time at the update is done, H: time horizon to update in min
# # #                                   # y: interval of the travel time per links in minutes
# # # end=time.time()
# # # print('Running time: %f s' %(end-start))

# # # dum_dict_tt=update_dummy_tt(dum_dict_tt,tt,'07:02:00',30,5)

# # # Adding the edges that links the dummy origins with the H  nodes (G edges)
# # # Adding the edges that links the the H  nodes (G edges) with the dummy destinations with the minimum travel time of the preceding G link (node in our case)
# # add_dummy_edges(H, l, tt_u)  # functions

# # # add_dual_edges(H) ## functions 2
# # #
# # # add_dummy_edges(H) ## functions 2


# # add_dual_edges(H, tt_u)  # functions


# # add_edge_attributes(H, dict_tt, dum_dict_tt)

# # # for n in H:
# # #     if H.nodes[n]['node_type'] == 'orig_dummy_node' or H.nodes[n]['node_type'] == 'dest_dummy_node':
# # #         print(H.nodes[n])

# # # TEST
# # #
# # # H.clear()
# # # H=nx.DiGraph()
# # #
# # # adding the links of G as nodes of H
# # # add_nodes_dual(H)
# # #
# # # Adding the nodes of G as H dummy nodes for origin and destination
# # #
# # # add_dummy_nodes(H)
# # #
# # #
# # # add_dual_edges(H)
# # #
# # # add_dummy_edges(H)
# # #
# # #
# # # add_edge_attributes(H)

# # # H.edges.data()

# # # print(G.number_of_nodes()) ## nodes = 95
# # # print(G.number_of_edges()) ## edges = 254
# # #
# # # print(H.number_of_nodes()) ## nodes = 444
# # # print(H.number_of_edges()) ## edges = 1029
# # #


# # # print(nx.dijkstra_path(G,96,17,28000, weight='weight', timetable='departure_time'))##[80, 79]
# # # print(nx.dijkstra_path_length(G,96,17,28000, weight='weight', timetable='departure_time')) ##34.57
# # # start=time.time()
# # # print(nx.dijkstra_path(H, '78o', '93d',28920, weight='weight', timetable='departure_time', edge_type='edge_type')) ##[80, 79]
# # # print(nx.dijkstra_path_length(H,'78o', '93d',28920, weight='weight', timetable='departure_time', edge_type='edge_type')) ##34.57
# # # end=time.time()
# # # print('Running time: %f min' %((end-start)/60))
# # #
# # # x=k_shortest_paths(G, 96, 17, 1000,weight='weight')
# # #
# # #
# # #
# # # PathTT(k_shortest_paths(G, 96, 17, 1000, weight='weight'),l,G)
# # #
# # #
# # end = time.time()
# # print('Road network graph generation time is {}sec'.format(end - start))
