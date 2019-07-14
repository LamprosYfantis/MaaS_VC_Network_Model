import csv
import math
import time
import networkx as nx
import pandas as pd
import numpy as np
from numpy.linalg import norm
from shapely.geometry import Point, LineString
from networkx.classes.function import number_of_edges, number_of_nodes
from pedest_graph_gen_funct_new import gen_walk_graph_nodes


def find_proj(point1=[], line_point1=[], line_point2=[]):
    point = Point(point1)
    line = LineString([line_point1, line_point2])

    x = np.array(point.coords[0])
    # print(x)

    u = np.array(line.coords[0])
    # print(u)
    v = np.array(line.coords[len(line.coords) - 1])
    # print(v)

    n = v - u
    # print(n)
    n /= np.linalg.norm(n, 2)

    P = u + n * np.dot(x - u, n)
    return(P)  # 0.2 1.


def gen_walk_graph_nodes_with_infra(G):
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


def gen_walk_graph_edges_with_attrs(G):
    # script below maps the pt infra in links of the walk network and captures links with no pt infra, links with just bus stops, links with just train stations and links with both (!!!!!!!!!!Need to be updated for the carsharing stations!!!!!!!!!!!!!!!!!!!)
    walk_links_with_other_mode_infra = {'links_with_no_infra': [], 'links_with_bus_stop': {}, 'links_with_train_station': {}, 'links_with_both_stop_and_station': {}}
    with open('Road_Links.csv', 'r') as rl:
        RoadLinkReader = csv.DictReader(rl)
        for row in RoadLinkReader:
            check_list = []
            for node in G:
                if not(G.nodes[node]['is_mode_dupl']):
                    continue
                if row['id'] in G.nodes[node]['access_links_id']:
                    check_list.append(row['id'])
                    if G.nodes[node]['to_mode'] == 'Bus':
                        walk_links_with_other_mode_infra['links_with_bus_stop'].update({row['id']: node})
                    if G.nodes[node]['to_mode'] == 'Train':
                        walk_links_with_other_mode_infra['links_with_train_station'].update({row['id']: node})
            if row['id'] in walk_links_with_other_mode_infra['links_with_bus_stop'] and row['id'] in walk_links_with_other_mode_infra['links_with_train_station']:
                conc_list = [walk_links_with_other_mode_infra['links_with_bus_stop'][row['id']], walk_links_with_other_mode_infra['links_with_train_station'][row['id']]]
                walk_links_with_other_mode_infra['links_with_both_stop_and_station'].update({row['id']: conc_list})
                walk_links_with_other_mode_infra['links_with_bus_stop'].pop(row['id'])
                walk_links_with_other_mode_infra['links_with_train_station'].pop(row['id'])
            if check_list == []:
                walk_links_with_other_mode_infra['links_with_no_infra'].append(row['id'])
    # print(walk_links_with_other_mode_infra)
    # print(len(walk_links_with_other_mode_infra['links_with_no_infra']) + len(walk_links_with_other_mode_infra['links_with_bus_stop']) + len(walk_links_with_other_mode_infra['links_with_train_station']) + len(walk_links_with_other_mode_infra['links_with_both_stop_and_station']))

    links_checked = []
    count = 0
    # link_with_no_infra_dist = {}
    with open('Road_Links.csv', 'r') as rl:
        RoadLinkReader = csv.DictReader(rl)
        for row in RoadLinkReader:
            if row['id'] in walk_links_with_other_mode_infra['links_with_no_infra']:
                if (row['from_node'], row['to_node']) not in links_checked:
                    link_polys_seq = {}
                    with open('Road_links_polyline.csv', 'r') as rlp:
                        RoadLinkPolyReader = csv.DictReader(rlp)
                        for i in RoadLinkPolyReader:
                            if i['id'] == row['id']:
                                link_polys_seq.update({i['seq_id']: [float(i['x']), float(i['y'])]})
                    link_part_list = []
                    for seq_id in link_polys_seq:
                        link_part_list.append(seq_id)
                    dist_walk_to_walk = 0
                    for k in range(len(link_part_list) - 1):
                        link_part = [link_polys_seq[link_part_list[k]], link_polys_seq[link_part_list[k + 1]]]
                        dist_walk_to_walk += math.sqrt(sum([(a - b) ** 2 for a, b in zip(link_part[0], link_part[1])]))
                    G.add_edge('w' + str(row['from_node']), 'w' + str(row['to_node']), id=row['id'], edge_type='walk_edge', from_node=row['from_node'], to_node=row['to_node'], distance=dist_walk_to_walk, travel_time=dist_walk_to_walk / 1.4)
                else:
                    count += 1
                    G.add_node('w' + str(row['from_node']) + ',' + str(count), id=row['from_node'], pos=G.nodes['w' + str(row['from_node'])]['pos'], node_type='walk_graph_node', node_graph_type='Walk', is_mode_dupl=False, walk_node_dupl=True, zone=G.nodes['w' + str(row['from_node'])]['zone'], to_mode='Walk')
                    G.add_node('w' + str(row['to_node']) + ',' + str(count), id=row['to_node'], pos=G.nodes['w' + str(row['to_node'])]['pos'], node_type='walk_graph_node', node_graph_type='Walk', is_mode_dupl=False, walk_node_dupl=True, zone=G.nodes['w' + str(row['to_node'])]['zone'], to_mode='Walk')

                    G.add_edge('w' + str(row['from_node']) + ',' + str(count), 'w' + str(row['to_node']) + ',' + str(count), id=row['id'], edge_type='walk_edge', from_node=row['from_node'], to_node=row['to_node'], duplicate=True, distance=G['w' + str(row['from_node'])]['w' + str(row['to_node'])]['distance'], travel_time=G['w' + str(row['from_node'])]['w' + str(row['to_node'])]['travel_time'])
                    # print(G.nodes['w' + str(row['from_node']) + ',' + str(i)]['id'], G.nodes['w' + str(row['to_node']) + ',' + str(i)]['id'])
                links_checked.append((row['from_node'], row['to_node']))
            elif row['id'] in walk_links_with_other_mode_infra['links_with_bus_stop']:
                bus_stop = walk_links_with_other_mode_infra['links_with_bus_stop'][row['id']]
                bus_stop_coord = G.nodes[bus_stop]['pos']
                link_polys_seq = {}
                with open('Road_links_polyline.csv', 'r') as rlp:
                    RoadLinkPolyReader = csv.DictReader(rlp)
                    for j in RoadLinkPolyReader:
                        if j['id'] == row['id']:
                            link_polys_seq.update({j['seq_id']: [float(j['x']), float(j['y'])]})
                link_part_list = []
                for seq_id in link_polys_seq:
                    link_part_list.append(seq_id)
                dist_walk_to_walk = 0
                dist_walk_to_bus_upstr = 0
                for m in range(len(link_part_list) - 1):
                    proj = find_proj(bus_stop_coord, link_polys_seq[link_part_list[m]], link_polys_seq[link_part_list[m + 1]])
                    eucl_dist_b_up = math.sqrt(sum([(a - b) ** 2 for a, b in zip(link_polys_seq[link_part_list[m]], proj)]))
                    eucl_dist_b_dstr = math.sqrt(sum([(a - b) ** 2 for a, b in zip(link_polys_seq[link_part_list[m + 1]], proj)]))
                    eucl_dist_p_to_p = math.sqrt(sum([(a - b) ** 2 for a, b in zip(link_polys_seq[link_part_list[m]], link_polys_seq[link_part_list[m + 1]])]))
                    if (eucl_dist_b_up < eucl_dist_p_to_p and eucl_dist_b_dstr < eucl_dist_p_to_p) or (eucl_dist_b_up == eucl_dist_p_to_p or eucl_dist_b_dstr == eucl_dist_p_to_p):
                        dist_walk_to_bus_upstr = dist_walk_to_walk + eucl_dist_b_up
                        G.add_edge('w' + str(row['from_node']), bus_stop, id=row['id'], edge_type='walk_edge', from_node=row['from_node'], to_node=bus_stop, distance=dist_walk_to_bus_upstr, travel_time=dist_walk_to_bus_upstr / 1.4)
                        G.add_edge(bus_stop, 'w' + str(row['from_node']), id=row['id'], edge_type='walk_edge', from_node=bus_stop, to_node=row['from_node'], distance=dist_walk_to_bus_upstr, travel_time=dist_walk_to_bus_upstr / 1.4)
                    dist_walk_to_walk += eucl_dist_p_to_p
                G.add_edge(bus_stop, 'w' + str(row['to_node']), id=row['id'], edge_type='walk_edge', from_node=bus_stop, to_node=row['to_node'], distance=dist_walk_to_walk - dist_walk_to_bus_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_bus_upstr) / 1.4)
                G.add_edge('w' + str(row['to_node']), bus_stop, id=row['id'], edge_type='walk_edge', from_node=row['to_node'], to_node=bus_stop, distance=dist_walk_to_walk - dist_walk_to_bus_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_bus_upstr) / 1.4)
            elif row['id'] in walk_links_with_other_mode_infra['links_with_train_station']:
                train_station = walk_links_with_other_mode_infra['links_with_train_station'][row['id']]
                train_station_coord = G.nodes[train_station]['pos']
                link_polys_seq = {}
                with open('Road_links_polyline.csv', 'r') as rlp:
                    RoadLinkPolyReader = csv.DictReader(rlp)
                    for z in RoadLinkPolyReader:
                        if z['id'] == row['id']:
                            link_polys_seq.update({z['seq_id']: [float(z['x']), float(z['y'])]})
                link_part_list = []
                for seq_id in link_polys_seq:
                    link_part_list.append(seq_id)
                dist_walk_to_walk = 0
                dist_walk_to_train_upstr = 0
                for w in range(len(link_part_list) - 1):
                    proj = find_proj(train_station_coord, link_polys_seq[link_part_list[w]], link_polys_seq[link_part_list[w + 1]])
                    eucl_dist_t_up = math.sqrt(sum([(a - b) ** 2 for a, b in zip(link_polys_seq[link_part_list[w]], proj)]))
                    eucl_dist_t_dstr = math.sqrt(sum([(a - b) ** 2 for a, b in zip(link_polys_seq[link_part_list[w + 1]], proj)]))
                    eucl_dist_p_to_p = math.sqrt(sum([(a - b) ** 2 for a, b in zip(link_polys_seq[link_part_list[w]], link_polys_seq[link_part_list[w + 1]])]))
                    if (eucl_dist_t_up < eucl_dist_p_to_p and eucl_dist_t_dstr < eucl_dist_p_to_p) or (eucl_dist_t_up == eucl_dist_p_to_p or eucl_dist_t_dstr == eucl_dist_p_to_p):
                        dist_walk_to_train_upstr = dist_walk_to_walk + eucl_dist_t_up
                        G.add_edge('w' + str(row['from_node']), train_station, id=row['id'], edge_type='walk_edge', from_node=row['from_node'], to_node=train_station, distance=dist_walk_to_train_upstr, travel_time=dist_walk_to_train_upstr / 1.4)
                        G.add_edge(train_station, 'w' + str(row['from_node']), id=row['id'], edge_type='walk_edge', from_node=train_station, to_node=row['from_node'], distance=dist_walk_to_train_upstr, travel_time=dist_walk_to_train_upstr / 1.4)
                    dist_walk_to_walk += eucl_dist_p_to_p
                G.add_edge(train_station, 'w' + str(row['to_node']), id=row['id'], edge_type='walk_edge', from_node=train_station, to_node=row['to_node'], distance=dist_walk_to_walk - dist_walk_to_train_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_train_upstr) / 1.4)
                G.add_edge('w' + str(row['to_node']), train_station, id=row['id'], edge_type='walk_edge', from_node=row['to_node'], to_node=train_station, distance=dist_walk_to_walk - dist_walk_to_train_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_train_upstr) / 1.4)
            elif row['id'] in walk_links_with_other_mode_infra['links_with_both_stop_and_station']:
                for node in walk_links_with_other_mode_infra['links_with_both_stop_and_station'][row['id']]:
                    if G.nodes[node]['to_mode'] == 'Bus':
                        bus_stop = node
                        bus_stop_coord = G.nodes[node]['pos']
                    elif G.nodes[node]['to_mode'] == 'Train':
                        train_station = node
                        train_station_coord = G.nodes[train_station]['pos']
                link_polys_seq = {}
                with open('Road_links_polyline.csv', 'r') as rlp:
                    RoadLinkPolyReader = csv.DictReader(rlp)
                    for q in RoadLinkPolyReader:
                        if q['id'] == row['id']:
                            link_polys_seq.update({q['seq_id']: [float(q['x']), float(q['y'])]})
                link_part_list = []
                for seq_id in link_polys_seq:
                    link_part_list.append(seq_id)
                dist_walk_to_walk = 0
                dist_walk_to_bus_upstr = 0
                dist_walk_to_train_upstr = 0
                case1 = case2 = case3 = case4 = False
                for q in range(len(link_part_list) - 1):
                    proj_b = find_proj(bus_stop_coord, link_polys_seq[link_part_list[q]], link_polys_seq[link_part_list[q + 1]])
                    proj_t = find_proj(train_station_coord, link_polys_seq[link_part_list[q]], link_polys_seq[link_part_list[q + 1]])
                    eucl_dist_b_up = math.sqrt(sum([(a - b) ** 2 for a, b in zip(link_polys_seq[link_part_list[q]], proj_b)]))
                    eucl_dist_b_dstr = math.sqrt(sum([(a - b) ** 2 for a, b in zip(link_polys_seq[link_part_list[q + 1]], proj_b)]))
                    eucl_dist_t_up = math.sqrt(sum([(a - b) ** 2 for a, b in zip(link_polys_seq[link_part_list[q]], proj_t)]))
                    eucl_dist_t_dstr = math.sqrt(sum([(a - b) ** 2 for a, b in zip(link_polys_seq[link_part_list[q + 1]], proj_t)]))
                    eucl_dist_p_to_p = math.sqrt(sum([(a - b) ** 2 for a, b in zip(link_polys_seq[link_part_list[q]], link_polys_seq[link_part_list[q + 1]])]))
                    # if both bus stop and train station in this polyline
                    if ((eucl_dist_b_up < eucl_dist_p_to_p and eucl_dist_b_dstr < eucl_dist_p_to_p) or (eucl_dist_b_up == eucl_dist_p_to_p or eucl_dist_b_dstr == eucl_dist_p_to_p)) and ((eucl_dist_t_up < eucl_dist_p_to_p and eucl_dist_t_dstr < eucl_dist_p_to_p) or (eucl_dist_t_up == eucl_dist_p_to_p or eucl_dist_t_dstr == eucl_dist_p_to_p)):
                        dist_walk_to_bus_upstr = dist_walk_to_walk + eucl_dist_b_up
                        dist_walk_to_train_upstr = dist_walk_to_walk + eucl_dist_t_up
                        # if bus stop first
                        if eucl_dist_b_up <= eucl_dist_t_up:
                            case1 = True
                            G.add_edge('w' + str(row['from_node']), bus_stop, id=row['id'], edge_type='walk_edge', from_node=row['from_node'], to_node=bus_stop, distance=dist_walk_to_bus_upstr, travel_time=dist_walk_to_bus_upstr / 1.4)
                            G.add_edge(bus_stop, 'w' + str(row['from_node']), id=row['id'], edge_type='walk_edge', from_node=bus_stop, to_node=row['from_node'], distance=dist_walk_to_bus_upstr, travel_time=dist_walk_to_bus_upstr / 1.4)
                            G.add_edge(bus_stop, train_station, id=row['id'], edge_type='walk_edge', from_node=bus_stop, to_node=train_station, distance=dist_walk_to_train_upstr - dist_walk_to_bus_upstr, travel_time=(dist_walk_to_train_upstr - dist_walk_to_bus_upstr) / 1.4)
                            if G[bus_stop][train_station]['distance'] < 0:
                                pass
                            G.add_edge(train_station, bus_stop, id=row['id'], edge_type='walk_edge', from_node=train_station, to_node=bus_stop, distance=dist_walk_to_train_upstr - dist_walk_to_bus_upstr, travel_time=(dist_walk_to_train_upstr - dist_walk_to_bus_upstr) / 1.4)
                            if G[train_station][bus_stop]['distance'] < 0:
                                pass
                        # if train station first
                        else:
                            case2 = True
                            G.add_edge('w' + str(row['from_node']), train_station, id=row['id'], edge_type='walk_edge', from_node=row['from_node'], to_node=train_station, distance=dist_walk_to_train_upstr, travel_time=dist_walk_to_train_upstr / 1.4)
                            G.add_edge(train_station, 'w' + str(row['from_node']), id=row['id'], edge_type='walk_edge', from_node=train_station, to_node=row['from_node'], distance=dist_walk_to_train_upstr, travel_time=dist_walk_to_train_upstr / 1.4)
                            G.add_edge(train_station, bus_stop, id=row['id'], edge_type='walk_edge', from_node=train_station, to_node=bus_stop, distance=dist_walk_to_bus_upstr - dist_walk_to_train_upstr, travel_time=(dist_walk_to_bus_upstr - dist_walk_to_train_upstr) / 1.4)
                            if G[train_station][bus_stop]['distance'] < 0:
                                pass
                            G.add_edge(bus_stop, train_station, id=row['id'], edge_type='walk_edge', from_node=bus_stop, to_node=train_station, distance=dist_walk_to_bus_upstr - dist_walk_to_train_upstr, travel_time=(dist_walk_to_bus_upstr - dist_walk_to_train_upstr) / 1.4)
                            if G[bus_stop][train_station]['distance'] < 0:
                                pass

                    # if bus stop in the poly
                    if (eucl_dist_b_up < eucl_dist_p_to_p and eucl_dist_b_dstr < eucl_dist_p_to_p) or (eucl_dist_b_up == eucl_dist_p_to_p or eucl_dist_b_dstr == eucl_dist_p_to_p):
                        if not(case1) and not(case2):
                            dist_walk_to_bus_upstr = dist_walk_to_walk + eucl_dist_b_up
                            case3 = True
                            if case4:
                                G.add_edge(train_station, bus_stop, id=row['id'], edge_type='walk_edge', from_node=train_station, to_node=bus_stop, distance=dist_walk_to_bus_upstr - dist_walk_to_train_upstr, travel_time=(dist_walk_to_bus_upstr - dist_walk_to_train_upstr) / 1.4)
                                if G[train_station][bus_stop]['distance'] < 0:
                                    pass
                                G.add_edge(bus_stop, train_station, id=row['id'], edge_type='walk_edge', from_node=bus_stop, to_node=train_station, distance=dist_walk_to_bus_upstr - dist_walk_to_train_upstr, travel_time=(dist_walk_to_bus_upstr - dist_walk_to_train_upstr) / 1.4)
                                if G[bus_stop][train_station]['distance'] < 0:
                                    pass
                            else:
                                G.add_edge('w' + str(row['from_node']), bus_stop, id=row['id'], edge_type='walk_edge', from_node=row['from_node'], to_node=bus_stop, distance=dist_walk_to_bus_upstr, travel_time=dist_walk_to_bus_upstr / 1.4)
                                G.add_edge(bus_stop, 'w' + str(row['from_node']), id=row['id'], edge_type='walk_edge', from_node=bus_stop, to_node=row['from_node'], distance=dist_walk_to_bus_upstr, travel_time=dist_walk_to_bus_upstr / 1.4)
                    # if train station in the poly
                    if (eucl_dist_t_up < eucl_dist_p_to_p and eucl_dist_t_dstr < eucl_dist_p_to_p) or (eucl_dist_t_up == eucl_dist_p_to_p or eucl_dist_t_dstr == eucl_dist_p_to_p):
                        if not(case1) and not(case2):
                            dist_walk_to_train_upstr = dist_walk_to_walk + eucl_dist_t_up
                            case4 = True
                            if case3:
                                G.add_edge(bus_stop, train_station, id=row['id'], edge_type='walk_edge', from_node=bus_stop, to_node=train_station, distance=dist_walk_to_train_upstr - dist_walk_to_bus_upstr, travel_time=(dist_walk_to_train_upstr - dist_walk_to_bus_upstr) / 1.4)
                                if G[bus_stop][train_station]['distance'] < 0:
                                    pass
                                G.add_edge(train_station, bus_stop, id=row['id'], edge_type='walk_edge', from_node=train_station, to_node=row['from_node'], distance=dist_walk_to_train_upstr - dist_walk_to_bus_upstr, travel_time=(dist_walk_to_train_upstr - dist_walk_to_bus_upstr) / 1.4)
                                if G[train_station][bus_stop]['distance'] < 0:
                                    pass
                            else:
                                G.add_edge('w' + str(row['from_node']), train_station, id=row['id'], edge_type='walk_edge', from_node=row['from_node'], to_node=train_station, distance=dist_walk_to_train_upstr, travel_time=dist_walk_to_train_upstr / 1.4)
                                G.add_edge(train_station, 'w' + str(row['from_node']), id=row['id'], edge_type='walk_edge', from_node=train_station, to_node=row['from_node'], distance=dist_walk_to_train_upstr, travel_time=dist_walk_to_train_upstr / 1.4)
                    dist_walk_to_walk += eucl_dist_p_to_p
                if case1:
                    G.add_edge(train_station, 'w' + str(row['to_node']), id=row['id'], edge_type='walk_edge', from_node=train_station, to_node=row['to_node'], distance=dist_walk_to_walk - dist_walk_to_train_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_train_upstr) / 1.4)
                    G.add_edge('w' + str(row['to_node']), train_station, id=row['id'], edge_type='walk_edge', from_node='w' + str(row['to_node']), to_node=train_station, distance=dist_walk_to_walk - dist_walk_to_train_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_train_upstr) / 1.4)
                elif case2:
                    G.add_edge(bus_stop, 'w' + str(row['to_node']), id=row['id'], edge_type='walk_edge', from_node=bus_stop, to_node=row['to_node'], distance=dist_walk_to_walk - dist_walk_to_bus_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_bus_upstr) / 1.4)
                    G.add_edge('w' + str(row['to_node']), bus_stop, id=row['id'], edge_type='walk_edge', from_node='w' + str(row['to_node']), to_node=bus_stop, distance=dist_walk_to_walk - dist_walk_to_bus_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_bus_upstr) / 1.4)
                elif case3 and case4:
                    if dist_walk_to_bus_upstr <= dist_walk_to_train_upstr:
                        G.add_edge(train_station, 'w' + str(row['to_node']), id=row['id'], edge_type='walk_edge', from_node=train_station, to_node=row['to_node'], distance=dist_walk_to_walk - dist_walk_to_train_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_train_upstr) / 1.4)
                        G.add_edge('w' + str(row['to_node']), train_station, id=row['id'], edge_type='walk_edge', from_node='w' + str(row['to_node']), to_node=train_station, distance=dist_walk_to_walk - dist_walk_to_train_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_train_upstr) / 1.4)
                    else:
                        G.add_edge(bus_stop, 'w' + str(row['to_node']), id=row['id'], edge_type='walk_edge', from_node=bus_stop, to_node=row['to_node'], distance=dist_walk_to_walk - dist_walk_to_bus_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_bus_upstr) / 1.4)
                        G.add_edge('w' + str(row['to_node']), bus_stop, id=row['id'], edge_type='walk_edge', from_node='w' + str(row['to_node']), to_node=bus_stop, distance=dist_walk_to_walk - dist_walk_to_bus_upstr, travel_time=(dist_walk_to_walk - dist_walk_to_bus_upstr) / 1.4)
