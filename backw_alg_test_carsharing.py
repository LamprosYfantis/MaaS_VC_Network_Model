import csv
import math
import time
import cProfile, pstats, io
import re
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import random
import statistics
from pedest_graph_gen_with_infra_funct import find_proj, gen_walk_graph_nodes_with_infra, gen_walk_graph_edges_with_attrs
from mrt_graph_functions_with_hist_tt import gen_train_station_nodes, gen_train_route_nodes, gen_train_route_edges, gen_depart_and_arrival_timetable_data, gen_train_route_edge_tt, add_static_tt_to_missing_edge_tt, assign_route_edge_dep_timetable, gen_train_platform_transfer_edges, gen_assign_train_route_edge_distances, gen_assign_train_edge_distance_based_cost, gen_assign_train_edge_zone_to_zone_cost, assign_train_station_access_nodes
from bus_graph_gen_funct_with_hist_tt import gen_bus_stop_nodes, gen_bus_route_nodes, gen_bus_route_edges, gen_bus_dep_arr_timetable, gen_bus_route_edge_tt, gen_bus_route_node_transfer_edges, assign_bus_stop_access_nodes, assign_bus_edge_dep_timetable, gen_assign_bus_edge_zone_to_zone_cost, gen_assign_bus_route_edge_distances, gen_assign_bus_edge_distance_based_cost
from ehail_functions import gen_taxi_dist_dict, gen_taxi_cost_dict, gen_taxi_wt_dict, gen_taxi_tt_dict, gen_on_demand_taxi_single_wt_dict, gen_on_demand_taxi_single_tt_dict, gen_on_demand_taxi_shared_wt_dict, gen_on_demand_taxi_shared_tt_dict, add_taxi_nodes, add_taxi_edges, add_on_demand_taxi_single_nodes, add_on_demand_taxi_single_edges, add_on_demand_taxi_shared_nodes, add_on_demand_taxi_shared_edges
from carsharing_functions import import_data, dicts_tt, import_tt, dist, gen_station_stock, gen_sta_dict, gen_cs_cost_dicts, add_cs_dummy_nodes, add_cs_station_nodes, add_cs_dual_nodes, add_cs_dummy_edges, add_cs_dual_edges, add_cs_station_access_edges
from networkx.classes.function import number_of_edges, number_of_nodes
from networkx.algorithms.operators.binary import union
from networkx.algorithms.simple_paths import k_shortest_paths_LY, shortest_simple_paths_LY,LY_shortest_path_with_attrs, \
_LY_dijkstra, pareto_paths_with_attrs, pareto_paths_with_attrs_backwards, pareto_paths_with_attrs_backwards_no_len


def profile(fnc):
    
    """A decorator that uses cProfile to profile a function"""
    
    def inner(*args, **kwargs):
        
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner


#-----------------------------------Walk Graph Generation-------------------------------------------
start = time.time()

ped_graph = nx.DiGraph()

gen_walk_graph_nodes_with_infra(ped_graph)

gen_walk_graph_edges_with_attrs(ped_graph)

end = time.time()
print('Walk graph generation time: %f sec' % (end - start))
print(ped_graph.number_of_nodes())
print(ped_graph.number_of_edges())
##------------------------------------------- Train Graph Generation------------------------------------------------
start = time.time()

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
print(train_graph.number_of_nodes())
print(train_graph.number_of_edges())
print(train_graph.nodes())

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
print(bus_graph.number_of_nodes())
print(bus_graph.number_of_edges())
print(bus_graph.nodes())
#----------------------------------------------------------------------------------------------------------------------------------

#------------------------------------------- Taxi Graph Generation------------------------------------------------
#start = time.time()
#
#taxi_graph = nx.DiGraph()
#
#
#taxi_taz_wt_dict = gen_taxi_wt_dict()  # Dict of waiting times for the 288 5min interval of the 24 zones
#taxi_taz_tt_dict = gen_taxi_tt_dict()  # Dict of travel times for the 288 5min interval of the 576 pairs between zones
#taxi_taz_dist_dict = gen_taxi_dist_dict('taxi')  # Dict of distances in km of the 576 pairs between zones
#taxi_taz_cost_dict = gen_taxi_cost_dict(taxi_taz_tt_dict, taxi_taz_dist_dict, 'taxi')  # Dict of cost of the 576 pairs between zones
#
## print(ehail_taz_wt_dict)
## print(ehail_taz_tt_dict)
## print(ehail_taz_dist_dict)
## print(ehail_taz_cost_dict)
#
#add_taxi_nodes(taxi_graph, taxi_taz_wt_dict)  # Add the 48 nodes (2 per zone, i: indicates incoming node, o: indicates outgoing) with the zone_id as an attribute)
#add_taxi_edges(taxi_graph, taxi_taz_tt_dict, taxi_taz_wt_dict, taxi_taz_dist_dict, taxi_taz_cost_dict)  # Add the 576 edges between incoming and outgoing nodes with the travel time, waiting time, distance and cost as attributes
#
## print(ehail_graph.edges(data=True))
#end = time.time()
#print('Taxi graph generation time is {}min'.format((end - start) / 60))
#print(taxi_graph.number_of_nodes())
#print(taxi_graph.number_of_edges())

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
print(on_demand_taxi_single_graph.number_of_nodes())
print(on_demand_taxi_single_graph.number_of_edges())

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
print(on_demand_taxi_shared_graph.number_of_nodes())
print(on_demand_taxi_shared_graph.number_of_edges())


#------------------------------------ Station-based Carsharing Graph Generation--------------------------
# 1.IMPORTING THE DATA

#start=time.time()
#nodes,l,l_dum=import_data() ## nodes: dict that contains Virtual City nodes data
#                             ## l: dict that contains VC links data
#                             ## l_dum: same as l but with the id of the from_nodes and to_nodes change to indicate the dual graph dummy nodes
#
#tt=import_tt() ## tt: DF that contains the 24 h travel time per link and turning every 5 mins (source: simulator)
                            ## NOTE: there is no information about some links at some time interval
                            ## meaning that no car transverse this link at those time intervals.
                            ## There are also some turnings that are not included in the 521 turning groups (CHECK THIS)
                            ## They are generated during the simulation by Simmobility in case there is
                            ## no path between OD, due to network misspecification , in order to allow a
                            ## car to come back to the origin ( CHECK THIS)


## 2. Car sharing graph
#cs_graph=nx.DiGraph()
#
#cs_dual_tt_dict,cs_dum_tt_dict=dicts_tt(tt) ## tt_dual: offline dict that contains the travel times of the 521 turnings for the 288
#                                ##5 min intervals with the default travel time as base
#                                ## tt_dum: offline dict that contains the travel times of the 254
#                                ## dummy destination edges for the 288 5 min intervals with the default
#                                ##travel time of the previous link as base
#
#cs_dual_dist_dict, cs_dum_dist_dict=dist()
#cs_sta_stock_level_dict= gen_station_stock()
#cs_sta_dict=gen_sta_dict()
#
#cs_dual_cost_dict, cs_dum_cost_dict = gen_cs_cost_dicts(cs_dual_tt_dict, cs_dum_tt_dict)
#
#add_cs_dummy_nodes(cs_graph, nodes, cs_sta_dict)
#add_cs_station_nodes(cs_graph,cs_sta_dict, cs_sta_stock_level_dict)
#
#add_cs_dual_nodes(cs_graph,l_dum)
#
#add_cs_dummy_edges(cs_graph,l_dum, cs_dum_tt_dict, cs_dum_dist_dict,cs_dum_cost_dict, cs_sta_dict)
#
#add_cs_dual_edges(cs_graph,cs_dual_tt_dict, cs_dual_dist_dict,cs_dual_cost_dict)
#
#add_cs_station_access_edges(cs_graph,cs_sta_dict, nodes,cs_dum_tt_dict, l)
#
#end=time.time()
#print('Running time: %f min' %((end-start)/60))
#print(cs_graph.number_of_nodes())
#print(cs_graph.number_of_edges())
#
##
#----------------------------------Integrated Multilayer Graph Generation-----------------------------


# ------------- generation of access edges between walk graph and train graph------------------------

start = time.time()
int_train_walk_graph = union(train_graph, ped_graph, rename=(None, None), name=None)

for train_station in train_graph:
    if train_graph.nodes[train_station]['node_type'] == 'station_node':
        for walk_node in ped_graph:
            if walk_node == 'w_train_stop' + train_station:
                int_train_walk_graph.add_edge(train_station, 'w_train_stop' + train_station, edge_type='access_edge', \
                                              up_node_graph_type=int_train_walk_graph.nodes[train_station]['node_graph_type'], \
                                              dstr_node_graph_type=int_train_walk_graph.nodes['w_train_stop' + train_station]['node_graph_type'], \
                                              up_node_type=int_train_walk_graph.nodes[train_station]['node_type'], \
                                              dstr_node_type=int_train_walk_graph.nodes['w_train_stop' + train_station]['node_type'], \
                                              up_node_zone=int_train_walk_graph.nodes[train_station]['zone'], \
                                              dstr_node_zone=int_train_walk_graph.nodes['w_train_stop' + train_station]['zone'])
                int_train_walk_graph.add_edge('w_train_stop' + train_station, train_station, edge_type='access_edge', \
                                              up_node_graph_type=int_train_walk_graph.nodes['w_train_stop' + train_station]['node_graph_type'], \
                                              dstr_node_graph_type=int_train_walk_graph.nodes[train_station]['node_graph_type'], \
                                              up_node_type=int_train_walk_graph.nodes['w_train_stop' + train_station]['node_type'], \
                                              dstr_node_type=int_train_walk_graph.nodes[train_station]['node_type'], \
                                              up_node_zone=int_train_walk_graph.nodes['w_train_stop' + train_station]['zone'], \
                                              dstr_node_zone=int_train_walk_graph.nodes[train_station]['zone'])
                break


## #----------------------generation of access edges between walk graph and bus graph----------------------------

start = time.time()
int_train_bus_walk_graph = union(int_train_walk_graph, bus_graph, rename=(None, None), name=None)
for bus_stop in bus_graph:
    if bus_graph.nodes[bus_stop]['node_type'] == 'stop_node':
        for walk_node in ped_graph:
            if walk_node == 'w_bus_stop' + bus_graph.nodes[bus_stop]['id']:
                int_train_bus_walk_graph.add_edge(bus_stop, 'w_bus_stop' + bus_graph.nodes[bus_stop]['id'], edge_type='access_edge', \
                                              up_node_graph_type=int_train_bus_walk_graph.nodes[bus_stop]['node_graph_type'], \
                                              dstr_node_graph_type=int_train_bus_walk_graph.nodes['w_bus_stop' + bus_graph.nodes[bus_stop]['id']]['node_graph_type'], \
                                              up_node_type=int_train_bus_walk_graph.nodes[bus_stop]['node_type'], \
                                              dstr_node_type=int_train_bus_walk_graph.nodes['w_bus_stop' + bus_graph.nodes[bus_stop]['id']]['node_type'], \
                                              up_node_zone=int_train_bus_walk_graph.nodes[bus_stop]['zone'], \
                                              dstr_node_zone=int_train_bus_walk_graph.nodes['w_bus_stop' + bus_graph.nodes[bus_stop]['id']]['zone'])
                int_train_bus_walk_graph.add_edge('w_bus_stop' + bus_graph.nodes[bus_stop]['id'], bus_stop, edge_type='access_edge', \
                                              up_node_graph_type=int_train_bus_walk_graph.nodes['w_bus_stop' + bus_graph.nodes[bus_stop]['id']]['node_graph_type'], \
                                              dstr_node_graph_type=int_train_bus_walk_graph.nodes[bus_stop]['node_graph_type'], \
                                              up_node_type=int_train_bus_walk_graph.nodes['w_bus_stop' + bus_graph.nodes[bus_stop]['id']]['node_type'], \
                                              dstr_node_type=int_train_bus_walk_graph.nodes[bus_stop]['node_type'], \
                                              up_node_zone=int_train_bus_walk_graph.nodes['w_bus_stop' + bus_graph.nodes[bus_stop]['id']]['zone'], \
                                              dstr_node_zone=int_train_bus_walk_graph.nodes[bus_stop]['zone'])
                break



# i = 0
# for e in int_train_bus_walk_graph.edges:
#     if int_train_bus_walk_graph[e[0]][e[1]]['edge_type'] == 'access_edge':
#         i += 1
#         print(e)
# print(i)

## #------------------------generation of access edges between walk graph and taxi graph-------------------------------
#int_trn_bus_walk_taxi_graph = union(int_train_walk_graph, taxi_graph, rename=(None, None), name=None)
#
#for walk_node in ped_graph:
#    if not(ped_graph.nodes[walk_node]['is_mode_dupl']):  # connect only the walk nodes and not the rest infrastructure; this may change later on to be discussed
#        for taxi_node in taxi_graph:
#            if taxi_graph.nodes[taxi_node]['zone'] == 't' + ped_graph.nodes[walk_node]['zone']:
#                if taxi_graph.nodes[taxi_node]['node_type'] == 'in_taxi_node':
#                    int_trn_bus_walk_taxi_graph.add_edge(walk_node, taxi_node, edge_type='access_edge', \
#                                              up_node_graph_type=int_trn_bus_walk_taxi_graph.nodes[walk_node]['node_graph_type'], \
#                                              dstr_node_graph_type=int_trn_bus_walk_taxi_graph.nodes[taxi_node]['node_graph_type'], \
#                                              up_node_type=int_trn_bus_walk_taxi_graph.nodes[walk_node]['node_type'], \
#                                              dstr_node_type=int_trn_bus_walk_taxi_graph.nodes[taxi_node]['node_type'], \
#                                              up_node_zone=int_trn_bus_walk_taxi_graph.nodes[walk_node]['zone'], \
#                                              dstr_node_zone=int_trn_bus_walk_taxi_graph.nodes[taxi_node]['zone'])
#                elif taxi_graph.nodes[taxi_node]['node_type'] == 'out_taxi_node':
#                    int_trn_bus_walk_taxi_graph.add_edge(taxi_node, walk_node, edge_type='access_edge', \
#                                              up_node_graph_type=int_trn_bus_walk_taxi_graph.nodes[taxi_node]['node_graph_type'], \
#                                              dstr_node_graph_type=int_trn_bus_walk_taxi_graph.nodes[walk_node]['node_graph_type'], \
#                                              up_node_type=int_trn_bus_walk_taxi_graph.nodes[taxi_node]['node_type'], \
#                                              dstr_node_type=int_trn_bus_walk_taxi_graph.nodes[walk_node]['node_type'], \
#                                              up_node_zone=int_trn_bus_walk_taxi_graph.nodes[taxi_node]['zone'], \
#                                              dstr_node_zone=int_trn_bus_walk_taxi_graph.nodes[walk_node]['zone'])
## #--------------------generation of access edges between walk graph and on-demand single graph---------------------
#
int_trn_bus_walk_taxi_ondemsngtx_graph = union(int_train_bus_walk_graph, on_demand_taxi_single_graph, rename=(None, None), name=None)

for walk_node in ped_graph:
    if not(ped_graph.nodes[walk_node]['is_mode_dupl']):  # connect only the walk nodes and not the rest infrastructure; this may change later on to be discusse; if it changes then we need to consider the zone mapping and the existing zone attributes
        for taxi_node in on_demand_taxi_single_graph:
            if on_demand_taxi_single_graph.nodes[taxi_node]['zone'] == 'sin' + ped_graph.nodes[walk_node]['zone']:
                if on_demand_taxi_single_graph.nodes[taxi_node]['node_type'] == 'in_on_demand_taxi_single_node':
                    int_trn_bus_walk_taxi_ondemsngtx_graph.add_edge(walk_node, taxi_node, edge_type='access_edge', \
                                              up_node_graph_type=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[walk_node]['node_graph_type'], \
                                              dstr_node_graph_type=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[taxi_node]['node_graph_type'], \
                                              up_node_type=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[walk_node]['node_type'], \
                                              dstr_node_type=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[taxi_node]['node_type'], \
                                              up_node_zone=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[walk_node]['zone'], \
                                              dstr_node_zone=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[taxi_node]['zone'])
                elif on_demand_taxi_single_graph.nodes[taxi_node]['node_type'] == 'out_on_demand_taxi_single_node':
                    int_trn_bus_walk_taxi_ondemsngtx_graph.add_edge(taxi_node, walk_node, edge_type='access_edge', \
                                              up_node_graph_type=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[taxi_node]['node_graph_type'], \
                                              dstr_node_graph_type=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[walk_node]['node_graph_type'], \
                                              up_node_type=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[taxi_node]['node_type'], \
                                              dstr_node_type=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[walk_node]['node_type'], \
                                              up_node_zone=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[taxi_node]['zone'], \
                                              dstr_node_zone=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[walk_node]['zone'])
#
## #-----------------generation of access edges between walk graph and on-demand-shared graph-----------------------
#
pt_walk_TNCs_graph = union(int_trn_bus_walk_taxi_ondemsngtx_graph, on_demand_taxi_shared_graph, rename=(None, None), name=None)

for walk_node in ped_graph:
    if not(ped_graph.nodes[walk_node]['is_mode_dupl']):  # connect only the walk nodes and not the rest infrastructure; this may change later on to be discussed
        for taxi_node in on_demand_taxi_shared_graph:
            if on_demand_taxi_shared_graph.nodes[taxi_node]['zone'] == 'shar' + ped_graph.nodes[walk_node]['zone']:
                if on_demand_taxi_shared_graph.nodes[taxi_node]['node_type'] == 'in_on_demand_taxi_shared_node':
                    pt_walk_TNCs_graph.add_edge(walk_node, taxi_node, edge_type='access_edge', \
                                              up_node_graph_type=pt_walk_TNCs_graph.nodes[walk_node]['node_graph_type'], \
                                              dstr_node_graph_type=pt_walk_TNCs_graph.nodes[taxi_node]['node_graph_type'], \
                                              up_node_type=pt_walk_TNCs_graph.nodes[walk_node]['node_type'], \
                                              dstr_node_type=pt_walk_TNCs_graph.nodes[taxi_node]['node_type'], \
                                              up_node_zone=pt_walk_TNCs_graph.nodes[walk_node]['zone'], \
                                              dstr_node_zone=pt_walk_TNCs_graph.nodes[taxi_node]['zone'])
                elif on_demand_taxi_shared_graph.nodes[taxi_node]['node_type'] == 'out_on_demand_taxi_shared_node':
                    pt_walk_TNCs_graph.add_edge(taxi_node, walk_node, edge_type='access_edge', \
                                              up_node_graph_type=pt_walk_TNCs_graph.nodes[taxi_node]['node_graph_type'], \
                                              dstr_node_graph_type=pt_walk_TNCs_graph.nodes[walk_node]['node_graph_type'], \
                                              up_node_type=pt_walk_TNCs_graph.nodes[taxi_node]['node_type'], \
                                              dstr_node_type=pt_walk_TNCs_graph.nodes[walk_node]['node_type'], \
                                              up_node_zone=pt_walk_TNCs_graph.nodes[taxi_node]['zone'], \
                                              dstr_node_zone=pt_walk_TNCs_graph.nodes[walk_node]['zone'])
#
#
## ------------ generation of access edges between walk graph and carsharing graph--------------------
#pt_walk_TNCs_cs_graph = union(int_train_bus_walk_graph, cs_graph, rename=(None, None), name=None)
#
#for station in cs_graph:
#    if cs_graph.nodes[station]['node_type'] == 'car_sharing_station_node':
#        pt_walk_TNCs_cs_graph.add_edge(station, 'w_crs_station'+cs_graph.nodes[station]['id'], edge_type='access_edge', \
#                                              up_node_graph_type=pt_walk_TNCs_cs_graph.nodes[station]['node_graph_type'], \
#                                              dstr_node_graph_type=pt_walk_TNCs_cs_graph.nodes['w_crs_station'+cs_graph.nodes[station]['id']]['node_graph_type'], \
#                                              up_node_type=pt_walk_TNCs_cs_graph.nodes[station]['node_type'], \
#                                              dstr_node_type=pt_walk_TNCs_cs_graph.nodes['w_crs_station'+cs_graph.nodes[station]['id']]['node_type'])
#        pt_walk_TNCs_cs_graph.add_edge('w_crs_station'+cs_graph.nodes[station]['id'], station, edge_type='access_edge', \
#                                              up_node_graph_type=pt_walk_TNCs_cs_graph.nodes['w_crs_station'+cs_graph.nodes[station]['id']]['node_graph_type'], \
#                                              dstr_node_graph_type=pt_walk_TNCs_cs_graph.nodes[station]['node_graph_type'], \
#                                              up_node_type=pt_walk_TNCs_cs_graph.nodes['w_crs_station'+cs_graph.nodes[station]['id']]['node_type'], \
#                                              dstr_node_type=pt_walk_TNCs_cs_graph.nodes[station]['node_type'])
#end = time.time()
#
print(pt_walk_TNCs_graph.number_of_nodes())
print(pt_walk_TNCs_graph.number_of_edges())
print('Running time for graph integration: %f sec' % ((end - start)))
#print(pt_walk_TNCs_cs_graph.number_of_nodes())
#print(pt_walk_TNCs_cs_graph.number_of_edges())




#for path in nx.all_simple_paths(pt_walk_TNCs_cs_graph, source='w60', target='w96'):
#    print(path)

#for e in pt_walk_TNCs_cs_graph.edges:
#    if e[0] == 'w_train_stopNS2/SC2':
#        print(pt_walk_TNCs_cs_graph[e[0]][e[1]])
        
#print(pt_walk_TNCs_cs_graph.nodes['w_train_stopNS2/SC2']['access_segs_id'])
#print(pt_walk_TNCs_cs_graph.nodes['w_bus_stop19']['access_segs_id'])
#print(pt_walk_TNCs_cs_graph.nodes['w_bus_stop18']['access_segs_id'])
# code for creating random OD queries from walk graph nodes in the VC
#nodes=list()
#for node in ped_graph.nodes():
#    nodes.append(node)
#
#perm=permutations(nodes,2)   
#perm=list(perm)
#
#OD_pairs=list()
#for i in range(500):
#    OD_pairs.append(random.choice(perm))
#
#
## # ########=---------- example if we receive a specific request from A to B and test the k-shortest path---------#######
#runtimes = []
#for pair in OD_pairs:
#origin = 'w8'  # 'SC1'  #
#destination = 'w94'  # 'NS2/SC2'  # 'w6'    # 'w55' w93
OD_pair = ('w52', 'w6')
request_time_sec = 28800                # 28920 is 9am, 64800 is 6pm
#
##walk_attrs_weights = [1, 1, 0, 0, 0]  # weight of tt, wt, dist, cost, line trans, mode transf (DKK/sec)
##bus_attrs_weights = [1, 1, 0, 0, 0]
##train_attrs_weights = [1, 1, 0, 0, 0]
##taxi_attrs_weights = [1, 1, 0, 0, 0]
##sms_attrs_weight = [1, 1, 0, 0, 0]
##sms_pool_attrs_weights = [1, 1, 0, 0, 0]
##carsharing_attrs_weights = [1, 1, 0, 0, 0]
##mode_trf_weights = 0
#walk_attrs_weights = [0.0467, 0, 0, 1, 0]  # weight of tt, wt, l, c, lt
#bus_attrs_weights = [0.0417, 0.05, 0, 1, 15]
#train_attrs_weights = [0.0417, 0.05, 0, 1, 15]
#taxi_attrs_weights = [0.0667, 0.075, 0, 1, 0]
#sms_attrs_weight = [0.05, 0.075, 0, 1, 0]
#sms_pool_attrs_weights = [0.0433, 0.075, 0, 1, 0]
#carsharing_attrs_weights = [0.0375, 0.05, 0.0015, 1, 0]
#mode_trf_weights = 15   # mt
#
## # # h = str(request_time_sec / 3600) if request_time_sec / 3600 >= 10 else '0' + str(request_time_sec / 3600)
## # # m = str(request_time_sec % 3600 / 60) if request_time_sec % 3600 / 60 >= 10 else '0' + str(request_time_sec % 3600 / 60)
## # # s = str(request_time_sec % 3600 % 60) if request_time_sec % 3600 % 60 >= 10 else '0' + str(request_time_sec % 3600 % 60)
## # # request_time = h + ':' + m + ':' + s
#
#
## Time-dependent Dijkstra
## best_weight, best_path, best_tt, best_wtt, best_dist, best_cost, best_num_line_transfers, best_num_mode_transfers, path_tt_data, path_wtt_data, path_dist_data, path_cost_data, path_line_trf_data, path_mode_trf_data, path_weight_labels, previous_edge_type_labels, previous_upstr_node_graph_type_labels, last_pt_vehicle_run_id_labels, current_time_labels, previous_edge_cost_labels, pt_trip_start_zone_labels, previous_edge_mode_labels = LY_shortest_path_with_attrs(pt_walk_TNCs_graph, origin, destination, request_time_sec, travel_time='travel_time', distance='distance', pt_additive_cost='pt_distance_based_cost', pt_non_additive_cost='pt_zone_to_zone_cost', taxi_fares='taxi_fares', taxi_wait_time='taxi_wait_time', timetable='departure_time', edge_type='edge_type', node_type='node_type', node_graph_type='node_graph_type', fare_scheme='fare_scheme', ignore_nodes=None, ignore_edges=None, current_time=request_time_sec, walk_attrs_w=walk_attrs_weights, bus_attrs_w=bus_attrs_weights, train_attrs_w=train_attrs_weights, taxi_attrs_w=taxi_attrs_weights, sms_attrs_w=sms_attrs_weight, sms_pool_attrs_w=sms_pool_attrs_weights, mode_transfer_weight=mode_trf_weights, paths=None)
#
## Time-dependent K-shortest Path algorithm
##@profile
##def elamou():
##    k_shortest_paths_LY(pt_walk_TNCs_cs_graph, OD_pair[0], OD_pair[1], request_time_sec, 20, travel_time='travel_time', distance='distance', \
##                        pt_additive_cost='pt_distance_based_cost', pt_non_additive_cost='pt_zone_to_zone_cost', taxi_fares='taxi_fares', \
##                        taxi_wait_time='taxi_wait_time', timetable='departure_time', edge_type='edge_type', node_type='node_type', \
##                        node_graph_type='node_graph_type', fare_scheme='zone_to_zone', walk_attrs_w=walk_attrs_weights, \
##                        bus_attrs_w=bus_attrs_weights, train_attrs_w=train_attrs_weights, taxi_attrs_w=taxi_attrs_weights, \
##                        sms_attrs_w=sms_attrs_weight, sms_pool_attrs_w=sms_pool_attrs_weights, cs_attrs_w=carsharing_attrs_weights, \
##                        mode_transfer_weight=mode_trf_weights)
##
##elamou()
#    
#
#for path, data in k_shortest_paths_LY(pt_walk_TNCs_cs_graph, OD_pair[0], OD_pair[1], request_time_sec, 50, travel_time='travel_time', distance='distance', pt_additive_cost='pt_distance_based_cost', pt_non_additive_cost='pt_zone_to_zone_cost', taxi_fares='taxi_fares', taxi_wait_time='taxi_wait_time', timetable='departure_time', edge_type='edge_type', node_type='node_type', node_graph_type='node_graph_type', fare_scheme='zone_to_zone', walk_attrs_w=walk_attrs_weights, bus_attrs_w=bus_attrs_weights, train_attrs_w=train_attrs_weights, taxi_attrs_w=taxi_attrs_weights, sms_attrs_w=sms_attrs_weight, sms_pool_attrs_w=sms_pool_attrs_weights, cs_attrs_w=carsharing_attrs_weights, mode_transfer_weight=mode_trf_weights).items():
#    print(path, data)
#
#@profile
#def elamou():
start = time.time()
pareto_paths = pareto_paths_with_attrs_backwards_no_len(pt_walk_TNCs_graph, OD_pair[0], OD_pair[1], request_time_sec, request_time_sec, 
                                         request_time_sec+3600, 20, travel_time='travel_time', distance='distance', \
                                         pt_additive_cost='pt_distance_based_cost', pt_non_additive_cost='pt_zone_to_zone_cost', \
                                         taxi_fares='taxi_fares', taxi_wait_time='taxi_wait_time', timetable='departure_time', \
                                         edge_type='edge_type', node_type='node_type', node_graph_type='node_graph_type', \
                                         fare_scheme='distance_based')
##    best_weight, best_path, best_tt, best_wtt, best_dist, best_cost, best_num_line_transfers, best_num_mode_transfers, path_tt_data, path_wtt_data, path_dist_data, path_cost_data, path_line_trf_data, path_mode_trf_data, path_weight_labels, previous_edge_type_labels, previous_upstr_node_graph_type_labels, last_pt_vehicle_run_id_labels, current_time_labels, previous_edge_cost_labels, pt_trip_start_zone_labels, previous_edge_mode_labels = LY_shortest_path_with_attrs(pt_walk_TNCs_cs_graph, origin, destination, request_time_sec, travel_time='travel_time', distance='distance', pt_additive_cost='pt_distance_based_cost', pt_non_additive_cost='pt_zone_to_zone_cost', taxi_fares='taxi_fares', taxi_wait_time='taxi_wait_time', timetable='departure_time', edge_type='edge_type', node_type='node_type', node_graph_type='node_graph_type', fare_scheme='zone_to_zone', ignore_nodes=None, ignore_edges=None, current_time=request_time_sec, walk_attrs_w=walk_attrs_weights, bus_attrs_w=bus_attrs_weights, train_attrs_w=train_attrs_weights, taxi_attrs_w=taxi_attrs_weights, sms_attrs_w=sms_attrs_weight, sms_pool_attrs_w=sms_pool_attrs_weights, cs_attrs_w=carsharing_attrs_weights, mode_transfer_weight=mode_trf_weights, orig_source=origin)
##
#elamou()
##print(best_weight, best_path, best_tt, best_wtt, best_dist, best_cost, best_num_line_transfers, best_num_mode_transfers)

# Pareto set of optimal paths


end = time.time()
print('Algorithm path Running time: %f sec' % (end - start))
print(pareto_paths)

#runtimes.append(end-start)
#    
#    
#average_CPU = sum(runtimes)/len(runtimes)
#print(average_CPU)
#stdv = statistics.stdev(runtimes)
#print(stdv)
#
oops = False
for path1, attrs1 in pareto_paths.items():
    for path2, attrs2 in pareto_paths.items():
        if path1 == path2 and attrs1 == attrs2:
            continue
        if attrs1['optimal_crt_values'] == attrs2['optimal_crt_values']:
            continue
        if len([True for i,j in zip(attrs1['optimal_crt_values'],attrs2['optimal_crt_values']) if i>=j]) == len(attrs1['optimal_crt_values']):
            oops = True
            print(attrs1['optimal_crt_values'], attrs2['optimal_crt_values'])
            break
        if len([True for i,j in zip(attrs1['optimal_crt_values'],attrs2['optimal_crt_values']) if i<=j]) == len(attrs1['optimal_crt_values']):
            oops = True
            print(attrs1['optimal_crt_values'], attrs2['optimal_crt_values'])
            break
            
if oops:
    print('oops')
else:
    print('good')
#    
#print(pareto_paths)
#
#
print(len(pareto_paths))
