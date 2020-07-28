import csv
import math
import networkx as nx
import matplotlib.pyplot as plt

# -------------Bus network generation: the following variables and attributes have been hardcoded:---------------------
# 1. PT zones -> 3 ad-hoc PT Zones with arbitrary boundaries have been designed (same zone for train) and the bus stations have been mapped in these zones;
#    a 'zone' column in the csv file extracted from the supply.bus_stop table

# 2. walking time and distance for transfer edges -> in gen_bus_route_node_transfer_edges() walking time is indicatively 1sec and distance is extracted
#    based on the aforementioned travel time and an average walking speed equal to 1.4 m/s

# 3. time periods and cost/meter -> in gen_assign_bus_edge_distance_based_cost() the time periods are 5
#    i.e. morning off-peak, morning peak, afternoon off-peak, afternoon-peak and evening off-peak.
#    time periods are in seconds; also the cost/meter differs for those time periods, it is arbitraruy for now and hardcoded

# 4. time periods and zone-to-zones cost -> in gen_assign_bus_edge_zone_to_zone_cost again time periods are the same with additive fare scheme
#    and costs are hardcoded

# Comment: some of the functions require as argument the file path in which they operate on and some don't; in the controller integration
#          with SimMobility these will be queried from the in memory data structures or the database directly

# *****************This module generates a directed bus graph based on the realistic time-dependent graph with constant tranfer times (same with train)
#                   as proposed by Pyrga et al., 2009 and Hrncir et al. 2013 (same graph with variable transfert times could also be used).*****************

# ----function that generates the bus stop nodes using a csv extracted from supply.bus_stop table-----
def gen_bus_stop_nodes(G):
    with open('Bus_stops_coord.csv', 'r') as bsc:
        BusStopsReader = csv.DictReader(bsc)
        for row in BusStopsReader:
            if row['status'] != 'OP':       # virtual bus stops are not represented in the graph for journey planning
                continue
            G.add_node('b' + str(row['code']), id=row['code'], pos=[float(row['x']), float(row['y'])], station=row['name'], node_type='stop_node', \
                       zone=row['zone'], section_id=row['section_id'], section_offset=float(row['section_offset']), stop_length=float(row['length']), \
                       node_graph_type='Bus')  # bus stop nodes are names as b+bus_stop_code (e.g. b1)

# -----function that generates the bus route nodes using 2 csv files extracted from supply.bus_stop and output.journey_time; 
    # While in train data, route nodes can be named based on their platforms (SimMobility VC includes a train line and platform_ids for each sequence of stations),
    # in bus data, bus stops and their corresponding route nodes might have the same names/ids (no platforms). 
    # Therefore, to generate distincted node_ids for stop and route nodes of the same bus stop, the bus route nodes are named as 'stop_code'+'route_id'+'seq_no'.
    # The corresponding bus stop id of each route node is added as an attribute of the node
    # Also, the bus stop sequence numbers in supply schema are different than in journey_time file (in supply starts from 0, while in journey_time from 1);
    # the journeytime file's sequence numbering is used here for mapping departure times with stops later on
def gen_bus_route_nodes(G):
    stop_list = []
    with open('Bus_stops_coord.csv', 'r') as bss:
        BusStopSequenceReader = csv.DictReader(bss)
        for row in BusStopSequenceReader:
            stop_list.append(row['code'])

    with open('journeytime.csv', 'r') as jt:
        PT_Data = csv.reader(jt)
        for row in PT_Data:
            if row[0] in stop_list:
                G.add_node(row[0] + ',' + row[1] + ',' + row[4], node_id=row[0], line_id=row[1], station=G.nodes['b' + str(row[0])]['station'], \
                           pos=G.nodes['b' + str(row[0])]['pos'], sequence_number=row[4], node_type='route_node', zone=G.nodes['b' + str(row[0])]['zone'], \
                           section_id=G.nodes['b' + str(row[0])]['section_id'], section_offset=G.nodes['b' + str(row[0])]['section_offset'], \
                           stop_length=G.nodes['b' + str(row[0])]['stop_length'], node_graph_type='Bus')


#--------function that generates the bus route edges between bus route nodes--------------------------
def gen_bus_route_edges(G):
    for n in G:
        if G.nodes[n]['node_type'] == 'route_node':
            for node in G:
                if G.nodes[node]['node_type'] == 'route_node':
                    if G.nodes[n]['line_id'] == G.nodes[node]['line_id'] and int(G.nodes[node]['sequence_number']) == int(G.nodes[n]['sequence_number']) + 1:
                        G.add_edge(n, node, line_id=G.nodes[node]['line_id'], edge_type='pt_route_edge', up_node_graph_type=G.nodes[n]['node_graph_type'], \
                                   dstr_node_graph_type=G.nodes[node]['node_graph_type'], up_node_type=G.nodes[n]['node_type'], \
                                   dstr_node_type=G.nodes[node]['node_type'], up_node_zone=G.nodes[n]['zone'], dstr_node_zone=G.nodes[node]['zone'])
                        break
#----------------------------------------------------------------------------------------------------


#-------function that extracts and returns departure and arrival timetable data from a csv file extracted from output.journey_time
def gen_bus_dep_arr_timetable(G):
    # initialize two dictionaries (one for departure times and one for arrival times) for each route node
    dep_time_dict = {}
    arr_time_dict = {}
    for n in G:
        if G.nodes[n]['node_type'] == 'route_node':
            dep_time_dict.update({n: {'departure_time': {}, 'sequence_number': G.nodes[n]['sequence_number'], 'line_id': G.nodes[n]['line_id']}})
            arr_time_dict.update({n: {'arrival_time': {}, 'sequence_number': G.nodes[n]['sequence_number'], 'line_id': G.nodes[n]['line_id']}})

    # populate the dictionaries with corresponding data from output.journey_time; the dicts store the departure and arrival times for each bus_run_id of each route node
    for node in dep_time_dict:
        with open('journeytime.csv', 'r') as jt:
            PT_Data = csv.reader(jt)
            for row in PT_Data:
                if node == row[0] + ',' + row[1] + ',' + row[4]:
                    r_node_arr_time = int(row[5].split(':')[0]) * 3600 + int(row[5].split(':')[1]) * 60 + int(row[5].split(':')[2])
                    r_node_dwell_time = int(row[6].split(':')[0]) * 3600 + int(row[6].split(':')[1]) * 60 + int(row[6].split(':')[2])
                    dep_time_dict[node]['departure_time'].update({row[2]: r_node_arr_time + r_node_dwell_time})
                    arr_time_dict[node]['arrival_time'].update({row[2]: r_node_arr_time})

    # extract timetable in h:m:s format
    # for key in dep_time_dict:
    #     for run_id in dep_time_dict[key]['departure_time']:
    #         h = str(int(dep_time_dict[key]['departure_time'][run_id] / 3600)) if int(dep_time_dict[key]['departure_time'][run_id]) / 3600 >= 10 else '0' + str(int(dep_time_dict[key]['departure_time'][run_id] / 3600))
    #         m = str(int(dep_time_dict[key]['departure_time'][run_id] % 3600 / 60)) if int(dep_time_dict[key]['departure_time'][run_id]) % 3600 / 60 >= 10 else '0' + str(int(dep_time_dict[key]['departure_time'][run_id] % 3600 / 60))
    #         s = str(int(dep_time_dict[key]['departure_time'][run_id] % 3600 % 60)) if int(dep_time_dict[key]['departure_time'][run_id]) % 3600 % 60 >= 10 else '0' + str(int(dep_time_dict[key]['departure_time'][run_id] % 3600 % 60))
    #         time = h + ':' + m + ':' + s
    #         dep_time_dict[key]['departure_time'][run_id] = time
    # print(dep_time_dict['47,6_2,5'])

    return dep_time_dict, arr_time_dict
#-------------------------------------------------------------------------------------------------


# ------ function that takes as input the departure and arrival timetable dicts, extracts the travel time information for each route edge and returns the travel time dict
def gen_bus_route_edge_tt(G, departure_timetable, arrival_timetable):
    # initialise a dictionary that will store the travel time data for each route edge
    edge_tt_dict = {}
    for e in G.edges():
        edge_tt_dict.update({e: {'travel_time': {}, 'line_id': G[e[0]][e[1]]['line_id']}})    
    
    for u in departure_timetable:
        for v in arrival_timetable:
            if v != u:
                if int(arrival_timetable[v]['sequence_number']) == int(departure_timetable[u]['sequence_number']) + 1 and \
                arrival_timetable[u]['line_id'] == departure_timetable[v]['line_id']:
                    for run_id_u in departure_timetable[u]['departure_time']:
                        for run_id_v in departure_timetable[v]['departure_time']:
                            if run_id_u == run_id_v:
                                tt = arrival_timetable[v]['arrival_time'][run_id_v] - departure_timetable[u]['departure_time'][run_id_u]
                                edge_tt_dict[(u, v)]['travel_time'].update({run_id_u: tt})
                                break
                    break
    return edge_tt_dict
#-----------------------------------------------------------------------------------------------------


# ------function generates the tranfer edges between route nodes and stop nodes; also it assigns the in-vehile travel time, the walking time and the distance
def gen_bus_route_node_transfer_edges(G):
    for u in G:
        for v in G:
            if u != v:
                if G.nodes[u]['node_type'] == 'stop_node' and G.nodes[v]['node_type'] == 'route_node' and u == 'b' + str(G.nodes[v]['node_id']):
                    G.add_edge(u, v, travel_time=1, distance=math.ceil(1 * 1.4), edge_type='pt_transfer_edge', up_node_graph_type=G.nodes[u]['node_graph_type'], \
                                   dstr_node_graph_type=G.nodes[v]['node_graph_type'], up_node_type=G.nodes[u]['node_type'], \
                                   dstr_node_type=G.nodes[v]['node_type'], up_node_zone=G.nodes[u]['zone'], dstr_node_zone=G.nodes[v]['zone'])
                    G.add_edge(v, u, travel_time=0, distance=0, edge_type='pt_transfer_edge', up_node_graph_type=G.nodes[v]['node_graph_type'], \
                                   dstr_node_graph_type=G.nodes[u]['node_graph_type'], up_node_type=G.nodes[v]['node_type'], \
                                   dstr_node_type=G.nodes[u]['node_type'], up_node_zone=G.nodes[v]['zone'], dstr_node_zone=G.nodes[u]['zone'])
# ----------------------------------------------------------------------------------------------


# -----function that assigns the departure timetable data to each route edge in the graph------------
def assign_bus_edge_dep_timetable(G, departure_timetable):
    for e in G.edges:
        G[e[0]][e[1]]['departure_time'] = departure_timetable[e[0]]['departure_time']
# ----------------------------------------------------------------------------------------------


# ------function calculates and assigns the edge distances based on csv files extracted from 1. supply.pt_train_route, 2. supply.pt_train_block------------------
def gen_assign_bus_route_edge_distances(G):  # there are incosistencies with the data for bus, some section_Sequence_list is empty for some edges 
    # because their corresponding section id in bus_stops_coord.csv is not the right one in bus_routes.csv; check it again
    # first I create a list with the section ids in sequential order for each pt_route_edge
    for e in G.edges:
        if G[e[0]][e[1]]['edge_type'] == 'pt_route_edge':
            edge_section_sequence_list = []
            with open('Bus_routes.csv', 'r') as br:
                BusRouteReader = csv.DictReader(br)
                for row in BusRouteReader:
                    if G[e[0]][e[1]]['line_id'] == row['route_id'] and G.nodes[e[0]]['section_id'] == row['section_id']:
                        edge_section_sequence_list.append(row['section_id'])
                        section_seq_num = int(row['sequence_no'])
                        continue
                    if edge_section_sequence_list != []:
                        if row['route_id'] == G[e[0]][e[1]]['line_id'] and int(row['sequence_no']) == section_seq_num + 1:
                            edge_section_sequence_list.append(row['section_id'])
                            section_seq_num = int(row['sequence_no'])
                        if row['section_id'] == G.nodes[e[1]]['section_id']:
                            break
            # then for each section_id in the list I extract and aggregate the distances based on the bus stop locations in the starting and ending segment, and their in between
            seg_edge_dist = 0
            # print(e, edge_section_sequence_list)
            for section_id in edge_section_sequence_list:  # following script will only work correctly if segment ids are in order based on sequence
                if section_id == edge_section_sequence_list[-1]:
                    seg_edge_dist += G.nodes[e[1]]['section_offset'] + G.nodes[e[1]]['stop_length']
                    break
                with open('road_segments_poly.csv', 'r') as rsp:
                    SegmentPolylineReader1 = csv.DictReader(rsp)
                    for row in SegmentPolylineReader1:
                        if section_id == row['id']:
                            with open('road_segments_poly.csv', 'r') as rsp:
                                SegmentPolylineReader2 = csv.DictReader(rsp)
                                for line in SegmentPolylineReader2:
                                    if section_id == line['id'] and int(line['seq_id']) == int(row['seq_id']) + 1:
                                        seg_edge_dist += math.sqrt(sum([(a - b) ** 2 for a, b in zip((float(row['x']), float(row['y'])), (float(line['x']), float(line['y'])))]))
                                        break
                if section_id == edge_section_sequence_list[0]:
                    seg_edge_dist -= G.nodes[e[0]]['section_offset']
            G[e[0]][e[1]]['distance'] = math.ceil(seg_edge_dist)


# ------function calculates and assigns the distance-based cost for both route and transfer edges in case the fare scheme is additive; in transfer edges the cost is zero------
def gen_assign_bus_edge_distance_based_cost(G):  # harcoded costs for monetary-unit/meter
    for e in G.edges:
        if G[e[0]][e[1]]['edge_type'] == 'pt_route_edge':
            G[e[0]][e[1]]['pt_distance_based_cost'] = {(0, 23399): 0.00008 * G[e[0]][e[1]]['distance'], (23400, 34200): 0.0001 * G[e[0]][e[1]]['distance'], (34201, 57599): 0.00008 * G[e[0]][e[1]]['distance'], (57600, 68400): 0.0001 * G[e[0]][e[1]]['distance'], (68401, 86399): 0.00008 * G[e[0]][e[1]]['distance']}
        else:
            G[e[0]][e[1]]['pt_distance_based_cost'] = 0
#---------------------------------------------------------------------------------------------------------------------------


# -------function calculates and assign the time-dependent zone-to-zone cost for zone-to-zone fare schemes; in transfer edges the cost is zero-------
def gen_assign_bus_edge_zone_to_zone_cost(G):               # the cost tables is hardcoded here
    zone_to_zone_cost = {(0, 23399): {('1', '1'): 16, ('1', '2'): 16, ('1', '3'): 20.5, ('2', '1'): 16, ('2', '2'): 16, ('2', '3'): 16, ('3', '1'): 20.5, ('3', '2'): 16, ('3', '3'): 16}, (23400, 34200): {('1', '1'): 20, ('1', '2'): 20, ('1', '3'): 24.5, ('2', '1'): 20, ('2', '2'): 20, ('2', '3'): 20, ('3', '1'): 24.5, ('3', '2'): 20, ('3', '3'): 20}, (34201, 57599): {('1', '1'): 16, ('1', '2'): 16, ('1', '3'): 20.5, ('2', '1'): 16, ('2', '2'): 16, ('2', '3'): 16, ('3', '1'): 20.5, ('3', '2'): 16, ('3', '3'): 16}, (57600, 68400): {('1', '1'): 20, ('1', '2'): 20, ('1', '3'): 24.5, ('2', '1'): 20, ('2', '2'): 20, ('2', '3'): 20, ('3', '1'): 24.5, ('3', '2'): 20, ('3', '3'): 20}, (68401, 86399): {('1', '1'): 16, ('1', '2'): 16, ('1', '3'): 20.5, ('2', '1'): 16, ('2', '2'): 16, ('2', '3'): 16, ('3', '1'): 20.5, ('3', '2'): 16, ('3', '3'): 16}}
    # morning_off_peak = (0, 23399)
    # morning_peak = (23400, 34200)
    # afternoon_off_peak = (34201, 57599)
    # evening_peak = (57600, 68400)
    # evening_off_peak = (68401, 86399)
    for e in G.edges:
        if G[e[0]][e[1]]['edge_type'] == 'pt_route_edge':
            G[e[0]][e[1]]['pt_zone_to_zone_cost'] = zone_to_zone_cost
        else:
            G[e[0]][e[1]]['pt_zone_to_zone_cost'] = 0
#---------------------------------------------------------------------------------------------------------------

# -------function that identifies and assigns to bus stop nodes their corresponding access segments, access links and access nodes from the walk graph
        # (here road graph is used as the walk graph)
        # These will be later used for connecting the bus graph with the walking graph and the other graphs if needed-------
def assign_bus_stop_access_nodes(G):
    for stop in G:
        if G.nodes[stop]['node_type'] == 'stop_node':
            G.nodes[stop]['access_segs_id'] = []
            G.nodes[stop]['access_links_id'] = []
            G.nodes[stop]['access_nodes_id'] = []
            with open('Bus_stops_coord.csv', 'r') as bsc:
                BusStopAccessReader = csv.DictReader(bsc)
                for row in BusStopAccessReader:
                    if 'b' + str(row['code']) == stop:
                        G.nodes[stop]['access_segs_id'].append(row['section_id'])
            for access_segment in G.nodes[stop]['access_segs_id']:
                with open('road_segments.csv', 'r') as rs:
                    RoadSegmentReader = csv.DictReader(rs)
                    for row in RoadSegmentReader:
                        if access_segment == row['id']:
                            G.nodes[stop]['access_links_id'].append(row['link_id'])
                            break
            for link in G.nodes[stop]['access_links_id']:
                with open('Road_links.csv', 'r') as rl:
                    RoadLinksReader = csv.DictReader(rl)
                    for row in RoadLinksReader:
                        if link == row['id']:
                            if row['from_node'] not in G.nodes[stop]['access_nodes_id']:
                                G.nodes[stop]['access_nodes_id'].append(row['from_node'])
                            if row['to_node'] not in G.nodes[stop]['access_nodes_id']:
                                G.nodes[stop]['access_nodes_id'].append(row['to_node'])
                            break

## ---- function that plots the train graph----------
#def plot_bus_graph(G):
#    pos = nx.get_node_attributes(G, 'pos')
#    nx.draw_networkx(G, pos)  # Graph with node attributes
#    plt.show()
##-------------------------------------------------------------
