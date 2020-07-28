import csv
import math
import matplotlib.pyplot as plt
from bisect import bisect_left
import networkx as nx

# specification of the time discrtization step (time interval)
dt = 30

def gen_bus_stop_nodes(G):
    with open('Bus_stops_coord.csv', 'r') as bsc:
        BusStopsReader = csv.DictReader(bsc)
        for row in BusStopsReader:
            if row['status'] != 'OP':  # virtual bus stops are not represented in the graph for journey planning
                continue
            G.add_node('b' + str(row['code']), id=row['code'], pos=[float(row['x']), float(row['y'])], station=row['name'], node_type='stop_node', \
                       zone=row['zone'], section_id=row['section_id'], section_offset=float(row['section_offset']), stop_length=float(row['length']), \
                       node_graph_type='Bus')  # bus stop nodes are names as b+bus_stop_code (e.g. b1)

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


def gen_bus_dep_arr_timetable(G):
    dep_time_dict = {}
    arr_time_dict = {}
    for n in G:
        if G.nodes[n]['node_type'] == 'route_node':
            dep_time_dict.update({n: {'departure_time': {}, 'sequence_number': G.nodes[n]['sequence_number'], 'line_id': G.nodes[n]['line_id']}})
            arr_time_dict.update({n: {'arrival_time': {}, 'sequence_number': G.nodes[n]['sequence_number'], 'line_id': G.nodes[n]['line_id']}})

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
    
def assign_bus_edge_dep_timetable(G, departure_timetable):
    for e in G.edges:
        G[e[0]][e[1]]['departure_time'] = departure_timetable[e[0]]['departure_time']
    
def find_ge(a, x):  # binary search algorithm #'Find leftmost item greater than or equal to x'
  i = bisect_left(a, x)
  if i != len(a):
    return i, a[i]
  raise ValueError
  

def gen_bus_route_edge_waiting_times(G):
    discr_waiting_times = dict()
    
    for u, v, weight in G.edges.data():
        if weight['edge_type'] == 'pt_route_edge':
            discr_waiting_times.update({(u,v): {'wait_time': dict()}})
            for t in range(0, 86400, dt):
                discr_waiting_times[(u,v)]['wait_time'].update({t: {'discr_value': None, 'veh_id' : None}})
                
    for edge, attrs in discr_waiting_times.items():
        sorted_dep_time_dict = {v_id: d_t for v_id, d_t in sorted(G[edge[0]][edge[1]]['departure_time'].items(), key=lambda item: item[1])}
        list_of_ptedge_dep_times = list(sorted_dep_time_dict.values())
        list_of_ptedge_veh_ids = list(sorted_dep_time_dict.keys())
        for time, info in attrs['wait_time'].items():
            if time > list_of_ptedge_dep_times[-1]:
                earlier_dep_time = list_of_ptedge_dep_times[0]
                index = 0
                wait_time = earlier_dep_time + (86400-time)
                discr_wait_time = wait_time - (wait_time%dt)
            elif time < list_of_ptedge_dep_times[0]:
                earlier_dep_time = list_of_ptedge_dep_times[0]
                index = 0
                wait_time = earlier_dep_time - time
                discr_wait_time = wait_time - (wait_time%dt)
            else:
                index, earlier_dep_time = find_ge(list_of_ptedge_dep_times, time)
                wait_time = earlier_dep_time - time
                discr_wait_time = wait_time - (wait_time%dt)
            vehicle_id = list_of_ptedge_veh_ids[index]
            info['discr_value'] = discr_wait_time
            info['veh_id'] = vehicle_id

            
    return discr_waiting_times


# def assign_bus_edge_waiting_times(G, waiting_times = {}):
#     for e in G.edges:
#         if G[e[0]][e[1]]['edge_type'] == 'pt_route_edge':
#             G[e[0]][e[1]]['wait_time'] = waiting_times[(e[0], e[1])]
        
def gen_bus_route_edge_tt(G, departure_timetable, arrival_timetable):
    
    bus_route_sequence = dict()
    with open('Bus_stop_sequence.csv', 'r') as bss1:
        BusStopSeq1 = csv.DictReader(bss1)
        for row in BusStopSeq1:
            if row['route_id'] not in bus_route_sequence:
                bus_route_sequence.update({row['route_id']: list()})
                with open('Bus_stop_sequence.csv', 'r') as bss2:
                    BusStopSeq2 = csv.DictReader(bss2)
                    for line in BusStopSeq2:
                        if row['route_id'] == line['route_id']:
                            bus_route_sequence[row['route_id']].append(1+int(line['sequence_no']))
                    bus_route_sequence[row['route_id']].sort()
                
    discr_travel_times = dict()
    for edge in G.edges():
        if G[edge[0]][edge[1]]['edge_type'] == 'pt_route_edge':
            discr_travel_times.update({edge: {'travel_time': dict()}})
            v_node_sequence = int(G.nodes[edge[1]]['sequence_number'])
            for t in range(0, 86400, dt):
                vehicle_run_id = G[edge[0]][edge[1]]['wait_time'][t]['veh_id']
                if v_node_sequence == bus_route_sequence[G.nodes[edge[1]]['line_id']][-1]:
                    in_vehicle_time = arrival_timetable[edge[1]]['arrival_time'][vehicle_run_id] - \
                        departure_timetable[edge[0]]['departure_time'][vehicle_run_id]
                    discr_in_vehicle_time = in_vehicle_time - (in_vehicle_time%dt)
                    discr_travel_times[edge]['travel_time'].update({t: discr_in_vehicle_time})
                else:
                    if vehicle_run_id not in departure_timetable[edge[1]]['departure_time']:
                        in_vehicle_time = 999999999
                        discr_in_vehicle_time = in_vehicle_time - (in_vehicle_time%dt)
                        discr_travel_times[edge]['travel_time'].update({t: discr_in_vehicle_time})
                        continue
                    
                    in_vehicle_time = departure_timetable[edge[1]]['departure_time'][vehicle_run_id] - \
                        departure_timetable[edge[0]]['departure_time'][vehicle_run_id]
                    discr_in_vehicle_time = in_vehicle_time - (in_vehicle_time%dt)
                    discr_travel_times[edge]['travel_time'].update({t: discr_in_vehicle_time})
    
    return discr_travel_times

def gen_bus_route_node_transfer_edges(G):
    for u in G:
        for v in G:
            if u != v:
                if G.nodes[u]['node_type'] == 'stop_node' and G.nodes[v]['node_type'] == 'route_node' and u == 'b' + str(G.nodes[v]['node_id']):
                    G.add_edge(u, v, travel_time=5-(5%dt), distance=math.ceil((5-(5%dt)) * 1.2), edge_type='pt_transfer_edge', up_node_graph_type=G.nodes[u]['node_graph_type'], \
                                   dstr_node_graph_type=G.nodes[v]['node_graph_type'], up_node_type=G.nodes[u]['node_type'], \
                                   dstr_node_type=G.nodes[v]['node_type'], up_node_zone=G.nodes[u]['zone'], dstr_node_zone=G.nodes[v]['zone'])
                    G.add_edge(v, u, travel_time=0, distance=0, edge_type='pt_transfer_edge', up_node_graph_type=G.nodes[v]['node_graph_type'], \
                                   dstr_node_graph_type=G.nodes[u]['node_graph_type'], up_node_type=G.nodes[v]['node_type'], \
                                   dstr_node_type=G.nodes[u]['node_type'], up_node_zone=G.nodes[v]['zone'], dstr_node_zone=G.nodes[u]['zone'])


def gen_assign_bus_route_edge_distances(G):
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
            seg_edge_dist = 0
            for section_id in edge_section_sequence_list:
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


def gen_assign_bus_edge_cost(G):
    
    costs = {(0, 23399): 0.0019, (23400, 34200): 0.0029, (34201, 57599): 0.0019, (57600, 68400): 0.0029, \
             (68401, 86399): 0.0019}
    costs_dict = dict()
    
    for e in G.edges:
        if G[e[0]][e[1]]['edge_type'] == 'pt_route_edge':
            costs_dict.update({e: {'pt_cost': dict()}})
            for t in range(0, 86400, dt):
                for time_interval in costs:
                    if t >= time_interval[0] and t <= time_interval[1]:
                        cost = math.ceil(costs[time_interval] * G[e[0]][e[1]]['distance'])
                        costs_dict[e]['pt_cost'].update({t: cost})
                        break      
        else:
            costs_dict.update({e: {'pt_cost': 0}})
    
    return costs_dict
#---------------------------------------------------------------------------------------------------------------------------


# -------function calculates and assign the time-dependent zone-to-zone cost for zone-to-zone fare schemes; in transfer edges the cost is zero-------
# def gen_assign_bus_edge_zone_to_zone_cost(G):               # the cost tables is hardcoded here
#     zone_to_zone_cost = {(0, 23399): {('1', '1'): 16, ('1', '2'): 16, ('1', '3'): 20.5, ('2', '1'): 16, ('2', '2'): 16, ('2', '3'): 16, ('3', '1'): 20.5, ('3', '2'): 16, ('3', '3'): 16}, (23400, 34200): {('1', '1'): 20, ('1', '2'): 20, ('1', '3'): 24.5, ('2', '1'): 20, ('2', '2'): 20, ('2', '3'): 20, ('3', '1'): 24.5, ('3', '2'): 20, ('3', '3'): 20}, (34201, 57599): {('1', '1'): 16, ('1', '2'): 16, ('1', '3'): 20.5, ('2', '1'): 16, ('2', '2'): 16, ('2', '3'): 16, ('3', '1'): 20.5, ('3', '2'): 16, ('3', '3'): 16}, (57600, 68400): {('1', '1'): 20, ('1', '2'): 20, ('1', '3'): 24.5, ('2', '1'): 20, ('2', '2'): 20, ('2', '3'): 20, ('3', '1'): 24.5, ('3', '2'): 20, ('3', '3'): 20}, (68401, 86399): {('1', '1'): 16, ('1', '2'): 16, ('1', '3'): 20.5, ('2', '1'): 16, ('2', '2'): 16, ('2', '3'): 16, ('3', '1'): 20.5, ('3', '2'): 16, ('3', '3'): 16}}
#     # morning_off_peak = (0, 23399)
#     # morning_peak = (23400, 34200)
#     # afternoon_off_peak = (34201, 57599)
#     # evening_peak = (57600, 68400)
#     # evening_off_peak = (68401, 86399)
#     for e in G.edges:
#         if G[e[0]][e[1]]['edge_type'] == 'pt_route_edge':
#             G[e[0]][e[1]]['pt_zone_to_zone_cost'] = zone_to_zone_cost
#         else:
#             G[e[0]][e[1]]['pt_zone_to_zone_cost'] = 0
#---------------------------------------------------------------------------------------------------------------


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