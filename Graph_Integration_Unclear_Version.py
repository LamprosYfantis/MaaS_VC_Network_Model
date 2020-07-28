import cProfile, pstats, io
import csv
import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import random
import re
import statistics
import time

from Walk_Graph_Func_Unclear_Version import gen_walk_graph_nodes, gen_walk_graph_edges
from Train_Graph_Discrete_Version import gen_train_station_nodes, gen_train_route_nodes, gen_train_route_edges, \
    gen_depart_and_arrival_timetable_data, gen_train_route_edge_travel_times, assign_route_edge_dep_timetable, \
        gen_train_platform_transfer_edges, gen_assign_train_route_edge_distances, \
            gen_assign_train_edge_cost, assign_train_station_access_nodes, gen_train_route_edge_waiting_times, find_ge
from Bus_Graph_Discrete_Version import gen_bus_stop_nodes, gen_bus_route_nodes, gen_bus_route_edges, \
    gen_bus_dep_arr_timetable, assign_bus_edge_dep_timetable, find_ge, gen_bus_route_edge_waiting_times, \
        gen_bus_route_edge_tt, gen_bus_route_node_transfer_edges, gen_assign_bus_route_edge_distances, \
            gen_assign_bus_edge_cost, assign_bus_stop_access_nodes
from ehail_functions import gen_taxi_dist_dict, gen_taxi_cost_dict, gen_taxi_wt_dict, gen_taxi_tt_dict, \
    gen_on_demand_taxi_single_wt_dict, gen_on_demand_taxi_single_tt_dict, gen_on_demand_taxi_shared_wt_dict, \
        gen_on_demand_taxi_shared_tt_dict, add_taxi_nodes, add_taxi_edges, add_on_demand_taxi_single_nodes, \
            add_on_demand_taxi_single_edges, add_on_demand_taxi_shared_nodes, add_on_demand_taxi_shared_edges
from carsharing_functions import import_data, dicts_tt, import_tt, dist, gen_station_stock, gen_sta_dict, \
    gen_cs_cost_dicts, add_cs_dummy_nodes, add_cs_station_nodes, add_cs_dual_nodes, add_cs_dummy_edges, \
        add_cs_dual_edges, add_cs_station_access_edges
from networkx.classes.function import number_of_edges, number_of_nodes
from networkx.algorithms.operators.binary import union

# specification of the time discrtization step (time interval)
dt = 30

# def profile(fnc):
    
#     """A decorator that uses cProfile to profile a function"""
    
#     def inner(*args, **kwargs):
        
#         pr = cProfile.Profile()
#         pr.enable()
#         retval = fnc(*args, **kwargs)
#         pr.disable()
#         s = io.StringIO()
#         sortby = 'cumulative'
#         ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
#         ps.print_stats()
#         print(s.getvalue())
#         return retval

#     return inner

#-----------------------------------Walk Graph Generation-------------------------------------------
start = time.time()

ped_graph = nx.DiGraph()

gen_walk_graph_nodes(ped_graph)

gen_walk_graph_edges(ped_graph)

end = time.time()
print('Walk graph generation time: %f sec' % (end - start))
print(ped_graph.number_of_nodes())
print(ped_graph.number_of_edges())
# print(ped_graph.edges(data=True))
#----------------------------------------------------------------------------------------------------

#------------------------------------------- Train Graph Generation----------------------------------
start = time.time()

train_graph = nx.DiGraph()

gen_train_station_nodes(train_graph)
gen_train_route_nodes(train_graph)

gen_train_route_edges(train_graph)

departure_timetable_dict, arrival_timetable_dict = gen_depart_and_arrival_timetable_data(train_graph)
assign_route_edge_dep_timetable(train_graph, departure_timetable_dict)

wait_times = gen_train_route_edge_waiting_times(train_graph)
nx.set_edge_attributes(train_graph, wait_times) 

train_route_edge_travel_times = gen_train_route_edge_travel_times(train_graph, departure_timetable_dict, arrival_timetable_dict)
nx.set_edge_attributes(train_graph, train_route_edge_travel_times)

gen_train_platform_transfer_edges(train_graph)

gen_assign_train_route_edge_distances(train_graph)

costs = gen_assign_train_edge_cost(train_graph)
nx.set_edge_attributes(train_graph, costs)

assign_train_station_access_nodes(train_graph)
end = time.time()

print('Train graph generation time is {}sec'.format(end - start))
print(train_graph.number_of_nodes())
print(train_graph.number_of_edges())
# print(train_graph.edges(data=True))
#------------------------------------------------------------------------------------------------------------

#---------------------------------------------Bus Graph Generation--------------------------------------
start = time.time()

bus_graph = nx.DiGraph()

gen_bus_stop_nodes(bus_graph)

gen_bus_route_nodes(bus_graph)

gen_bus_route_edges(bus_graph)

bus_dep_times, bus_arr_times = gen_bus_dep_arr_timetable(bus_graph)
assign_bus_edge_dep_timetable(bus_graph, bus_dep_times)

wait_times = gen_bus_route_edge_waiting_times(bus_graph)
nx.set_edge_attributes(bus_graph, wait_times)

bus_route_edge_tts = gen_bus_route_edge_tt(bus_graph, bus_dep_times, bus_arr_times)
nx.set_edge_attributes(bus_graph, bus_route_edge_tts)

gen_bus_route_node_transfer_edges(bus_graph)

gen_assign_bus_route_edge_distances(bus_graph)

bus_costs = gen_assign_bus_edge_cost(bus_graph)
nx.set_edge_attributes(bus_graph, bus_costs)

assign_bus_stop_access_nodes(bus_graph)

end = time.time()

print('Bus graph generation time is {}sec'.format(end - start))
print(bus_graph.number_of_nodes())
print(bus_graph.number_of_edges())

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
# print(taxi_graph.nodes())
add_taxi_edges(taxi_graph, taxi_taz_tt_dict, taxi_taz_wt_dict, taxi_taz_dist_dict, taxi_taz_cost_dict)  # Add the 576 edges between incoming and outgoing nodes with the travel time, waiting time, distance and cost as attributes

# print(ehail_graph.edges(data=True))
end = time.time()
print('Taxi graph generation time is {}min'.format((end - start) / 60))
print(taxi_graph.number_of_nodes())
print(taxi_graph.number_of_edges())
##
###------------------------------------------- On-demand single taxi Graph Generation------------------------------------------------
##
start = time.time()

on_demand_taxi_single_graph = nx.DiGraph()


on_demand_taxi_single_taz_wt_dict = gen_on_demand_taxi_single_wt_dict()  # Dict of waiting times for the 288 5min interval of the 24 zones
on_demand_taxi_single_taz_tt_dict = gen_on_demand_taxi_single_tt_dict()  # Dict of travel times for the 288 5min interval of the 576 pairs between zones
on_demand_taxi_single_taz_dist_dict = gen_taxi_dist_dict('single_taxi')  # Dict of distances in km of the 576 pairs between zones
on_demand_taxi_single_taz_cost_dict = gen_taxi_cost_dict(on_demand_taxi_single_taz_tt_dict, on_demand_taxi_single_taz_dist_dict, 'single_taxi')  # Dict of cost of the 576 pairs between zones


add_on_demand_taxi_single_nodes(on_demand_taxi_single_graph, on_demand_taxi_single_taz_wt_dict)  # Add the 48 nodes (2 per zone, i: indicates incoming node, o: indicates outgoing) with the zone_id as an attribute)
add_on_demand_taxi_single_edges(on_demand_taxi_single_graph, on_demand_taxi_single_taz_tt_dict, on_demand_taxi_single_taz_wt_dict, on_demand_taxi_single_taz_dist_dict, on_demand_taxi_single_taz_cost_dict)  # Add the 576 edges between incoming and outgoing nodes with the travel time, waiting time, distance and cost as attributes
# print(on_demand_taxi_single_graph.edges())
# print(ehail_graph.edges(data=True))
end = time.time()
print('On-demand taxi single graph generation time is {}min'.format((end - start) / 60))
print(on_demand_taxi_single_graph.number_of_nodes())
print(on_demand_taxi_single_graph.number_of_edges())

#
##------------------------------------------- On-demand shared taxi Graph Generation------------------------------------------------
#
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
# print(on_demand_taxi_shared_graph['SMS_Poolshar2i']['SMS_Poolshar2o']['taxi_fares'])

# print(ehail_graph.edges(data=True))
end = time.time()
print('On-demand taxi shared graph generation time is {}min'.format((end - start) / 60))
print(on_demand_taxi_shared_graph.number_of_nodes())
print(on_demand_taxi_shared_graph.number_of_edges())
##
###------------------------------------ Station-based Carsharing Graph Generation--------------------------
# 1.IMPORTING THE DATA

start=time.time()
nodes,l,l_dum=import_data() ## nodes: dict that contains Virtual City nodes data
                             ## l: dict that contains VC links data
                             ## l_dum: same as l but with the id of the from_nodes and to_nodes change to indicate the dual graph dummy nodes

tt=import_tt() ## tt: DF that contains the 24 h travel time per link and turning every 5 mins (source: simulator)
                            ## NOTE: there is no information about some links at some time interval
                            ## meaning that no car transverse this link at those time intervals.
                            ## There are also some turnings that are not included in the 521 turning groups (CHECK THIS)
                            ## They are generated during the simulation by Simmobility in case there is
                            ## no path between OD, due to network misspecification , in order to allow a
                            ## car to come back to the origin ( CHECK THIS)


## 2. Car sharing graph
cs_graph=nx.DiGraph()

cs_dual_tt_dict,cs_dum_tt_dict=dicts_tt(tt) ## tt_dual: offline dict that contains the travel times of the 521 turnings for the 288
                                ##5 min intervals with the default travel time as base
                                ## tt_dum: offline dict that contains the travel times of the 254
                                ## dummy destination edges for the 288 5 min intervals with the default
                                ##travel time of the previous link as base

cs_dual_dist_dict, cs_dum_dist_dict=dist()
cs_sta_stock_level_dict= gen_station_stock()
cs_sta_dict=gen_sta_dict()

cs_dual_cost_dict, cs_dum_cost_dict = gen_cs_cost_dicts(cs_dual_tt_dict, cs_dum_tt_dict)

add_cs_dummy_nodes(cs_graph, nodes, cs_sta_dict)
add_cs_station_nodes(cs_graph,cs_sta_dict, cs_sta_stock_level_dict)

add_cs_dual_nodes(cs_graph,l_dum)

add_cs_dummy_edges(cs_graph,l_dum, cs_dum_tt_dict, cs_dum_dist_dict,cs_dum_cost_dict, cs_sta_dict)

add_cs_dual_edges(cs_graph,cs_dual_tt_dict, cs_dual_dist_dict,cs_dual_cost_dict)

add_cs_station_access_edges(cs_graph,cs_sta_dict, nodes,cs_dum_tt_dict, l)

end=time.time()
print('Running time: %f min' %((end-start)/60))
print(cs_graph.number_of_nodes())
print(cs_graph.number_of_edges())
############################----------------------------------------------------------#########################################



#----------------------------------Integrated Time-Dependent Multilayer Graph Generation-----------------------------


# ------------- generation of access edges between walk graph and train graph------------------------

start = time.time()
int_train_walk_graph = union(train_graph, ped_graph, rename=(None, None), name=None)

for train_station in train_graph:
    if train_graph.nodes[train_station]['node_type'] == 'station_node':
        for walk_node in ped_graph:
            if ped_graph.nodes[walk_node]['id'] in train_graph.nodes[train_station]['access_nodes_id']:
                edge_dist = math.sqrt(sum([(a - b) ** 2 for a, b in zip(ped_graph.nodes[walk_node]['pos'], train_graph.nodes[train_station]['pos'])]))
                edge_tt = edge_dist / 1.4
                discr_edge_tt = edge_tt - (edge_tt%dt)
                int_train_walk_graph.add_edge(train_station, walk_node, edge_type='access_edge', \
                                              up_node_graph_type=int_train_walk_graph.nodes[train_station]['node_graph_type'], \
                                              dstr_node_graph_type=int_train_walk_graph.nodes[walk_node]['node_graph_type'], \
                                              up_node_type=int_train_walk_graph.nodes[train_station]['node_type'], \
                                              dstr_node_type=int_train_walk_graph.nodes[walk_node]['node_type'], \
                                              up_node_zone=int_train_walk_graph.nodes[train_station]['zone'], \
                                              dstr_node_zone=int_train_walk_graph.nodes[walk_node]['zone'], \
                                              distance = edge_dist, travel_time = discr_edge_tt)
                int_train_walk_graph.add_edge(walk_node, train_station, edge_type='access_edge', \
                                              up_node_graph_type=int_train_walk_graph.nodes[walk_node]['node_graph_type'], \
                                              dstr_node_graph_type=int_train_walk_graph.nodes[train_station]['node_graph_type'], \
                                              up_node_type=int_train_walk_graph.nodes[walk_node]['node_type'], \
                                              dstr_node_type=int_train_walk_graph.nodes[train_station]['node_type'], \
                                              up_node_zone=int_train_walk_graph.nodes[walk_node]['zone'], \
                                              dstr_node_zone=int_train_walk_graph.nodes[train_station]['zone'], \
                                              distance = edge_dist, travel_time = discr_edge_tt)



# #----------------------generation of access edges between walk graph and bus graph----------------------------

#start = time.time()
int_train_bus_walk_graph = union(int_train_walk_graph, bus_graph, rename=(None, None), name=None)

for bus_stop in bus_graph:
    if bus_graph.nodes[bus_stop]['node_type'] == 'stop_node':
        for walk_node in ped_graph:
            if ped_graph.nodes[walk_node]['id'] in bus_graph.nodes[bus_stop]['access_nodes_id']:
                edge_dist = math.sqrt(sum([(a - b) ** 2 for a, b in zip(ped_graph.nodes[walk_node]['pos'], bus_graph.nodes[bus_stop]['pos'])]))
                edge_tt = edge_dist / 1.4
                discr_edge_tt = edge_tt - (edge_tt%dt)
                int_train_bus_walk_graph.add_edge(bus_stop, walk_node, edge_type='access_edge', \
                                              up_node_graph_type=int_train_bus_walk_graph.nodes[bus_stop]['node_graph_type'], \
                                              dstr_node_graph_type=int_train_bus_walk_graph.nodes[walk_node]['node_graph_type'], \
                                              up_node_type=int_train_bus_walk_graph.nodes[bus_stop]['node_type'], \
                                              dstr_node_type=int_train_bus_walk_graph.nodes[walk_node]['node_type'], \
                                              up_node_zone=int_train_bus_walk_graph.nodes[bus_stop]['zone'], \
                                              dstr_node_zone=int_train_bus_walk_graph.nodes[walk_node]['zone'], \
                                              distance = edge_dist, travel_time = discr_edge_tt)
                int_train_bus_walk_graph.add_edge(walk_node, bus_stop, edge_type='access_edge', \
                                              up_node_graph_type=int_train_bus_walk_graph.nodes[walk_node]['node_graph_type'], \
                                              dstr_node_graph_type=int_train_bus_walk_graph.nodes[bus_stop]['node_graph_type'], \
                                              up_node_type=int_train_bus_walk_graph.nodes[walk_node]['node_type'], \
                                              dstr_node_type=int_train_bus_walk_graph.nodes[bus_stop]['node_type'], \
                                              up_node_zone=int_train_bus_walk_graph.nodes[walk_node]['zone'], \
                                              dstr_node_zone=int_train_bus_walk_graph.nodes[bus_stop]['zone'], \
                                              distance = edge_dist, travel_time = discr_edge_tt)

##end=time.time()

#print('Running time for graph integration: %f sec' % ((end - start)))

# #------------------------generation of access edges between walk graph and taxi graph-------------------------------
int_trn_bus_walk_taxi_graph = union(int_train_bus_walk_graph, taxi_graph, rename=(None, None), name=None)

for walk_node in ped_graph:
    if not(ped_graph.nodes[walk_node]['is_mode_dupl']):  # connect only the walk nodes and not the rest infrastructure; this may change later on to be discussed
        for taxi_node in taxi_graph:
            if taxi_graph.nodes[taxi_node]['zone'] == 't' + ped_graph.nodes[walk_node]['zone']:
                if taxi_graph.nodes[taxi_node]['node_type'] == 'in_taxi_node':
                    int_trn_bus_walk_taxi_graph.add_edge(walk_node, taxi_node, edge_type='access_edge', \
                                              up_node_graph_type=int_trn_bus_walk_taxi_graph.nodes[walk_node]['node_graph_type'], \
                                              dstr_node_graph_type=int_trn_bus_walk_taxi_graph.nodes[taxi_node]['node_graph_type'], \
                                              up_node_type=int_trn_bus_walk_taxi_graph.nodes[walk_node]['node_type'], \
                                              dstr_node_type=int_trn_bus_walk_taxi_graph.nodes[taxi_node]['node_type'], \
                                              up_node_zone=int_trn_bus_walk_taxi_graph.nodes[walk_node]['zone'], \
                                              dstr_node_zone=int_trn_bus_walk_taxi_graph.nodes[taxi_node]['zone'], \
                                              distance = 0, travel_time = 0)
                elif taxi_graph.nodes[taxi_node]['node_type'] == 'out_taxi_node':
                    int_trn_bus_walk_taxi_graph.add_edge(taxi_node, walk_node, edge_type='access_edge', \
                                              up_node_graph_type=int_trn_bus_walk_taxi_graph.nodes[taxi_node]['node_graph_type'], \
                                              dstr_node_graph_type=int_trn_bus_walk_taxi_graph.nodes[walk_node]['node_graph_type'], \
                                              up_node_type=int_trn_bus_walk_taxi_graph.nodes[taxi_node]['node_type'], \
                                              dstr_node_type=int_trn_bus_walk_taxi_graph.nodes[walk_node]['node_type'], \
                                              up_node_zone=int_trn_bus_walk_taxi_graph.nodes[taxi_node]['zone'], \
                                              dstr_node_zone=int_trn_bus_walk_taxi_graph.nodes[walk_node]['zone'], \
                                              distance = 0, travel_time = 0)

##for e in int_trn_bus_walk_taxi_graph.edges:
##    if int_trn_bus_walk_taxi_graph[e[0]][e[1]]['edge_type'] == 'access_edge':
##        print(e)
### #--------------------generation of access edges between walk graph and on-demand single graph---------------------
##
int_trn_bus_walk_taxi_ondemsngtx_graph = union(int_trn_bus_walk_taxi_graph, on_demand_taxi_single_graph, rename=(None, None), name=None)

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
                                              dstr_node_zone=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[taxi_node]['zone'], \
                                              distance = 0, travel_time = 0)
                elif on_demand_taxi_single_graph.nodes[taxi_node]['node_type'] == 'out_on_demand_taxi_single_node':
                    int_trn_bus_walk_taxi_ondemsngtx_graph.add_edge(taxi_node, walk_node, edge_type='access_edge', \
                                              up_node_graph_type=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[taxi_node]['node_graph_type'], \
                                              dstr_node_graph_type=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[walk_node]['node_graph_type'], \
                                              up_node_type=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[taxi_node]['node_type'], \
                                              dstr_node_type=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[walk_node]['node_type'], \
                                              up_node_zone=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[taxi_node]['zone'], \
                                              dstr_node_zone=int_trn_bus_walk_taxi_ondemsngtx_graph.nodes[walk_node]['zone'], \
                                              distance = 0, travel_time = 0)
#
##for e in int_train_walk_graph.edges:
##    if int_train_walk_graph[e[0]][e[1]]['edge_type'] == 'access_edge':
##        print(e)
### #-----------------generation of access edges between walk graph and on-demand-shared graph-----------------------
##
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
                                              dstr_node_zone=pt_walk_TNCs_graph.nodes[taxi_node]['zone'], 
                                              distance = 0, travel_time = 0)
                elif on_demand_taxi_shared_graph.nodes[taxi_node]['node_type'] == 'out_on_demand_taxi_shared_node':
                    pt_walk_TNCs_graph.add_edge(taxi_node, walk_node, edge_type='access_edge', \
                                              up_node_graph_type=pt_walk_TNCs_graph.nodes[taxi_node]['node_graph_type'], \
                                              dstr_node_graph_type=pt_walk_TNCs_graph.nodes[walk_node]['node_graph_type'], \
                                              up_node_type=pt_walk_TNCs_graph.nodes[taxi_node]['node_type'], \
                                              dstr_node_type=pt_walk_TNCs_graph.nodes[walk_node]['node_type'], \
                                              up_node_zone=pt_walk_TNCs_graph.nodes[taxi_node]['zone'], \
                                              dstr_node_zone=pt_walk_TNCs_graph.nodes[walk_node]['zone'], \
                                              distance = 0, travel_time = 0)
##
##
##for e in int_train_walk_graph.edges:
##    if int_train_walk_graph[e[0]][e[1]]['edge_type'] == 'access_edge':
##        print(e)
### ------------ generation of access edges between walk graph and carsharing graph--------------------
pt_walk_TNCs_cs_graph = union(pt_walk_TNCs_graph, cs_graph, rename=(None, None), name=None)

for station in cs_graph:
    if cs_graph.nodes[station]['node_type'] == 'car_sharing_station_node':
        for walk_node in ped_graph:
            if ped_graph.nodes[walk_node]['id'] == cs_graph.nodes[station]['access_node']:
                edge_dist = math.sqrt(sum([(a - b) ** 2 for a, b in zip(ped_graph.nodes[walk_node]['pos'], cs_graph.nodes[station]['pos'])]))
                edge_tt = edge_dist / 1.4
                discr_edge_tt = edge_tt - (edge_tt%dt)
                pt_walk_TNCs_cs_graph.add_edge(station, walk_node, edge_type='access_edge', \
                                               up_node_graph_type=pt_walk_TNCs_cs_graph.nodes[station]['node_graph_type'], \
                                               dstr_node_graph_type=pt_walk_TNCs_cs_graph.nodes[walk_node]['node_graph_type'], \
                                               up_node_type=pt_walk_TNCs_cs_graph.nodes[station]['node_type'], \
                                               dstr_node_type=pt_walk_TNCs_cs_graph.nodes[walk_node]['node_type'], \
                                               distance = edge_dist, travel_time = discr_edge_tt)
                pt_walk_TNCs_cs_graph.add_edge(walk_node, station, edge_type='access_edge', \
                                               up_node_graph_type=pt_walk_TNCs_cs_graph.nodes[walk_node]['node_graph_type'], \
                                               dstr_node_graph_type=pt_walk_TNCs_cs_graph.nodes[station]['node_graph_type'], \
                                               up_node_type=pt_walk_TNCs_cs_graph.nodes[walk_node]['node_type'], \
                                               dstr_node_type=pt_walk_TNCs_cs_graph.nodes[station]['node_type'], \
                                               distance = edge_dist, travel_time = discr_edge_tt)
#                break
end = time.time()

print(pt_walk_TNCs_cs_graph.number_of_nodes())
print(pt_walk_TNCs_cs_graph.number_of_edges())
print('Running time for graph integration: %f sec' % ((end - start)))

# ----- dumping the graph to a pickle file
nx.write_gpickle(pt_walk_TNCs_cs_graph, "VC_multimodal_graph_discr20sec")

# ----- reading the graph from a pickle file
nx.write_gpickle(ped_graph, "VC_walk_graph_discr20sec")