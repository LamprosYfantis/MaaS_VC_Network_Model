import csv
import math
import time
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from mrt_graph_functions_with_hist_tt import gen_train_station_nodes, gen_train_route_nodes, gen_train_route_edges, gen_depart_and_arrival_timetable_data, gen_train_route_edge_tt, add_static_tt_to_missing_edge_tt, set_route_edge_dep_timetable, gen_train_platform_transfer_edges_with_fixed_tt, plot_train_graph
from bus_graph_gen_funct_with_hist_tt import gen_bus_stop_nodes, gen_bus_route_nodes, gen_bus_route_edges, gen_bus_dep_arr_timetable, gen_bus_route_edge_tt, gen_bus_route_node_transfer_edges
# from pedest_graph_gen_funct import gen_walk_graph_nodes, gen_walk_graph_edges, calc_and_assign_walk_edge_tt
from networkx.classes.function import number_of_edges, number_of_nodes
from networkx.algorithms.operators.binary import union, disjoint_union
from functions import PathTT, import_data, dict_tt, add_edges, add_nodes, add_nodes_dual, graph, add_dummy_nodes, import_tt_turnings, add_dummy_edges, add_dual_edges, k_shortest_paths, dummy_dict, add_edge_attributes, update_dicts_tt  # update_dummy_tt, , update_tt
# from calc_eucl_dist_func import haversine

start = time.time()


#------------------------------------------- Train Graph Generation----------------------------------------------------------
train_graph = nx.DiGraph()

station_data_file = 'C:/Users/Lampros Yfantis/Desktop/VC_Network_Data_Fran/Rail_Network_Data/Train_stop_coord.csv'
gen_train_station_nodes(train_graph, station_data_file)

platform_data_file = 'C:/Users/Lampros Yfantis/Desktop/VC_Network_Data_Fran/Rail_Network_Data/Train_platform.csv'
gen_train_route_nodes(train_graph, platform_data_file)

platform_sequence_file = 'C:/Users/Lampros Yfantis/Desktop/VC_Network_Data_Fran/Rail_Network_Data/Train_route_platform.csv'
gen_train_route_edges(train_graph, platform_sequence_file)

histroric_train_data = 'C:/Users/Lampros Yfantis/Desktop/SimM_PT_Historical_Data/journeytime.csv'
departure_timetable_dict, arrival_timetable_dict = gen_depart_and_arrival_timetable_data(train_graph, platform_sequence_file, histroric_train_data)
# print(departure_timetable_dict)
# print(arrival_timetable_dict)

train_route_edges_tt_dict = gen_train_route_edge_tt(train_graph, departure_timetable_dict, arrival_timetable_dict)
# print(train_route_edges_tt_dict)

static_train_tt_data = 'C:/Users/Lampros Yfantis/Desktop/VC_Network_Data_Fran/Rail_Network_Data/Train_edge_travel_time.csv'
train_route_edges_tt_dict = add_static_tt_to_missing_edge_tt(train_graph, train_route_edges_tt_dict, static_train_tt_data)
# print(train_route_edges_tt_dict)

# assign the list of travel times for each edge in our graph
nx.set_edge_attributes(train_graph, train_route_edges_tt_dict)  # at this point the travel times of the last edge of each line are missing because journeytime.csv doen't include the arrival times of the last node in each line, this info have to be taken from the station to station travel times csv

# assign the list of departure times for each edge in our graph
set_route_edge_dep_timetable(train_graph, departure_timetable_dict)

gen_train_platform_transfer_edges_with_fixed_tt(train_graph)
# print(train_graph.edges(data=True))
# print('The total number of nodes in G is {}'.format(number_of_nodes(train_graph)))
# print('The total number of edges in G is {}'.format(number_of_edges(train_graph)))
end = time.time()
print('Train graph generation time is {}sec'.format(end - start))

#-----------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------Bus Graph Generation------------------------------------------------------------------
start = time.time()

bus_graph = nx.DiGraph()

csv_file_path = 'C:/Users/Lampros Yfantis/Desktop/VC_Network_Data_Fran/Bus_Network_Data/Bus_stops_coord.csv'
gen_bus_stop_nodes(bus_graph, csv_file_path)

csv_file_path1 = 'C:/Users/Lampros Yfantis/Desktop/VC_Network_Data_Fran/Bus_Network_Data/Bus_stops_coord.csv'
csv_file_path2 = 'C:/Users/Lampros Yfantis/Desktop/SimM_PT_Historical_Data/journeytime.csv'
gen_bus_route_nodes(bus_graph, csv_file_path1, csv_file_path2)

gen_bus_route_edges(bus_graph)

csv_file_path = 'C:/Users/Lampros Yfantis/Desktop/SimM_PT_Historical_Data/journeytime.csv'
bus_dep_times, bus_arr_times = gen_bus_dep_arr_timetable(bus_graph, csv_file_path)

for e in bus_graph.edges:
    for stop in bus_dep_times:
        if e[0] == stop:
            bus_graph[e[0]][e[1]]['departure_time'] = bus_dep_times[stop]['departure_time']
            break

bus_route_edge_tts = gen_bus_route_edge_tt(bus_graph, bus_dep_times, bus_arr_times)

nx.set_edge_attributes(bus_graph, bus_route_edge_tts)

gen_bus_route_node_transfer_edges(bus_graph)

end = time.time()
print('Bus graph generation time is {}sec'.format(end - start))
#----------------------------------------------------------------------------------------------------------------------------------

# bus_train_graph = union(train_graph, bus_graph, rename=(None, None), name=None)
bus_train_graph = union(train_graph, bus_graph)

pos = nx.get_node_attributes(bus_train_graph, 'pos')
nx.draw_networkx(bus_train_graph, pos, with_labels=True)  # Graph with node attributes
plt.show()
