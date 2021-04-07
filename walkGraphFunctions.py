import csv
import math
#import time
import networkx as nx
#import pandas as pd
import numpy as np
# from shapely.geometry import Point, LineString
#from numpy.linalg import norm
#from networkx.classes.function import number_of_edges, number_of_nodes

# specification of the time discrtization step (time interval)
dt = 30

def gen_walk_graph_nodes(G):
    # create the node from the actual walk network
    with open('Road_nodes_coord.csv', 'r') as rnc:
        RoadNodeReader = csv.DictReader(rnc)
        for row in RoadNodeReader:
            G.add_node('w' + str(row['id']), id=row['id'], pos=[float(row['x']), float(row['y'])], node_type='walk_graph_node', node_graph_type='Walk', \
                       is_mode_dupl=False, walk_node_dupl=False, to_mode='Walk')
            with open('node_taz_mapping.csv', 'r') as ntm:
                NodeTazMapReader = csv.DictReader(ntm)
                for line in NodeTazMapReader:
                    if row['id'] == line['node_id']:
                        G.nodes['w' + str(row['id'])]['zone'] = line['taz']
                        break
                        
def gen_walk_graph_edges(G):               
    links_checked = [] # list that stores the (from_node, to_node) links that are being added; if we have more than one link from the same node to the same node (multidirected) then
    # we create duplicates of from and to nodes since NetworkX directed graph would not create the same link twice and we would miss links
    count = 0
    duplicated_node_list = list()
    with open('Road_Links.csv', 'r') as rl:
        RoadLinkReader = csv.DictReader(rl)
        for row in RoadLinkReader:
            link_polys_seq = {}
            with open('Road_links_polyline.csv', 'r') as rlp:
                RoadLinkPolyReader = csv.DictReader(rlp)
                for i in RoadLinkPolyReader:
                    if i['id'] == row['id']:
                        link_polys_seq.update({i['seq_id']: [float(i['x']), float(i['y'])]})
                dist_walk_to_walk = 0
                for k in range(len(link_polys_seq) - 1):
                    link_part = [link_polys_seq[str(k)], link_polys_seq[str(k + 1)]]
                    dist_walk_to_walk += math.sqrt(sum([(a - b) ** 2 for a, b in zip(link_part[0], link_part[1])]))
            tt = dist_walk_to_walk/1.4
            discr_tt = tt - (tt%dt)
            if (row['from_node'], row['to_node']) not in links_checked:
                G.add_edge('w' + str(row['from_node']), 'w' + str(row['to_node']), id=row['id'], edge_type='walk_edge', from_node=row['from_node'], \
                           to_node=row['to_node'], distance=dist_walk_to_walk, travel_time=discr_tt, \
                           up_node_graph_type=G.nodes['w' + str(row['from_node'])]['node_graph_type'], \
                           dstr_node_graph_type=G.nodes['w' + str(row['to_node'])]['node_graph_type'], \
                           up_node_type=G.nodes['w' + str(row['from_node'])]['node_type'], dstr_node_type=G.nodes['w' + str(row['to_node'])]['node_type'], \
                           up_node_zone=G.nodes['w' + str(row['from_node'])]['zone'], dstr_node_zone=G.nodes['w' + str(row['to_node'])]['zone'])
                if duplicated_node_list:
                    for u,info in G.nodes(data=True):
                        for node in duplicated_node_list:
                            if info['id'] == row['to_node'] and u != 'w' + str(row['to_node']):
                                G.add_edge('w' + str(row['from_node']), u, id='new_id', edge_type='walk_edge', \
                                   from_node=row['from_node'], to_node=info['id'], duplicate=True, distance=dist_walk_to_walk, \
                                   travel_time=discr_tt, up_node_graph_type=G.nodes['w' + str(row['from_node'])]['node_graph_type'], \
                                   dstr_node_graph_type=info['node_graph_type'], \
                                   up_node_type=G.nodes['w' + str(row['from_node'])]['node_type'], \
                                   dstr_node_type=info['node_type'], \
                                   up_node_zone=G.nodes['w' + str(row['from_node'])]['zone'], dstr_node_zone=info['zone'])
                            if info['id'] == row['from_node'] and u != 'w' + str(row['from_node']):
                                G.add_edge(u, 'w' + str(row['to_node']), id='new_id', edge_type='walk_edge', \
                                   from_node=info['id'], to_node=row['to_node'], duplicate=True, distance=dist_walk_to_walk, \
                                   travel_time=discr_tt, up_node_graph_type=info['node_graph_type'], \
                                   dstr_node_graph_type=G.nodes['w' + str(row['to_node'])]['node_graph_type'], \
                                   up_node_type=info['node_type'], \
                                   dstr_node_type=G.nodes['w' + str(row['to_node'])]['node_type'], \
                                   up_node_zone=info['zone'], dstr_node_zone=G.nodes['w' + str(row['to_node'])]['zone'])
            else:
                count += 1
                duplicated_node_list.append(row['from_node'])
                G.add_node('w' + str(row['from_node']) + ',' + str(count), id=row['from_node'], pos=G.nodes['w' + str(row['from_node'])]['pos'], \
                           node_type='walk_graph_node', node_graph_type='Walk', is_mode_dupl=False, walk_node_dupl=True, \
                           zone=G.nodes['w' + str(row['from_node'])]['zone'], to_mode='Walk')
                
                G.add_edge('w' + str(row['from_node']) + ',' + str(count), 'w' + str(row['to_node']), id=row['id'], edge_type='walk_edge', \
                           from_node=row['from_node'], to_node=row['to_node'], duplicate=True, \
                           distance=G['w' + str(row['from_node'])]['w' + str(row['to_node'])]['distance'], \
                           travel_time=G['w' + str(row['from_node'])]['w' + str(row['to_node'])]['travel_time'], \
                           up_node_graph_type=G.nodes['w' + str(row['from_node']) + ',' + str(count)]['node_graph_type'], \
                           dstr_node_graph_type=G.nodes['w' + str(row['to_node'])]['node_graph_type'], \
                           up_node_type=G.nodes['w' + str(row['from_node']) + ',' + str(count)]['node_type'], \
                           dstr_node_type=G.nodes['w' + str(row['to_node'])]['node_type'], \
                           up_node_zone=G.nodes['w' + str(row['from_node']) + ',' + str(count)]['zone'], dstr_node_zone=G.nodes['w' + str(row['to_node'])]['zone'])
                for u,v,info in G.edges(data=True):
                    if info['to_node'] == row['from_node'] and info['from_node'] != row['to_node']:
                        G.add_edge(u, 'w' + str(row['from_node']) + ',' + str(count), id='new_id', edge_type='walk_edge', \
                           from_node=info['from_node'], to_node=row['from_node'], duplicate=True, distance=info['distance'], \
                           travel_time=info['travel_time'], \
                           up_node_graph_type=G.nodes[u]['node_graph_type'], \
                           dstr_node_graph_type=G.nodes['w' + str(row['from_node']) + ',' + str(count)]['node_graph_type'], \
                           up_node_type=G.nodes[u]['node_type'], \
                           dstr_node_type=G.nodes['w' + str(row['from_node']) + ',' + str(count)]['node_type'], \
                           up_node_zone=G.nodes[u]['zone'], dstr_node_zone=G.nodes['w' + str(row['from_node']) + ',' + str(count)]['zone'])
                    elif info['from_node'] == row['from_node'] and info['to_node'] != row['to_node']:
                        G.add_edge('w' + str(row['from_node']) + ',' + str(count), v, id='new_id', edge_type='walk_edge', \
                           from_node=row['from_node'], to_node=info['to_node'], duplicate=True, distance=info['distance'], \
                           travel_time=info['travel_time'], \
                           up_node_graph_type=G.nodes['w' + str(row['from_node']) + ',' + str(count)]['node_graph_type'], \
                           dstr_node_graph_type=G.nodes[v]['node_graph_type'], \
                           up_node_type=G.nodes['w' + str(row['from_node']) + ',' + str(count)]['node_type'], \
                           dstr_node_type=G.nodes[v]['node_type'], \
                           up_node_zone=G.nodes['w' + str(row['from_node']) + ',' + str(count)]['zone'], dstr_node_zone=G.nodes[v]['zone'])
            links_checked.append((row['from_node'], row['to_node']))