# -*- coding: utf-8 -*-
"""
Created on Wed May 15 10:20:44 2019

@author: Francisco
"""

import csv
import networkx as nx
with open('C:/Users/Francisco/OneDrive/Documentos/DTU/Spring 19/Master thesis/Virtual-City/VC_Network_Data_Fran/Bus_Network_data/Bus_stops_coord.csv', 'r') as bsc:
    BusStopsReader = csv.DictReader(bsc, delimiter=',')
    # print(BusStopsReader)
    Bus_Graph=nx.MultiDiGraph()
    for row in BusStopsReader:                                                 # bus stop connections in our graph are represented as straght lines
        Bus_Graph.add_node(row['code'], pos=[float(row['x']), float(row['y'])], station=row['name'], node_type='stop_node')
    print(Bus_Graph.nodes(data=True))