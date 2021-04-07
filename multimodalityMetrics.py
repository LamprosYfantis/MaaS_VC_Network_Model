# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 11:59:14 2021

@author: yfala
"""

import cProfile, pstats, io
import csv
import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import random
import re
import statistics
import time
import pickle
import io
import logging

from itertools import permutations 
from networkx.algorithms.simple_paths import get_full_pareto_set_correcting, get_ε_pareto_set_correcting, \
    get_bucket_pareto_set_correcting, get_shortest_weighted_path, \
        get_full_pareto_set_setting, get_bucket_pareto_set_setting, get_ε_pareto_set_setting, get_slack_pareto_set_setting, \
            get_slack_pareto_set_correcting
            
            
start = time.time()
multimodal_graph = nx.read_gpickle("VC_multimodal_graph_discr30sec")
end = time.time()
# print(multimodal_graph.number_of_nodes())
# print(multimodal_graph.number_of_edges())
print('Multimodal Network formulation running time is {}sec'.format(end - start))
# # print(multimodal_graph.nodes(data=True))
# print(multimodal_graph.number_of_nodes())
# print(multimodal_graph.number_of_edges())

##### reading pareto set file for an algorithm
with open('Pareto_set_h-DMLC-U-UB.pickle', 'rb') as handle:
    test_set = pickle.load(handle)
    
#### computing average multimodal path percentages for an algorithm
multimodal_path_percentages_list = list()
for OD, details in test_set.items():
    mutlimodal_path_counter = 0
    # print(test_set[OD])
    for path_id, stuff in details.items():
        # print(stuff['path'])
        mode_list = list()
        for i in range(len(stuff['path'])):
            node = stuff['path'][i]
            mode = multimodal_graph.nodes[node]['node_graph_type']
            if mode != 'Walk':
                if multimodal_graph.nodes[stuff['path'][i-1]]['node_graph_type'] == 'Walk' and \
                    multimodal_graph.nodes[stuff['path'][i+1]]['node_graph_type'] == 'Walk':
                    continue
                if not mode_list:
                    mode_list.append(mode)
                    continue
                if mode_list[-1] != mode:
                    mode_list.append(mode)
        if len(mode_list) > 1:
            mutlimodal_path_counter += 1
    multimodal_path_percentages_list.append((mutlimodal_path_counter/len(details))*100)
    
# print(multimodal_path_percentages_list)

average_multimodal_path_percentages = sum(multimodal_path_percentages_list)/len(multimodal_path_percentages_list)
stdv_multimodal_path_percentages = statistics.stdev(multimodal_path_percentages_list)

print(average_multimodal_path_percentages)
print(stdv_multimodal_path_percentages)



######### computing average percentages for each mode combination and each algorithm
bus_percentages_list = list()
train_percentages_list = list()
taxi_percentages_list = list()
single_percentages_list = list()
shared_percentages_list = list()
carsharing_percentages_list = list()
bus_train_percentages_list = list()
bus_taxi_percentages_list = list()
bus_single_percentages_list = list()
bus_shared_percentages_list = list()
bus_carsharing_percentages_list = list()
train_taxi_percentages_list = list()
train_single_percentages_list = list()
train_shared_percentages_list = list()
train_carsharing_percentages_list = list()
taxi_carsharing_percentages_list = list()
single_carsharing_percentages_list = list()
shared_carsharing_percentages_list = list()
other_list = list()


for OD, details in test_set.items():
    mode_comb_counter = {'bus':0, 'train':0, 'taxi':0, 'single':0, 'shared':0, 'carsharing':0, \
                             'bus_train':0, 'bus_taxi':0, 'bus_single':0, 'bus_shared':0, 'bus_carsharing':0, \
                                 'train_taxi':0, 'train_single':0, 'train_shared':0, 'train_carsharing':0, \
                                     'taxi_carsharing':0, 'single_carsharing':0, 'shared_carsharing':0, 'other':0}
    # print(test_set[OD])
    for path_id, stuff in details.items():
        mode_list = list()
        for i in range(len(stuff['path'])):
            node = stuff['path'][i]
            mode = multimodal_graph.nodes[node]['node_graph_type']
            if mode != 'Walk':
                if multimodal_graph.nodes[stuff['path'][i-1]]['node_graph_type'] == 'Walk' and \
                    multimodal_graph.nodes[stuff['path'][i+1]]['node_graph_type'] == 'Walk':
                    continue
                if not mode_list:
                    mode_list.append(mode)
                    continue
                if mode_list[-1] != mode:
                    mode_list.append(mode)
        if mode_list == ['Bus']:
            mode_comb_counter['bus'] +=1
        elif mode_list == ['Train']:
            mode_comb_counter['train'] +=1
        elif mode_list == ['taxi_graph']:
            mode_comb_counter['taxi'] +=1
        elif mode_list == ['on_demand_single_taxi_graph']:
            mode_comb_counter['single'] +=1
        elif mode_list == ['on_demand_shared_taxi_graph']:
            mode_comb_counter['shared'] +=1
        elif mode_list == ['car_sharing_graph']:
            mode_comb_counter['carsharing'] +=1
        
        
        elif mode_list == ['Bus', 'Train'] or mode_list == ['Train', 'Bus']:
            mode_comb_counter['bus_train'] +=1
        elif mode_list == ['Bus', 'taxi_graph'] or mode_list == ['taxi_graph', 'Bus']:
            mode_comb_counter['bus_taxi'] +=1
        elif mode_list == ['Bus', 'on_demand_single_taxi_graph'] or mode_list == ['on_demand_single_taxi_graph', 'Bus']:
            mode_comb_counter['bus_single'] +=1
        elif mode_list == ['Bus', 'on_demand_shared_taxi_graph'] or mode_list == ['on_demand_shared_taxi_graph', 'Bus']:
            mode_comb_counter['bus_shared'] +=1
        elif mode_list == ['Bus', 'car_sharing_graph'] or mode_list == ['car_sharing_graph', 'Bus']:
            mode_comb_counter['bus_carsharing'] +=1
        
        
        elif mode_list == ['Train', 'taxi_graph'] or mode_list == ['taxi_graph', 'Train']:
            mode_comb_counter['train_taxi'] +=1
        elif mode_list == ['Train', 'on_demand_single_taxi_graph'] or mode_list == ['on_demand_single_taxi_graph', 'Train']:
            mode_comb_counter['train_single'] +=1
        elif mode_list == ['Train', 'on_demand_shared_taxi_graph'] or mode_list == ['on_demand_shared_taxi_graph', 'Train']:
            mode_comb_counter['train_shared'] +=1
        elif mode_list == ['Train', 'car_sharing_graph'] or mode_list == ['car_sharing_graph', 'Train']:
            mode_comb_counter['train_carsharing'] +=1
        
        
        elif mode_list == ['taxi_graph', 'car_sharing_graph'] or mode_list == ['car_sharing_graph', 'taxi_graph']:
            mode_comb_counter['taxi_carsharing'] +=1
        elif mode_list == ['on_demand_single_taxi_graph', 'car_sharing_graph'] or mode_list == ['car_sharing_graph', 'on_demand_single_taxi_graph']:
            mode_comb_counter['single_carsharing'] +=1
        elif mode_list == ['on_demand_shared_taxi_graph', 'car_sharing_graph'] or mode_list == ['car_sharing_graph', 'on_demand_shared_taxi_graph']:
            mode_comb_counter['shared_carsharing'] +=1
        else:
            if not mode_list:
                pass
            else:
                # print(mode_list)
                mode_comb_counter['other'] +=1
        
    for key in mode_comb_counter:
        mode_comb_counter[key] = (mode_comb_counter[key]/len(details))*100
    
    bus_percentages_list.append(mode_comb_counter['bus'])
    train_percentages_list.append(mode_comb_counter['train'])
    taxi_percentages_list.append(mode_comb_counter['taxi'])
    single_percentages_list.append(mode_comb_counter['single'])
    shared_percentages_list.append(mode_comb_counter['shared'])
    carsharing_percentages_list.append(mode_comb_counter['carsharing'])
    bus_train_percentages_list.append(mode_comb_counter['bus_train'])
    bus_taxi_percentages_list.append(mode_comb_counter['bus_taxi'])
    bus_single_percentages_list.append(mode_comb_counter['bus_single'])
    bus_shared_percentages_list.append(mode_comb_counter['bus_shared'])
    bus_carsharing_percentages_list.append(mode_comb_counter['bus_carsharing'])
    train_taxi_percentages_list.append(mode_comb_counter['train_taxi'])
    train_single_percentages_list.append(mode_comb_counter['train_single'])
    train_shared_percentages_list.append(mode_comb_counter['train_shared'])
    train_carsharing_percentages_list.append(mode_comb_counter['train_carsharing'])
    taxi_carsharing_percentages_list.append(mode_comb_counter['taxi_carsharing'])
    single_carsharing_percentages_list.append(mode_comb_counter['single_carsharing'])
    shared_carsharing_percentages_list.append(mode_comb_counter['shared_carsharing'])
    other_list.append(mode_comb_counter['other'])

# print(multimodal_path_percentages_list)

average_bus_percentages_list = sum(bus_percentages_list)/len(bus_percentages_list)
stdv_bus_percentages_list = statistics.stdev(bus_percentages_list)
print(average_bus_percentages_list)
print(stdv_bus_percentages_list)
print('')

average_train_percentages_list = sum(train_percentages_list)/len(train_percentages_list)
stdv_train_percentages_list = statistics.stdev(train_percentages_list)
print(average_train_percentages_list)
print(stdv_train_percentages_list)
print('')

average_taxi_percentages_list = sum(taxi_percentages_list)/len(taxi_percentages_list)
stdv_taxi_percentages_list = statistics.stdev(taxi_percentages_list)
print(average_taxi_percentages_list)
print(stdv_taxi_percentages_list)
print('')

average_single_percentages_list = sum(single_percentages_list)/len(single_percentages_list)
stdv_single_percentages_list = statistics.stdev(single_percentages_list)
print(average_single_percentages_list)
print(stdv_single_percentages_list)
print('')

average_shared_percentages_list = sum(shared_percentages_list)/len(shared_percentages_list)
stdv_shared_percentages_list = statistics.stdev(shared_percentages_list)
print(average_shared_percentages_list)
print(stdv_shared_percentages_list)
print('')

average_carsharing_percentages_list = sum(carsharing_percentages_list)/len(carsharing_percentages_list)
stdv_carsharing_percentages_list = statistics.stdev(carsharing_percentages_list)
print(average_carsharing_percentages_list)
print(stdv_carsharing_percentages_list)
print('')

average_bus_train_percentages_list = sum(bus_train_percentages_list)/len(bus_train_percentages_list)
stdv_bus_train_percentages_list = statistics.stdev(bus_train_percentages_list)
print(average_bus_train_percentages_list)
print(stdv_bus_train_percentages_list)
print('')

average_bus_taxi_percentages_list = sum(bus_taxi_percentages_list)/len(bus_taxi_percentages_list)
stdv_bus_taxi_percentages_list = statistics.stdev(bus_taxi_percentages_list)
print(average_bus_taxi_percentages_list)
print(stdv_bus_taxi_percentages_list)
print('')

average_bus_single_percentages_list = sum(bus_single_percentages_list)/len(bus_single_percentages_list)
stdv_bus_single_percentages_list = statistics.stdev(bus_single_percentages_list)
print(average_bus_single_percentages_list)
print(stdv_bus_single_percentages_list)
print('')

average_bus_shared_percentages_list = sum(bus_shared_percentages_list)/len(bus_shared_percentages_list)
stdv_bus_shared_percentages_list = statistics.stdev(bus_shared_percentages_list)
print(average_bus_shared_percentages_list)
print(stdv_bus_shared_percentages_list)
print('')

average_bus_carsharing_percentages_list = sum(bus_carsharing_percentages_list)/len(bus_carsharing_percentages_list)
stdv_bus_carsharing_percentages_list = statistics.stdev(bus_carsharing_percentages_list)
print(average_bus_carsharing_percentages_list)
print(stdv_bus_carsharing_percentages_list)
print('')

average_train_taxi_percentages_list = sum(train_taxi_percentages_list)/len(train_taxi_percentages_list)
stdv_train_taxi_percentages_list = statistics.stdev(train_taxi_percentages_list)
print(average_train_taxi_percentages_list)
print(stdv_train_taxi_percentages_list)
print('')

average_train_single_percentages_list = sum(train_single_percentages_list)/len(train_single_percentages_list)
stdv_train_single_percentages_list = statistics.stdev(train_single_percentages_list)
print(average_train_single_percentages_list)
print(stdv_train_single_percentages_list)
print('')

average_train_shared_percentages_list = sum(train_shared_percentages_list)/len(train_shared_percentages_list)
stdv_train_shared_percentages_list = statistics.stdev(train_shared_percentages_list)
print(average_train_shared_percentages_list)
print(stdv_train_shared_percentages_list)
print('')

average_train_carsharing_percentages_list = sum(train_carsharing_percentages_list)/len(train_carsharing_percentages_list)
stdv_train_carsharing_percentages_list= statistics.stdev(train_carsharing_percentages_list)
print(average_train_carsharing_percentages_list)
print(stdv_train_carsharing_percentages_list)
print('')

average_taxi_carsharing_percentages_list = sum(taxi_carsharing_percentages_list)/len(taxi_carsharing_percentages_list)
stdv_taxi_carsharing_percentages_list= statistics.stdev(taxi_carsharing_percentages_list)
print(average_taxi_carsharing_percentages_list)
print(stdv_taxi_carsharing_percentages_list)
print('')

average_single_carsharing_percentages_list = sum(single_carsharing_percentages_list)/len(single_carsharing_percentages_list)
stdv_single_carsharing_percentages_list= statistics.stdev(single_carsharing_percentages_list)
print(average_single_carsharing_percentages_list)
print(stdv_single_carsharing_percentages_list)
print('')

average_shared_carsharing_percentages_list = sum(shared_carsharing_percentages_list)/len(shared_carsharing_percentages_list)
stdv_shared_carsharing_percentages_list= statistics.stdev(shared_carsharing_percentages_list)
print(average_shared_carsharing_percentages_list)
print(stdv_shared_carsharing_percentages_list)
print('')

average_other_list = sum(other_list)/len(other_list)
stdv_other_list= statistics.stdev(other_list)
print(average_other_list)
print(stdv_other_list)
print('')


