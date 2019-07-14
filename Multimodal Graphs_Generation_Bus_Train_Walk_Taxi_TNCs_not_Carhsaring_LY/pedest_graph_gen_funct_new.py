import csv
import math
import time
import networkx as nx
from networkx.classes.function import number_of_edges, number_of_nodes

# importing pandas package

# -------------For Walk graph generation the following variables and attributes have been hardcoded:---------------------

# 2. walking speed ->  in calc_and_assign_walk_edge_attrs() walking time is basd on a speed equal to 1.4 m/s

# Comment: some of the functions require as argument the file path in which they operate on and some don't; in the controller integration with SimMobility these will be quried from the database directly so for now I keep it as it is and we'll decide later on the proper implementation

# *****************This module generates an unrestricted directed walk graph; Since SimMob doesn't currently include a pedestrian network, the walk graph is assumed to be the same with the road network in SimMob*****************

# ----function that generates the walk nodes using a csv extracted from supply.nodes table-----
# data = pd.read_csv('Road_nodes_coord.csv', index_col ="id")


def gen_walk_graph_nodes(G):
    # create the node from the actual walk network
    with open('Road_nodes_coord.csv', 'r') as rnc:
        RoadNodeReader = csv.DictReader(rnc)
        for row in RoadNodeReader:
            G.add_node('w' + str(row['id']), id=row['id'], pos=[float(row['x']), float(row['y'])], node_type='walk_graph_node', node_graph_type='Walk', is_mode_dupl=False, walk_node_dupl=False, to_mode='Walk')
            with open('node_taz_mapping.csv', 'r') as ntm:
                NodeTazMapReader = csv.DictReader(ntm)
                for line in NodeTazMapReader:
                    if row['id'] == line['node_id']:
                        G.nodes['w' + str(row['id'])]['zone'] = line['taz']
                        break
    # # add new nodes if there are parallel links between the same combination of nodes
    # links_checked = []
    # i = 0
    # with open('Road_Links.csv', 'r') as rl:
    #     RoadLinkReader = csv.DictReader(rl)
    #     for row in RoadLinkReader:
    #         if (row['from_node'], row['to_node']) not in links_checked:
    #             links_checked.append((row['from_node'], row['to_node']))
    #         else:
    #             i += 1
    #             G.add_node('w' + str(row['from_node']) + ',' + str(i), id=row['from_node'], pos=G.nodes['w' + str(row['from_node'])]['pos'], node_type='walk_graph_node', node_graph_type='Walk', walk_node_dupl=True, is_mode_dupl=False, zone=G.nodes['w' + str(row['from_node'])]['zone'])
    #             G.add_node('w' + str(row['to_node']) + ',' + str(i), id=row['to_node'], pos=G.nodes['w' + str(row['to_node'])]['pos'], node_type='walk_graph_node', node_graph_type='Walk', walk_node_dupl=True, is_mode_dupl=False, zone=G.nodes['w' + str(row['to_node'])]['zone'])

    # create the bus stops that will be represented in the walk network as duplicated nodes
    with open('Bus_stops_coord.csv', 'r') as bsc:
        BusStopReader = csv.DictReader(bsc)
        for i in BusStopReader:
            if i['status'] == 'OP':
                G.add_node('w_bus_stop' + str(i['code']), id=i['code'], pos=[float(i['x']), float(i['y'])], node_type='walk_graph_node', node_graph_type='Walk', is_mode_dupl=True, access_segs_id=[i['section_id']], zone=i['zone'], to_mode='Bus')
                G.nodes['w_bus_stop' + str(i['code'])]['access_links_id'] = []
                G.nodes['w_bus_stop' + str(i['code'])]['access_nodes_id'] = []
                for access_segment in G.nodes['w_bus_stop' + str(i['code'])]['access_segs_id']:
                    with open('road_segments.csv', 'r') as rs:
                        RoadSegmentReader = csv.DictReader(rs)
                        for j in RoadSegmentReader:
                            if access_segment == j['id']:
                                G.nodes['w_bus_stop' + str(i['code'])]['access_links_id'].append(j['link_id'])
                                break
                for link in G.nodes['w_bus_stop' + str(i['code'])]['access_links_id']:
                    with open('Road_links.csv', 'r') as rl:
                        RoadLinksReader = csv.DictReader(rl)
                        for k in RoadLinksReader:
                            if link == k['id']:
                                G.nodes['w_bus_stop' + str(i['code'])]['access_nodes_id'].append(k['from_node'])
                                G.nodes['w_bus_stop' + str(i['code'])]['access_nodes_id'].append(k['to_node'])
                                break

    # create the train stations that will be represented in the walk network as duplicated nodes
    with open('Train_stop_coord.csv', 'r') as tsc:
        TrainStopReader = csv.DictReader(tsc)
        for i in TrainStopReader:
            G.add_node('w_train_stop' + str(i['platform_name']), id=i['id'], pos=[float(i['x']), float(i['y'])], node_type='walk_graph_node', node_graph_type='Walk', is_mode_dupl=True, zone=i['zone'], to_mode='Train')
            G.nodes['w_train_stop' + str(i['platform_name'])]['access_segs_id'] = []
            G.nodes['w_train_stop' + str(i['platform_name'])]['access_links_id'] = []
            G.nodes['w_train_stop' + str(i['platform_name'])]['access_nodes_id'] = []
            with open('Train_access_segment.csv', 'r') as tas:
                TrainAccessSegReader = csv.DictReader(tas)
                for j in TrainAccessSegReader:
                    if i['id'] == j['mrt_stop_id']:
                        G.nodes['w_train_stop' + str(i['platform_name'])]['access_segs_id'].append(j['segment_id'])
            for access_segment in G.nodes['w_train_stop' + str(i['platform_name'])]['access_segs_id']:
                with open('road_segments.csv', 'r') as rs:
                    RoadSegmentReader = csv.DictReader(rs)
                    for k in RoadSegmentReader:
                        if access_segment == k['id']:
                            G.nodes['w_train_stop' + str(i['platform_name'])]['access_links_id'].append(k['link_id'])
                            break
            for link in G.nodes['w_train_stop' + str(i['platform_name'])]['access_links_id']:
                with open('Road_links.csv', 'r') as rl:
                    RoadLinksReader = csv.DictReader(rl)
                    for l in RoadLinksReader:
                        if link == l['id']:
                            if l['from_node'] not in G.nodes['w_train_stop' + str(i['platform_name'])]['access_nodes_id']:
                                G.nodes['w_train_stop' + str(i['platform_name'])]['access_nodes_id'].append(l['from_node'])
                            if l['to_node'] not in G.nodes['w_train_stop' + str(i['platform_name'])]['access_nodes_id']:
                                G.nodes['w_train_stop' + str(i['platform_name'])]['access_nodes_id'].append(l['to_node'])
                            break
# need to add the carsharing stations


# ----function that generates the walk edges from walk node to walk node using the links data from SimMob road network; due to potential parallel links from the same downstream intersection to the upstream intersection of the link, we also add virtual duplicates of those nodes and connect them; then we assign their corresponding attributes-----


# def gen_walk_graph_edges(G, data_file_path):
#     links_checked = []
#     i = 0
#     with open(data_file_path, 'r') as rl:
#         RoadLinksReader = csv.DictReader(rl)
#         for row in RoadLinksReader:
#             if (row['from_node'], row['to_node']) not in links_checked:
#                 G.add_edge('w' + str(row['from_node']), 'w' + str(row['to_node']), id=row['id'], edge_type='walk_edge', from_node='from_node', to_node='to_node', duplicate=None)
#             else:
#                 i += 1
#                 G.add_node('w' + str(row['from_node']) + ',' + str(i), id=row['from_node'], pos=G.nodes['w' + str(row['from_node'])]['pos'], node_type='walk_graph_node', node_graph_type='Walk', duplicate=True, zone=G.nodes['w' + str(row['from_node'])]['zone'])
#                 G.add_node('w' + str(row['to_node']) + ',' + str(i), id=row['to_node'], pos=G.nodes['w' + str(row['to_node'])]['pos'], node_type='walk_graph_node', node_graph_type='Walk', duplicate=True, zone=G.nodes['w' + str(row['to_node'])]['zone'])

#                 G.add_edge('w' + str(row['from_node']) + ',' + str(i), 'w' + str(row['to_node']) + ',' + str(i), id=row['id'], edge_type='walk_edge', from_node='from_node', to_node='to_node', duplicate=True)
#                 # print(G.nodes['w' + str(row['from_node']) + ',' + str(i)]['id'], G.nodes['w' + str(row['to_node']) + ',' + str(i)]['id'])
#             links_checked.append((row['from_node'], row['to_node']))
#     # we connect the duplicated nodes betwwen them as well as their incoming and outgoing connections
#     dupl_edge_dict = {}
#     for dupl_e in G.edges:
#         if G[dupl_e[0]][dupl_e[1]]['duplicate']:     # found a duplicated edge
#             for edge in G.edges:           # iterate over all the edges again
#                 if edge != dupl_e:
#                     if G.nodes[dupl_e[0]]['id'] == G.nodes[edge[1]]['id']:
#                         dupl_edge_dict.update({(edge[0], dupl_e[0]): {'id': G[edge[0]][edge[1]]['id'], 'edge_type': 'walk_edge', 'from_node': G[edge[0]][edge[1]]['from_node'], 'to_node': G[edge[0]][edge[1]]['to_node'], 'duplicate': True, 'virtual': True}})
#                     elif G.nodes[dupl_e[0]]['id'] == G.nodes[edge[0]]['id']:
#                         dupl_edge_dict.update({(dupl_e[0], edge[1]): {'id': G[edge[0]][edge[1]]['id'], 'edge_type': 'walk_edge', 'from_node': G[edge[0]][edge[1]]['from_node'], 'to_node': G[edge[0]][edge[1]]['to_node'], 'duplicate': True, 'virtual': True}})
#                     elif G.nodes[dupl_e[1]]['id'] == G.nodes[edge[0]]['id']:
#                         dupl_edge_dict.update({(dupl_e[1], edge[1]): {'id': G[edge[0]][edge[1]]['id'], 'edge_type': 'walk_edge', 'from_node': G[edge[0]][edge[1]]['from_node'], 'to_node': G[edge[0]][edge[1]]['to_node'], 'duplicate': True, 'virtual': True}})
#                     elif G.nodes[dupl_e[1]]['id'] == G.nodes[edge[1]]['id']:
#                         dupl_edge_dict.update({(edge[0], dupl_e[1]): {'id': G[edge[0]][edge[1]]['id'], 'edge_type': 'walk_edge', 'from_node': G[edge[0]][edge[1]]['from_node'], 'to_node': G[edge[0]][edge[1]]['to_node'], 'duplicate': True, 'virtual': True}})
#     for e, data in dupl_edge_dict.items():
#         G.add_edge(e[0], e[1], id=data['id'], edge_type=data['edge_type'], from_node=data['from_node'], to_node=data['to_node'], duplicate=data['duplicate'], virtual=data['virtual'])

# #--------function that assings walk edge attributes---------------


# def calc_and_assign_walk_edge_attrs(G, data_file_path):
#     for e in G.edges:
#         ped_edge_dist = 0
#         with open(data_file_path, 'r') as rlp:
#             RoadLinksPolyReader = csv.DictReader(rlp)
#             for row in RoadLinksPolyReader:
#                 if row['id'] == G[e[0]][e[1]]['id']:
#                     with open(data_file_path, 'r') as rlp:
#                         RoadLinksPolyReader = csv.DictReader(rlp)
#                         for line in RoadLinksPolyReader:
#                             if line['id'] == G[e[0]][e[1]]['id'] and int(line['seq_id']) == int(row['seq_id']) + 1:
#                                 ped_edge_dist += math.sqrt(sum([(a - b) ** 2 for a, b in zip((float(row['x']), float(row['y'])), (float(line['x']), float(line['y'])))]))
#                                 break
#         G[e[0]][e[1]]['travel_time'] = ped_edge_dist / 1.4
#         G[e[0]][e[1]]['wait_time'] = 0
#         G[e[0]][e[1]]['distance'] = ped_edge_dist
#         G[e[0]][e[1]]['cost'] = 0
