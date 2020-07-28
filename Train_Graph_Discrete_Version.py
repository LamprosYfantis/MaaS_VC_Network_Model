import math
import csv
from bisect import bisect_left
import networkx as nx

# specification of the time discrtization step (time interval)
dt = 30

def gen_train_station_nodes(G):
    with open('Train_stop_coord.csv', 'r') as ts:
        TrainStations = csv.DictReader(ts)
        for row in TrainStations:
            G.add_node(row['platform_name'], pos=(float(row['x']), float(row['y'])), station=row['platform_name'], station_id=row['id'], \
                       node_type='station_node', zone=row['zone'], node_graph_type='Train')  # node_type is also assigned

def gen_train_route_nodes(G):
    with open('Train_platform.csv', 'r') as tp:
        TrainStationPlatforms = csv.DictReader(tp)
        for row in TrainStationPlatforms:
            G.add_node(row['platform_no'], station=row['station_no'], line_id=row['line_id'], pos=G.nodes[row['station_no']]['pos'], \
                       node_type='route_node', block_id=row['block_id'], zone=G.nodes[row['station_no']]['zone'], node_graph_type='Train')  # node_type is also assigned
    with open('Train_route_platform.csv', 'r') as trp:
        TrainRoutePlatforms = csv.DictReader(trp)
        for row in TrainRoutePlatforms:
            G.nodes[row['platform_no']]['sequence_no'] = row['sequence_no']

def gen_train_route_edges(G):
    # creation of MRT route edges that connect the MRT platforms
    with open('Train_route_platform.csv', 'r') as trp:
        TrainRoutePlatforms1 = csv.DictReader(trp)
        for row in TrainRoutePlatforms1:
            with open('Train_route_platform.csv', 'r') as trp:
                TrainRoutePlatforms2 = csv.DictReader(trp)
                for line in TrainRoutePlatforms2:
                    if row['line_id'] == line['line_id'] and int(line['sequence_no']) == int(row['sequence_no']) + 1:
                        G.add_edge(row['platform_no'], line['platform_no'], line_id=row['line_id'], edge_type='pt_route_edge', \
                                   up_node_graph_type=G.nodes[row['platform_no']]['node_graph_type'], dstr_node_graph_type=G.nodes[line['platform_no']]['node_graph_type'], \
                                   up_node_type=G.nodes[row['platform_no']]['node_type'], dstr_node_type=G.nodes[line['platform_no']]['node_type'], \
                                   up_node_zone=G.nodes[row['platform_no']]['zone'], dstr_node_zone=G.nodes[line['platform_no']]['zone'])
                        break


def gen_depart_and_arrival_timetable_data(G):
    dep_time_dict = {}
    arr_time_dict = {}
    with open('Train_route_platform.csv', 'r') as trp:
        TrainRoutePlatforms = csv.DictReader(trp)
        for row in TrainRoutePlatforms:
            dep_time_dict.update({row['platform_no']: {'departure_time': {}, 'sequence_no': row['sequence_no'], 'line_id': row['line_id']}})
            arr_time_dict.update({row['platform_no']: {'arrival_time': {}, 'sequence_no': row['sequence_no'], 'line_id': row['line_id']}})

    for key in dep_time_dict:
        with open('journeytime.csv', 'r') as jt:
            pt_data = csv.reader(jt)
            for line in pt_data:
                if line[0] == key:
                    plt_arr_time = int(line[5].split(':')[0]) * 3600 + int(line[5].split(':')[1]) * 60 + int(line[5].split(':')[2])
                    plt_dwell_time = int(line[6].split(':')[0]) * 3600 + int(line[6].split(':')[1]) * 60 + int(line[6].split(':')[2])
                    dep_time_dict[line[0]]['departure_time'].update({line[2]: plt_arr_time + plt_dwell_time})
                    arr_time_dict[line[0]]['arrival_time'].update({line[2]: plt_arr_time})

    # extract timetable in h:m:s format
    # for key in dep_time_dict:
    #     for run_id, dep_time in dep_time_dict[key]['departure_time'].items():
    #         h = str(int(dep_time / 3600)) if int(dep_time) / 3600 >= 10 else '0' + str(int(dep_time / 3600))
    #         m = str(int(dep_time % 3600 / 60)) if int(dep_time) % 3600 / 60 >= 10 else '0' + str(int(dep_time % 3600 / 60))
    #         s = str(int(dep_time % 3600 % 60)) if int(dep_time) % 3600 % 60 >= 10 else '0' + str(int(dep_time % 3600 % 60))
    #         time = h + ':' + m + ':' + s
    #         dep_time_dict[key]['departure_time'][run_id] = time
    return dep_time_dict, arr_time_dict

def assign_route_edge_dep_timetable(G, departure_timetable):
    for e in G.edges:
        G[e[0]][e[1]]['departure_time'] = departure_timetable[e[0]]['departure_time']

def find_ge(a, x):  # binary search algorithm #'Find leftmost item greater than or equal to x'
  i = bisect_left(a, x)
  if i != len(a):
    return i, a[i]
  raise ValueError
                        
def gen_train_route_edge_waiting_times(G):
    
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


# def assign_train_edge_waiting_times(G, waiting_times = {}):
#     for e in G.edges:
#         if G[e[0]][e[1]]['edge_type'] == 'pt_route_edge':
#             G[e[0]][e[1]]['wait_time'] = waiting_times[(e[0], e[1])]

def gen_train_route_edge_travel_times(G, departure_timetable, arrival_timetable):
    line_platform_sequence = dict()
    with open('Train_route_platform.csv', 'r') as trp:
        TrainRoutePlatforms1 = csv.DictReader(trp)
        for row in TrainRoutePlatforms1:
            if row['line_id'] not in line_platform_sequence:
                line_platform_sequence.update({row['line_id']: list()})
                with open('Train_route_platform.csv', 'r') as trp:
                    TrainRoutePlatforms2 = csv.DictReader(trp)
                    for line in TrainRoutePlatforms2:
                        if row['line_id'] == line['line_id']:
                            line_platform_sequence[row['line_id']].append(int(line['sequence_no']))
                    line_platform_sequence[row['line_id']].sort()
                
    discr_travel_times = dict()
    for edge in G.edges():
        if G[edge[0]][edge[1]]['edge_type'] == 'pt_route_edge':
            discr_travel_times.update({edge: {'travel_time': dict()}})
            v_node_sequence = int(G.nodes[edge[1]]['sequence_no'])
            for t in range(0, 86400, dt):
                vehicle_run_id = G[edge[0]][edge[1]]['wait_time'][t]['veh_id']
                if v_node_sequence == line_platform_sequence[G.nodes[edge[1]]['line_id']][-1]:
                    if not arrival_timetable[edge[1]]['arrival_time']:
                        break
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
    
    for edge in discr_travel_times:
        if not discr_travel_times[edge]['travel_time']:
            with open('Train_edge_travel_time.csv', 'r') as tett:
                Mrt_edge_tt = csv.DictReader(tett)
                for row in Mrt_edge_tt:
                    if row['from_stn'] in G.nodes[edge[0]]['station'] and row['to_stn'] in G.nodes[edge[1]]['station']:
                        for t in range(0, 86400, dt):
                            discr_travel_times[edge]['travel_time'].update({t: int(row['travel_time'])})
            
    return discr_travel_times
# ------------------------------------------------------------------------------------------------------------

# ------the following script will not be needed after running the modified executable for simmobility_prod;
#       the fuction basically assigns to the last edge of each line the travel times from the static data that were missing-----------------
# def add_static_tt_to_missing_edge_tt(G, route_edges_travel_times):
#     # ---------------Script for adding missing travel times for last edges using static travel times---------------------------
#     # first I create a list with all MRT lines
#     list_of_MRT_lines = []
#     for edge in route_edges_travel_times:
#         if route_edges_travel_times[edge]['line_id'] not in list_of_MRT_lines:
#             list_of_MRT_lines.append(route_edges_travel_times[edge]['line_id'])

#     # then I create a dict with the vehicle run_ids for all MRT lines
#     train_runs_of_each_line = {}
#     for line_id in list_of_MRT_lines:
#         train_runs_of_each_line.update({line_id: []})
#         for edge in route_edges_travel_times:
#             if route_edges_travel_times[edge]['line_id'] == line_id and route_edges_travel_times[edge]['travel_time'] != {}:
#                 for run_id in route_edges_travel_times[edge]['travel_time']:
#                     train_runs_of_each_line[line_id].append(run_id)
#                 break

#     # then I use the dict of run_ids for all MRT lines to assign those run_ids to the missing edges (last edges of each line) and
#     # at the same time I assign the default travel time from the static data tgo each run_id of the missing edges
#     for line in train_runs_of_each_line:
#         for edge in route_edges_travel_times:
#             if route_edges_travel_times[edge]['travel_time'] == {} and route_edges_travel_times[edge]['line_id'] == line:
#                 for run_id in train_runs_of_each_line[line]:
#                     with open('Train_edge_travel_time.csv', 'r') as tett:
#                         Mrt_edge_tt = csv.DictReader(tett)
#                         for row in Mrt_edge_tt:
#                             if row['from_stn'] in G.nodes[edge[0]]['station'] and row['to_stn'] in G.nodes[edge[1]]['station']:
#                                 route_edges_travel_times[edge]['travel_time'][run_id] = int(row['travel_time'])
#                                 break
#                 break
#     return route_edges_travel_times
# -----------------------------------------------------------------------------------------------------------------------

def gen_train_platform_transfer_edges(G):
    
    for u in G:
        for v in G:
            if u != v:
                if G.nodes[u]['node_type'] == 'station_node' and G.nodes[v]['node_type'] == 'route_node' and u == G.nodes[v]['station']:
                    G.add_edge(u, v, travel_time=60-(60%dt), distance=math.ceil((60-(60%dt)) * 1.2), edge_type='pt_transfer_edge', up_node_graph_type=G.nodes[u]['node_graph_type'], \
                               dstr_node_graph_type=G.nodes[v]['node_graph_type'], up_node_type=G.nodes[u]['node_type'], dstr_node_type=G.nodes[v]['node_type'], \
                                   up_node_zone=G.nodes[u]['zone'], dstr_node_zone=G.nodes[v]['zone'])
                    G.add_edge(v, u, travel_time=0, distance=0, edge_type='pt_transfer_edge', up_node_graph_type=G.nodes[v]['node_graph_type'], \
                               dstr_node_graph_type=G.nodes[u]['node_graph_type'], up_node_type=G.nodes[v]['node_type'], dstr_node_type=G.nodes[u]['node_type'], \
                                   up_node_zone=G.nodes[v]['zone'], dstr_node_zone=G.nodes[u]['zone'])

def gen_assign_train_route_edge_distances(G):
    for e in G.edges:
        if G[e[0]][e[1]]['edge_type'] == 'pt_route_edge':
            platform_seq_of_blocks = []
            with open('Train_route.csv', 'r') as tr:
                TrainRouteReader = csv.DictReader(tr)
                for row in TrainRouteReader:
                    if G[e[0]][e[1]]['line_id'] == row['line_id'] and G.nodes[e[0]]['block_id'] == row['block_id']:
                        platform_seq_of_blocks.append(row['block_id'])
                        block_seq_num = int(row['sequence_no'])
                        continue
                    if platform_seq_of_blocks != []:
                        if row['line_id'] == G[e[0]][e[1]]['line_id'] and int(row['sequence_no']) == block_seq_num + 1:
                            platform_seq_of_blocks.append(row['block_id'])
                            block_seq_num = int(row['sequence_no'])
                        if row['block_id'] == G.nodes[e[1]]['block_id']:
                            break
            G[e[0]][e[1]]['distance'] = 0
            with open('Train_blocks.csv', 'r') as tb:
                TrainBlockReader = csv.DictReader(tb)
                for row in TrainBlockReader:
                    if row['block_id'] in platform_seq_of_blocks:
                        if row['block_id'] == platform_seq_of_blocks[0] or row['block_id'] == platform_seq_of_blocks[-1]:
                            G[e[0]][e[1]]['distance'] = G[e[0]][e[1]]['distance'] + int(math.ceil(float(row['length']) / 2))
                        else:
                            G[e[0]][e[1]]['distance'] = G[e[0]][e[1]]['distance'] + int(math.ceil(float(row['length'])))

def gen_assign_train_edge_cost(G):  # harcoded costs for monetary-unit/meter
    
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
# -------------------------------------------------------------------------------------------------------------------

# -------function calculates and assign the time-dependent zone-to-zone cost for zone-to-zone fare schemes; in transfer edges the cost is zero-------
# def gen_assign_train_edge_zone_to_zone_cost(G):               # the cost tables is hardcoded here
#     zone_to_zone_cost = {(0, 23399): {('1', '1'): 16, ('1', '2'): 16, ('1', '3'): 20.5, ('2', '1'): 16, ('2', '2'): 16, ('2', '3'): 16, ('3', '1'): 20.5, ('3', '2'): 16, ('3', '3'): 16}, (23400, 34200): {('1', '1'): 20, ('1', '2'): 20, ('1', '3'): 24.5, ('2', '1'): 20, ('2', '2'): 20, ('2', '3'): 20, ('3', '1'): 24.5, ('3', '2'): 20, ('3', '3'): 20}, (34201, 57599): {('1', '1'): 16, ('1', '2'): 16, ('1', '3'): 20.5, ('2', '1'): 16, ('2', '2'): 16, ('2', '3'): 16, ('3', '1'): 20.5, ('3', '2'): 16, ('3', '3'): 16}, (57600, 68400): {('1', '1'): 20, ('1', '2'): 20, ('1', '3'): 24.5, ('2', '1'): 20, ('2', '2'): 20, ('2', '3'): 20, ('3', '1'): 24.5, ('3', '2'): 20, ('3', '3'): 20}, (68401, 86399): {('1', '1'): 16, ('1', '2'): 16, ('1', '3'): 20.5, ('2', '1'): 16, ('2', '2'): 16, ('2', '3'): 16, ('3', '1'): 20.5, ('3', '2'): 16, ('3', '3'): 16}}
#     # morning_off_peak = (0, 23399)
#     # morning_peak = (23400, 34200)
#     # afternoon_off_peak = (34201, 57599)
#     # afternoon_peak = (57600, 68400)
#     # evening_off_peak = (68401, 86399)
#     for e in G.edges:
#         if G[e[0]][e[1]]['edge_type'] == 'pt_route_edge':
#             G[e[0]][e[1]]['pt_zone_to_zone_cost'] = zone_to_zone_cost
#         else:
#             G[e[0]][e[1]]['pt_zone_to_zone_cost'] = 0

def assign_train_station_access_nodes(G):
    for station in G:
        if G.nodes[station]['node_type'] == 'station_node':
            G.nodes[station]['access_segs_id'] = []
            G.nodes[station]['access_links_id'] = []
            G.nodes[station]['access_nodes_id'] = []
            with open('Train_access_segment.csv', 'r') as tas:
                TrainStationAccessReader = csv.DictReader(tas)
                for row in TrainStationAccessReader:
                    if row['mrt_stop_id'] == G.nodes[station]['station_id']:
                        G.nodes[station]['access_segs_id'].append(row['segment_id'])
            for access_segment in G.nodes[station]['access_segs_id']:
                with open('road_segments.csv', 'r') as rs:
                    RoadSegmentReader = csv.DictReader(rs)
                    for row in RoadSegmentReader:
                        if access_segment == row['id']:
                            G.nodes[station]['access_links_id'].append(row['link_id'])
                            break
            for link in G.nodes[station]['access_links_id']:
                with open('Road_links.csv', 'r') as rl:
                    RoadLinksReader = csv.DictReader(rl)
                    for row in RoadLinksReader:
                        if link == row['id']:
                            if row['from_node'] not in G.nodes[station]['access_nodes_id']:
                                G.nodes[station]['access_nodes_id'].append(row['from_node'])
                            if row['to_node'] not in G.nodes[station]['access_nodes_id']:
                                G.nodes[station]['access_nodes_id'].append(row['to_node'])
                            break

# # ---- function that plots the train graph----------
# def plot_train_graph(G):
#     pos = nx.get_node_attributes(G, 'pos')
#     nx.draw_networkx(G, pos)  # Graph with node attributes
#     plt.show()
# #-----------------------------------------------------