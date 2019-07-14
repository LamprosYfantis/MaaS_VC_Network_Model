import csv
import math
import time
import networkx as nx
import pandas as pd
import numpy as np
from networkx.classes.function import number_of_edges, number_of_nodes
from pedest_graph_gen_funct_new import gen_walk_graph_nodes


ped_graph = nx.DiGraph()

gen_walk_graph_nodes(ped_graph)

print(ped_graph.nodes.data())

# script below maps the pt infra in links of the walk network and captures links with no pt infra, links with just bus stops, links with just train stations and links with both (!!!!!!!!!!Need to be updated for the carsharing stations!!!!!!!!!!!!!!!!!!!)
# walk_links_with_other_mode_infra = {'links_with_no_infra': [], 'links_with_bus_stop': {}, 'links_with_train_station': {}, 'links_with_both_stop_and_station': {}}
# with open('Road_Links.csv', 'r') as rl:
#     RoadLinkReader = csv.DictReader(rl)
#     for row in RoadLinkReader:
#         check_list = []
#         for node in ped_graph:
#             if not(ped_graph.nodes[node]['is_mode_dupl']):
#                 continue
#             if row['id'] in ped_graph.nodes[node]['access_links_id']:
#                 check_list.append(row['id'])
#                 if ped_graph.nodes[node]['to_mode'] == 'Bus':
#                     walk_links_with_other_mode_infra['links_with_bus_stop'].update({row['id']: node})
#                 if ped_graph.nodes[node]['to_mode'] == 'Train':
#                     walk_links_with_other_mode_infra['links_with_train_station'].update({row['id']: node})
#         if row['id'] in walk_links_with_other_mode_infra['links_with_bus_stop'] and row['id'] in walk_links_with_other_mode_infra['links_with_train_station']:
#             conc_list = [walk_links_with_other_mode_infra['links_with_bus_stop'][row['id']], walk_links_with_other_mode_infra['links_with_train_station'][row['id']]]
#             walk_links_with_other_mode_infra['links_with_both_stop_and_station'].update({row['id']: conc_list})
#             walk_links_with_other_mode_infra['links_with_bus_stop'].pop(row['id'])
#             walk_links_with_other_mode_infra['links_with_train_station'].pop(row['id'])
#         if check_list == []:
#             walk_links_with_other_mode_infra['links_with_no_infra'].append(row['id'])
# # print(walk_links_with_other_mode_infra)
# # print(len(walk_links_with_other_mode_infra['links_with_no_infra']) + len(walk_links_with_other_mode_infra['links_with_bus_stop']) + len(walk_links_with_other_mode_infra['links_with_train_station']) + len(walk_links_with_other_mode_infra['links_with_both_stop_and_station']))


# links_checked = []
# count = 0
# # link_with_no_infra_dist = {}
# with open('Road_Links.csv', 'r') as rl:
#     RoadLinkReader = csv.DictReader(rl)
#     for row in RoadLinkReader:
#         if row['id'] in walk_links_with_other_mode_infra['links_with_no_infra']:
#             if (row['from_node'], row['to_node']) not in links_checked:
#                 link_polys_seq = {}
#                 with open('Road_links_polyline.csv', 'r') as rlp:
#                     RoadLinkPolyReader = csv.DictReader(rlp)
#                     for i in RoadLinkPolyReader:
#                         if i['id'] == row['id']:
#                             link_polys_seq.update({i['seq_id']: [float(i['x']), float(i['y'])]})
#                 link_part_list = []
#                 for seq_id in link_polys_seq:
#                     link_part_list.append(seq_id)
#                 dist_walk_to_walk = 0
#                 for k in range(len(link_part_list) - 1):
#                     link_part = [link_polys_seq[link_part_list[k]], link_polys_seq[link_part_list[k + 1]]]
#                     dist_walk_to_walk += math.sqrt(sum([(a - b) ** 2 for a, b in zip(link_part[0], link_part[1])]))
#                 ped_graph.add_edge('w' + str(row['from_node']), 'w' + str(row['to_node']), id=row['id'], edge_type='walk_edge', from_node=row['from_node'], to_node=row['to_node'], distance=dist_walk_to_walk, travel_time=dist_walk_to_walk / 1.4)
#             else:
#                 count += 1
#                 ped_graph.add_node('w' + str(row['from_node']) + ',' + str(count), id=row['from_node'], pos=G.nodes['w' + str(row['from_node'])]['pos'], node_type='walk_graph_node', node_graph_type='Walk', is_mode_dupl=False, walk_node_dupl=True, zone=G.nodes['w' + str(row['from_node'])]['zone'])
#                 ped_graph.add_node('w' + str(row['to_node']) + ',' + str(count), id=row['to_node'], pos=G.nodes['w' + str(row['to_node'])]['pos'], node_type='walk_graph_node', node_graph_type='Walk', is_mode_dupl=False, walk_node_dupl=True, zone=G.nodes['w' + str(row['to_node'])]['zone'])

#                 ped_graph.add_edge('w' + str(row['from_node']) + ',' + str(count), 'w' + str(row['to_node']) + ',' + str(count), id=row['id'], edge_type='walk_edge', from_node=row['from_node'], to_node=row['to_node'], duplicate=True, distance=G['w' + str(row['from_node'])]['w' + str(row['to_node'])]['distance'], travel_time=G['w' + str(row['from_node'])]['w' + str(row['to_node'])]['travel_time'])
#                 # print(G.nodes['w' + str(row['from_node']) + ',' + str(i)]['id'], G.nodes['w' + str(row['to_node']) + ',' + str(i)]['id'])
#             links_checked.append((row['from_node'], row['to_node']))
#         elif row['id'] in walk_links_with_other_mode_infra['links_with_bus_stop']:
#             bus_stop = walk_links_with_other_mode_infra['links_with_bus_stop'][row['id']]
#             bus_stop_coord = ped_graph.nodes[bus_stop]['pos']
#             link_polys_seq = {}
#             with open('Road_links_polyline.csv', 'r') as rlp:
#                 RoadLinkPolyReader = csv.DictReader(rlp)
#                 for j in RoadLinkPolyReader:
#                     if j['id'] == row['id']:
#                         link_polys_seq.update({j['seq_id']: [float(j['x']), float(j['y'])]})
#             link_part_list = []
#             for seq_id in link_polys_seq:
#                 link_part_list.append(seq_id)
#             dist_walk_to_walk = 0
#             dist_walk_to_bus_upstr = 0
#             for m in range(len(link_part_list) - 1):
#                 link_part = [link_polys_seq[link_part_list[m]], link_polys_seq[link_part_list[m + 1]]]
#                 ab = np.array(link_part)
#                 ag = np.array([link_polys_seq[link_part_list[m]], bus_stop_coord])
#                 proj_up = link_polys_seq[link_part_list[m]] + np.dot(ag, ab) / np.dot(ab, ab) * ab
#                 eucl_dist_1 = math.sqrt(sum([(a - b) ** 2 for a, b in zip(proj_up[0], proj_up[1])]))  # distance from upstream point to bus stop projection point
#                 ag = np.array([link_polys_seq[link_part_list[m + 1]], bus_stop_coord])
#                 proj_dstr = link_polys_seq[link_part_list[m + 1]] + np.dot(ag, ab) / np.dot(ab, ab) * ab
#                 eucl_dist_2 = math.sqrt(sum([(a - b) ** 2 for a, b in zip(proj_dstr[0], proj_dstr[1])]))  # distance from downstream point to bus stop projection point
#                 eucl_dist_3 = math.sqrt(sum([(a - b) ** 2 for a, b in zip(ab[0], ab[1])]))  # distance from upstream to downstream polyline point
#                 if (eucl_dist_1 < eucl_dist_3 and eucl_dist_2 < eucl_dist_3) or (eucl_dist_1 == eucl_dist_3 or eucl_dist_2 == eucl_dist_3):
#                     dist_walk_to_bus_upstr = dist_walk_to_walk + eucl_dist_1
#                     ped_graph.add_edge('w' + str(row['from_node']), bus_stop, id=row['id'], edge_type='walk_edge', from_node=row['from_node'], to_node=bus_stop, distance=dist_walk_to_bus_upstr, travel_time=dist_walk_to_bus_upstr / 1.4)
#                     ped_graph.add_edge(bus_stop, 'w' + str(row['from_node']), id=row['id'], edge_type='walk_edge', from_node=bus_stop, to_node=row['from_node'], distance=dist_walk_to_bus_upstr, travel_time=dist_walk_to_bus_upstr / 1.4)
#                 dist_walk_to_walk += eucl_dist_3
#                 ped_graph.add_edge(bus_stop, 'w' + str(row['to_node']), id=row['id'], edge_type='walk_edge', from_node=bus_stop, to_node=row['to_node'], distance=dist_walk_to_walk - dist_walk_to_bus_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_bus_upstr) / 1.4)
#                 ped_graph.add_edge('w' + str(row['to_node']), bus_stop, id=row['id'], edge_type='walk_edge', from_node=row['to_node'], to_node=bus_stop, distance=dist_walk_to_walk - dist_walk_to_bus_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_bus_upstr) / 1.4)
#         elif row['id'] in walk_links_with_other_mode_infra['links_with_train_station']:
#             train_station = walk_links_with_other_mode_infra['links_with_train_station'][row['id']]
#             train_station_coord = ped_graph.nodes[train_station]['pos']
#             link_polys_seq = {}
#             with open('Road_links_polyline.csv', 'r') as rlp:
#                 RoadLinkPolyReader = csv.DictReader(rlp)
#                 for z in RoadLinkPolyReader:
#                     if z['id'] == row['id']:
#                         link_polys_seq.update({z['seq_id']: [float(z['x']), float(z['y'])]})
#             link_part_list = []
#             for seq_id in link_polys_seq:
#                 link_part_list.append(seq_id)
#             dist_walk_to_walk = 0
#             dist_walk_to_train_upstr = 0
#             for w in range(len(link_part_list) - 1):
#                 link_part = [link_polys_seq[link_part_list[w]], link_polys_seq[link_part_list[w + 1]]]
#                 ab = np.array(link_part)
#                 ag = np.array([link_polys_seq[link_part_list[w]], train_station_coord])
#                 proj_up = link_polys_seq[link_part_list[w]] + np.dot(ag, ab) / np.dot(ab, ab) * ab
#                 eucl_dist_1 = math.sqrt(sum([(a - b) ** 2 for a, b in zip(proj_up[0], proj_up[1])]))  # distance from upstream point to bus stop projection point
#                 ag = np.array([link_polys_seq[link_part_list[w + 1]], train_station_coord])
#                 proj_dstr = link_polys_seq[link_part_list[w + 1]] + np.dot(ag, ab) / np.dot(ab, ab) * ab
#                 eucl_dist_2 = math.sqrt(sum([(a - b) ** 2 for a, b in zip(proj_dstr[0], proj_dstr[1])]))  # distance from downstream point to bus stop projection point
#                 eucl_dist_3 = math.sqrt(sum([(a - b) ** 2 for a, b in zip(ab[0], ab[1])]))  # distance from upstream to downstream polyline point
#                 if (eucl_dist_1 < eucl_dist_3 and eucl_dist_2 < eucl_dist_3) or (eucl_dist_1 == eucl_dist_3 or eucl_dist_2 == eucl_dist_3):
#                     dist_walk_to_train_upstr = dist_walk_to_walk + eucl_dist_1
#                     ped_graph.add_edge('w' + str(row['from_node']), train_station, id=row['id'], edge_type='walk_edge', from_node=row['from_node'], to_node=train_station, distance=dist_walk_to_train_upstr, travel_time=dist_walk_to_train_upstr / 1.4)
#                     ped_graph.add_edge(train_station, 'w' + str(row['from_node']), id=row['id'], edge_type='walk_edge', from_node=train_station, to_node=row['from_node'], distance=dist_walk_to_train_upstr, travel_time=dist_walk_to_train_upstr / 1.4)
#                 dist_walk_to_walk += eucl_dist_3
#                 ped_graph.add_edge(train_station, 'w' + str(row['to_node']), id=row['id'], edge_type='walk_edge', from_node=train_station, to_node=row['to_node'], distance=dist_walk_to_walk - dist_walk_to_train_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_train_upstr) / 1.4)
#                 ped_graph.add_edge('w' + str(row['to_node']), train_station, id=row['id'], edge_type='walk_edge', from_node=row['to_node'], to_node=train_station, distance=dist_walk_to_walk - dist_walk_to_train_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_train_upstr) / 1.4)
#         elif row['id'] in walk_links_with_other_mode_infra['links_with_both_stop_and_station']:
#             for node in walk_links_with_other_mode_infra['links_with_both_stop_and_station']:
#                 if ped_graph.nodes[node]['to_mode'] == 'Bus':
#                     bus_stop = node
#                     bus_stop_coord = ped_graph.nodes[node]['pos']
#                 elif ped_graph.nodes[node]['to_mode'] == 'Train':
#                     train_station = node
#                     train_station_coord = ped_graph.nodes[train_station]['pos']
#             link_polys_seq = {}
#             with open('Road_links_polyline.csv', 'r') as rlp:
#                 RoadLinkPolyReader = csv.DictReader(rlp)
#                 for q in RoadLinkPolyReader:
#                     if q['id'] == row['id']:
#                         link_polys_seq.update({q['seq_id']: [float(q['x']), float(q['y'])]})
#             link_part_list = []
#             for seq_id in link_polys_seq:
#                 link_part_list.append(seq_id)
#             dist_walk_to_walk = 0
#             dist_walk_to_bus_upstr = 0
#             dist_walk_to_train_upstr = 0
#             for w in range(len(link_part_list) - 1):
#                 link_part = [link_polys_seq[link_part_list[w]], link_polys_seq[link_part_list[w + 1]]]
#                 ab = np.array(link_part)
#                 ag = np.array([link_polys_seq[link_part_list[w]], train_station_coord])
#                 proj_up = link_polys_seq[link_part_list[w]] + np.dot(ag, ab) / np.dot(ab, ab) * ab
#                 eucl_dist_1 = math.sqrt(sum([(a - b) ** 2 for a, b in zip(proj_up[0], proj_up[1])]))  # distance from upstream point to bus stop projection point
#                 ag = np.array([link_polys_seq[link_part_list[w + 1]], train_station_coord])
#                 proj_dstr = link_polys_seq[link_part_list[w + 1]] + np.dot(ag, ab) / np.dot(ab, ab) * ab
#                 eucl_dist_2 = math.sqrt(sum([(a - b) ** 2 for a, b in zip(proj_dstr[0], proj_dstr[1])]))  # distance from downstream point to bus stop projection point
#                 eucl_dist_3 = math.sqrt(sum([(a - b) ** 2 for a, b in zip(ab[0], ab[1])]))  # distance from upstream to downstream polyline point
#                 if (eucl_dist_1 < eucl_dist_3 and eucl_dist_2 < eucl_dist_3) or (eucl_dist_1 == eucl_dist_3 or eucl_dist_2 == eucl_dist_3):
#                     dist_walk_to_train_upstr = dist_walk_to_walk + eucl_dist_1
#                     ped_graph.add_edge('w' + str(row['from_node']), train_station, id=row['id'], edge_type='walk_edge', from_node=row['from_node'], to_node=train_station, distance=dist_walk_to_train_upstr, travel_time=dist_walk_to_train_upstr / 1.4)
#                     ped_graph.add_edge(train_station, 'w' + str(row['from_node']), id=row['id'], edge_type='walk_edge', from_node=train_station, to_node=row['from_node'], distance=dist_walk_to_train_upstr, travel_time=dist_walk_to_train_upstr / 1.4)
#                 dist_walk_to_walk += eucl_dist_3
#                 ped_graph.add_edge(train_station, 'w' + str(row['to_node']), id=row['id'], edge_type='walk_edge', from_node=train_station, to_node=row['to_node'], distance=dist_walk_to_walk - dist_walk_to_train_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_train_upstr) / 1.4)
#                 ped_graph.add_edge('w' + str(row['to_node']), train_station, id=row['id'], edge_type='walk_edge', from_node=row['to_node'], to_node=train_station, distance=dist_walk_to_walk - dist_walk_to_train_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_train_upstr) / 1.4)

# csv_file_path = 'Road_Links.csv'
# gen_walk_graph_edges(ped_graph, csv_file_path)

# csv_file_path = 'Road_links_polyline.csv'
# calc_and_assign_walk_edge_attrs(ped_graph, csv_file_path)

# # for n in ped_graph:
# #     print(n)
# # print(ped_graph.nodes['w60']['zone'], ped_graph.nodes['w6']['zone'])

# print(ped_graph)

# for e, data in ped_graph.edges.items():
#     print(e, data)

# for e, data in ped_graph.edges.items():
#     print(e, data)

# print(ped_graph.is_directed())
# print(ped_graph.edges(data=True))
# origin = 'w60'
# destination = 'w55'
# request_time_sec = 64800                # 28920 is 9am
# # # # h = str(request_time_sec / 3600) if request_time_sec / 3600 >= 10 else '0' + str(request_time_sec / 3600)
# # # # m = str(request_time_sec % 3600 / 60) if request_time_sec % 3600 / 60 >= 10 else '0' + str(request_time_sec % 3600 / 60)
# # # # s = str(request_time_sec % 3600 % 60) if request_time_sec % 3600 % 60 >= 10 else '0' + str(request_time_sec % 3600 % 60)
# # # # request_time = h + ':' + m + ':' + s
# start = time.time()
# sp = nx.dijkstra_path(ped_graph, origin, destination, request_time_sec, in_vehicle_tt='in_vehicle_tt', walk_tt='walk_tt', distance='distance', distance_based_cost='distance_based_cost', zone_to_zone_cost='zone_to_zone_cost', timetable='departure_time', edge_type='edge_type', fare_scheme='zone_to_zone')
# end = time.time()
# print('Algorithm path Running time: %f sec' % (end - start))

# # start = time.time()
# # eat_sec = math.ceil(nx.dijkstra_path_length(ped_graph, origin, destination, request_time_sec, weight='weight', timetable='departure_time', edge_type='edge_type'))
# # end = time.time()
# # print('Algorithm dist Running time: %f sec' % (end - start))
# # # # h = str(eat_sec / 3600) if eat_sec / 3600 >= 10 else '0' + str(eat_sec / 3600)
# # # # m = str(eat_sec % 3600 / 60) if eat_sec % 3600 / 60 >= 10 else '0' + str(eat_sec % 3600 / 60)
# # # # s = str(eat_sec % 3600 % 60) if eat_sec % 3600 % 60 >= 10 else '0' + str(eat_sec % 3600 % 60)
# # # # arrival_time = h + ':' + m + ':' + s

# print('The shortest path is {}'.format(sp))
# # print('If a traveller leaves from {} to {} at {}, the earliest arrival time is {}'.format(origin, destination, request_time_sec, eat_sec))
