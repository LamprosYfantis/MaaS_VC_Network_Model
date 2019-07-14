import csv
import math
import time
import networkx as nx
from networkx.classes.function import number_of_edges, number_of_nodes
from pedest_graph_gen_funct import gen_walk_graph_nodes, gen_walk_graph_edges, calc_and_assign_walk_edge_attrs


ped_graph = nx.DiGraph()

csv_file_path = 'Road_nodes_coord.csv'
gen_walk_graph_nodes(ped_graph, csv_file_path)

csv_file_path = 'Road_Links.csv'
gen_walk_graph_edges(ped_graph, csv_file_path)


csv_file_path = 'Road_links_polyline.csv'
calc_and_assign_walk_edge_attrs(ped_graph, csv_file_path)

# for n in ped_graph:
#     print(n)
# print(ped_graph.nodes['w60']['zone'], ped_graph.nodes['w6']['zone'])


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
