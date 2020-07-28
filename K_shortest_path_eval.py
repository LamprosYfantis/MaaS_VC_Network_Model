# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 23:29:34 2020

@author: User
"""


# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 14:16:21 2020

@author: User
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
# import json
# import yaml
import io
from itertools import permutations 
from networkx.algorithms.simple_paths import get_full_pareto_set, get_ε_pareto_set, get_bucket_pareto_set, \
    get_ellipse_pareto_set, get_ε_ratio_pareto_set, get_ε_bucket_pareto_set, get_shortest_weighted_path, \
        get_k_shortest_paths

start = time.time()
multimodal_graph = nx.read_gpickle("VC_multimodal_graph_discr30sec")
end = time.time()
print('Multimodal Network formulation running time is {}sec'.format(end - start))
# # print(multimodal_graph.nodes(data=True))
# print(multimodal_graph.number_of_nodes())
# print(multimodal_graph.number_of_edges())
start = time.time()
walk_graph = nx.read_gpickle("VC_walk_graph_discr30sec")
end = time.time()
print('Walking Network formulation running time is {}sec'.format(end - start))
# pos = nx.get_node_attributes(walk_graph, 'pos')
# nx.draw_networkx(walk_graph, pos)  # Graph with node attributes
# plt.show()
def profile(fnc):
    
    """A decorator that uses cProfile to profile a function"""
    
    def inner(*args, **kwargs):
        
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner
# OD_pairs = [('w11', 'w95'), ('w60', 'w89'), ('w90', 'w11'), ('w94', 'w60'), ('w7', 'w94'), ('w94', 'w13'), \
#             ('w90', 'w66'), ('w60', 'w80'), ('w31', 'w84'), ('w89', 'w7')]

#----- testing weighted shortest path
# walk_attrs_weights = [0.0467, 0, 0, 1, 0]  # weight of tt, wt, l, c, lt
# bus_attrs_weights = [0.0417, 0.05, 0, 1, 15]
# train_attrs_weights = [0.0417, 0.05, 0, 1, 15]
# taxi_attrs_weights = [0.0667, 0.075, 0, 1, 0]
# sms_attrs_weights = [0.05, 0.075, 0, 1, 0]
# sms_pool_attrs_weights = [0.0433, 0.075, 0, 1, 0]
# cs_attrs_weights = [0.0375, 0.05, 0.0015, 1, 0]
# mode_trf_weight = 15   # mt

dt = 30
request_time_sec = 28880

# start = time.time()

# walk_path_data = get_shortest_weighted_path(walk_graph, 'w11', 'w95', request_time_sec, request_time_sec, \
#                                        request_time_sec+30000, dt, walk_attrs_weights = walk_attrs_weights, \
#                                            bus_attrs_weights = bus_attrs_weights, \
#                                                train_attrs_weights = train_attrs_weights, \
#                                                    taxi_attrs_weights = taxi_attrs_weights, \
#                                                        sms_attrs_weights = sms_attrs_weights, \
#                                                            sms_pool_attrs_weights = sms_pool_attrs_weights, \
#                                                                cs_attrs_weights = cs_attrs_weights, \
#                                                                   mode_transfer_weight = mode_trf_weight)
# end = time.time()
# print(end-start)
# print(walk_path_data)

# i=0
# total_tt = 0
# while i<=len(walk_path_data['path'])-2:
#     from_node = walk_path_data['path'][i]
#     to_node = walk_path_data['path'][i+1]
#     total_tt += walk_graph[from_node][to_node]['travel_time']
#     i += 1
# # print(total_tt)
# time_horizon = int(total_tt)
# print(time_horizon)

walk_attrs_weights = [0.0467, 0, 0, 1, 0]  # weight of tt, wt, l, c, b
bus_attrs_weights = [0.0417, 0.05, 0, 1, 15]
train_attrs_weights = [0.0417, 0.05, 0, 1, 15]
taxi_attrs_weights = [0.0667, 0.075, 0, 1, 0]
sms_attrs_weights = [0.05, 0.075, 0, 1, 0]
sms_pool_attrs_weights = [0.0433, 0.075, 0, 1, 0]
cs_attrs_weights = [0.0375, 0.05, 0, 1, 0]
mode_transfer_weight = 15   # mt

# start = time.time()
# @profile
# def elamou():
shortest_path =get_k_shortest_paths(multimodal_graph, 'w11', 'w95', request_time_sec, request_time_sec, \
                                       request_time_sec+3600, dt, 5, walk_attrs_weights = walk_attrs_weights, \
                                           bus_attrs_weights = bus_attrs_weights, \
                                               train_attrs_weights = train_attrs_weights, \
                                                   taxi_attrs_weights = taxi_attrs_weights, \
                                                       sms_attrs_weights = sms_attrs_weights, \
                                                           sms_pool_attrs_weights = sms_pool_attrs_weights, \
                                                               cs_attrs_weights = cs_attrs_weights, \
                                                                   mode_transfer_weight = mode_transfer_weight)
    # return shortest_path
# lam = elamou()
end = time.time()
print(end-start)
print(shortest_path)