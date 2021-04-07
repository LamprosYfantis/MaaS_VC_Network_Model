# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 19:18:27 2021

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
from networkx.algorithms.simple_paths import get_full_pareto_set_dmlc, get_pareto_set_h_dmlc_u, get_pareto_set_h_dmlc_u_ub, \
    get_pareto_set_h_dmlc_u_ub_c, get_pareto_set_h_dmlc_u_ub_e, get_pareto_set_h_dmlc_u_ub_c_e, get_pareto_set_h_dmlc_u_ub_b, \
        get_pareto_set_h_dmlc_u_ub_c_b, get_pareto_set_h_dmlc_u_ub_s, get_pareto_set_h_dmlc_u_ub_c_s, get_full_pareto_set_dmls, \
            get_full_pareto_set_h_dmls_u, get_full_pareto_set_h_dmls_u_c, get_pareto_set_h_dmls_u_e, get_pareto_set_h_dmls_u_c_e, \
                get_pareto_set_h_dmls_u_b, get_pareto_set_h_dmls_u_c_b, get_pareto_set_h_dmls_u_s, get_pareto_set_h_dmls_u_c_s, \
                    get_full_pareto_set_dijkstra
        
# logging.basicConfig(level = logging.DEBUG, filename = 'ods_log_for_memory.log')

# def profile(fnc):
    
#     """A decorator that uses cProfile to profile a function"""
    
#     def inner(*args, **kwargs):
        
#         pr = cProfile.Profile()
#         pr.enable()
#         retval = fnc(*args, **kwargs)
#         pr.disable()
#         s = io.StringIO()
#         sortby = 'cumulative'
#         ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
#         ps.print_stats()
#         print(s.getvalue())
#         return retval

#     return inner

#------------------ reading the pre-generated MaaS supernetwork model ----------#
start = time.time()
multimodal_graph = nx.read_gpickle("VC_multimodal_graph_discr30sec")
end = time.time()
# print(multimodal_graph.number_of_nodes())
# print(multimodal_graph.number_of_edges())
print('Multimodal Network formulation running time is {}sec'.format(end - start))
# # print(multimodal_graph.nodes(data=True))
# print(multimodal_graph.number_of_nodes())
# print(multimodal_graph.number_of_edges())

#------------------ reading the pre-generated walk graph -------#
start = time.time()
walk_graph = nx.read_gpickle("VC_walk_graph_discr30sec")
end = time.time()
# print(walk_graph.number_of_nodes())
# print(walk_graph.number_of_edges())
print('Walking Network formulation running time is {}sec'.format(end - start))

#----- reading a pre-generated file with the optimal walking times for each OD in the network
with open('VC_all_OD_walk_times_30sec.pickle', 'rb') as handle:
    walk_times_per_OD = pickle.load(handle)

#------ an indicative randomly selected OD sample ----#
OD_pairs = [('w55', 'w101'), ('w71', 'w17'), ('w36', 'w42'), ('w69', 'w20'), ('w50', 'w8'), ('w15', 'w14'), ('w15', 'w42'), ('w41', 'w80'), ('w62', 'w38'), ('w59', 'w60'), ('w61', 'w56'), ('w23', 'w45'), ('w20', 'w48'), ('w28', 'w67'), ('w63', 'w40'), ('w29', 'w41'), ('w40', 'w60'), ('w10', 'w22'), ('w19', 'w62'), ('w43', 'w17'), ('w51', 'w33'), ('w18', 'w67'), ('w69', 'w67'), ('w15', 'w101'), ('w35', 'w44'), ('w32', 'w15'), ('w27', 'w61'), ('w39', 'w51'), ('w65', 'w41'), ('w32', 'w65'), ('w49', 'w36'), ('w20', 'w6'), ('w9', 'w13'), ('w67', 'w8'), ('w22', 'w35'), ('w33', 'w9'), ('w29', 'w58'), ('w23', 'w33'), ('w72', 'w57'), ('w22', 'w101'), ('w19', 'w49'), ('w18', 'w100'), ('w63', 'w35'), ('w80,1', 'w24'), ('w9', 'w37'), ('w72', 'w53'), ('w47', 'w20'), ('w49', 'w64'), ('w80,1', 'w50'), ('w100', 'w36'), ('w50', 'w101'), ('w22', 'w31'), ('w57', 'w61'), ('w19', 'w9'), ('w21', 'w39'), ('w80,1', 'w23'), ('w61', 'w33'), ('w31', 'w72'), ('w51', 'w31'), ('w30', 'w9'), ('w5', 'w8'), ('w11', 'w43'), ('w51', 'w28'), ('w52', 'w61'), ('w15', 'w22'), ('w21', 'w51'), ('w24', 'w69'), ('w44', 'w25'), ('w24', 'w9'), ('w36', 'w47'), ('w18', 'w15'), ('w65', 'w34'), ('w33', 'w80'), ('w42', 'w18'), ('w49', 'w12'), ('w34', 'w58'), ('w52', 'w18'), ('w100', 'w15'), ('w28', 'w58'), ('w8', 'w69'), ('w71', 'w48'), ('w60', 'w65'), ('w29', 'w28'), ('w31', 'w105'), ('w105', 'w42'), ('w55', 'w72'), ('w102', 'w14'), ('w51', 'w80,1'), ('w11', 'w36'), ('w56', 'w67'), ('w65', 'w39'), ('w20', 'w37'), ('w57', 'w66'), ('w51', 'w65'), ('w8', 'w40'), ('w21', 'w31'), ('w105', 'w11'), ('w11', 'w33'), ('w69', 'w28'), ('w14', 'w18'), ('w64', 'w37')]

#--- the time inteval
dt = 30

#---- the query request time - e.g., am/pm peak hour
request_time_sec = 65400 #30600


################## loading the benchmark Pareto set for heuristic evaluation (if needed)

# with open('full_Pareto_set_DMLS.pickle', 'rb') as handle:
#     fullParetoSet = pickle.load(handle)
# with open('norm_full_Pareto_set_DMLS.pickle', 'rb') as handle:
#     normFullParetoSet = pickle.load(handle)

# with open('Pareto_set_h-DMLS-U.pickle', 'rb') as handle:
#     fullParetoSet = pickle.load(handle)
# with open('norm_Pareto_set_h-DMLS-U.pickle', 'rb') as handle:
#     normFullParetoSet = pickle.load(handle)
    

    
# #------------ script for running and getting metrics for non-ratio-based heuristics ---------------------#
Pareto_set = dict()
CPU_list = list()
Pareto_set_size = list()
Redundant_label_num = list()

for OD in OD_pairs:
    # print(OD)
    Pareto_set.update({OD: dict()})
    time_horizon = int(walk_times_per_OD[OD])
    # time_horizons.append(time_horizon)

    start = time.time()
    pareto_set, redundant_label_num = get_full_pareto_set_dmlc(multimodal_graph, OD[0], OD[1], request_time_sec, \
                                        request_time_sec, request_time_sec+time_horizon, dt)
    end = time.time()
    
    Pareto_set[OD] = pareto_set
    CPU_list.append(end - start)
    # print(end-start)
    Pareto_set_size.append(len(pareto_set))
    Redundant_label_num.append(redundant_label_num)
    # print(cpu_list)
    # print(len(pareto_set))
    # print(missed_path_percentages)


average_CPU = sum(CPU_list)/len(CPU_list)
stdv_CPU = statistics.stdev(CPU_list)

average_pareto_set_size = sum(Pareto_set_size)/len(Pareto_set_size)
stdv_pareto_set_size = statistics.stdev(Pareto_set_size)

average_red_labels = sum(Redundant_label_num)/len(Redundant_label_num)
stdv_average_red_labels = statistics.stdev(Redundant_label_num)

##### metric for the exact solution algorithms
# performance_metrics = {'CPU': {'μ': average_CPU, 'σ': stdv_CPU}, \
#                         'Pareto_set_size': {'μ': average_pareto_set_size, 'σ': stdv_pareto_set_size}, \
#                         'redundant_labels': {'μ': average_red_labels, 'σ': stdv_average_red_labels}}

# print(performance_metrics)

########## further processing for the extraction of metrics for heuristics
# with open('Pareto_set_h-DMLC-U-UB-S0-10-0-300.pickle', 'wb') as handle:
#     pickle.dump(Pareto_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('Pareto_set_h-DMLC-U-UB-S0-10-0-300.pickle', 'rb') as handle:
#     ParetoSet = pickle.load(handle)

# #---- normalize the labels of the Pareto Set ------------#
# normParetoSet = dict()
# for OD, attrs in ParetoSet.items():
#     normParetoSet.update({OD: dict()})
#     travel_times = list()
#     mon_costs = list()
#     trips = list()
#     walk_times = list()
#     for path_id, info in attrs.items():
#         travel_times.append(info['label'][0])
#         mon_costs.append(info['label'][1])
#         trips.append(info['label'][2])
#         walk_times.append(info['label'][3])
#     min_travel_time = min(travel_times)
#     max_travel_time = max(travel_times)
#     min_mon_cost = min(mon_costs)
#     max_mon_cost = max(mon_costs)
#     min_trips = min(trips)
#     max_trips = max(trips)
#     min_walk_time = min(walk_times)
#     max_walk_time = max(walk_times)
    
#     for path_id, info in attrs.items():
#         if min_travel_time == max_travel_time:
#             norm_tt = 0
#         else:
#             norm_tt = (info['label'][0] - min_travel_time)/(max_travel_time-min_travel_time)
#         if min_mon_cost == max_mon_cost:
#             norm_cost = 0
#         else:
#             norm_cost = (info['label'][1] - min_mon_cost)/(max_mon_cost-min_mon_cost)
#         if min_trips == max_trips:
#             norm_trip = 0
#         else:
#             norm_trip = (info['label'][2] - min_trips)/(max_trips-min_trips)
#         if min_walk_time == max_walk_time:
#             norm_wt = 0
#         else:
#             norm_wt = (info['label'][3] - min_walk_time)/(max_walk_time-min_walk_time)
#         norm_label = (norm_tt, norm_cost, norm_trip, norm_wt) #norm_wt
#         normParetoSet[OD].update({path_id: {'path': info['path'], 'label': norm_label}})


# with open('norm_Pareto_set_h-DMLC-U-UB-S0-10-0-300.pickle', 'wb') as handle:
#     pickle.dump(normParetoSet, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('norm_Pareto_set_h-DMLC-U-UB-S0-10-0-300.pickle', 'rb') as handle:
#     normParetoSet = pickle.load(handle)
    
# euclidean_distances = list()
# jaccard_distances = list()
# optimal_pareto_paths_percentages = list()

# for OD, attrs in normFullParetoSet.items():
#     eucl_dist_sum = 0
#     for path_id1, info1 in attrs.items():
#         eucl_dists = list()
#         for path_id2, info2 in normParetoSet[OD].items():
#             e_dist = math.sqrt(sum([(a - b) ** 2 for a, b in zip(info1['label'], info2['label'])]))
#             eucl_dists.append(e_dist)
#         min_e_dist = min(eucl_dists)
#         eucl_dist_sum += min_e_dist
#     euclidean_distance = eucl_dist_sum/len(normFullParetoSet[OD])
#     euclidean_distances.append(euclidean_distance)

# average_euclidean_distance = sum(euclidean_distances)/len(euclidean_distances)
# stdv_euclidean_distance = statistics.stdev(euclidean_distances)

# for OD, attrs in normFullParetoSet.items():
#     jacc_dist_sum = 0
#     for path_id1, info1 in attrs.items():
#         jacc_dists = list()
#         set1 = set(info1['path'])
#         for path_id2, info2 in normParetoSet[OD].items():
#             set2 = set(info2['path'])
#             j_dist = 1 - (len(set1.intersection(set2)) / len(set1.union(set2)))
#             jacc_dists.append(j_dist)
#         min_j_dist = min(jacc_dists)
#         jacc_dist_sum += min_j_dist
#     jaccard_distance = jacc_dist_sum/len(normFullParetoSet[OD])
#     jaccard_distances.append(jaccard_distance)

# average_jaccard_distance = sum(jaccard_distances)/len(jaccard_distances)
# stdv_jaccard_distance = statistics.stdev(jaccard_distances)

# for OD, attrs in normParetoSet.items():
#     opt_par_perc_sum = 0
#     for path_id1, info1 in attrs.items():
#         for path_id2, info2 in normFullParetoSet[OD].items():
#             if info1['path'] == info2['path']:
#                 opt_par_perc_sum += 1
#                 break
#     optimal_pareto_paths_percentages.append((opt_par_perc_sum/len(normParetoSet[OD]))*100)
    

# average_optimal_pareto_paths_percentages = sum(optimal_pareto_paths_percentages)/len(optimal_pareto_paths_percentages)
# stdv_optimal_pareto_paths_percentages = statistics.stdev(optimal_pareto_paths_percentages)


# performance_metrics = {'Average_CPU': {'μ': average_CPU, 'σ': stdv_CPU}, \
#                         'Average_Pareto_set_size': {'μ': average_pareto_set_size, 'σ': stdv_pareto_set_size}, \
#                             'Average_Euclidean_distance': {'μ': average_euclidean_distance, 'σ': stdv_euclidean_distance}, \
#                                 'Average_Jaccard_Distance': {'μ': average_jaccard_distance, 'σ': stdv_jaccard_distance}, \
#                                     'Average_Optimal_Pareto_Path_%': {'μ': average_optimal_pareto_paths_percentages, 'σ': stdv_optimal_pareto_paths_percentages}, \
#                                         'Average_redundant_labels': {'μ': average_red_labels, 'σ': stdv_average_red_labels}}
        
# print(performance_metrics)

#------------ script for running and getting metrics for ratio-based heuristics ---------------------#

# Pareto_set = dict()
# CPU_list = list()
# Pareto_set_size = list()
# Redundant_label_num = list()
# time_horizons = list()

# for OD in OD_pairs:
#     print(OD)
#     Pareto_set.update({OD: dict()})
#     travel_times = list()
#     for path_id, attrs in fullParetoSet[OD].items():
#         travel_times.append(attrs['label'][0])
#     min_travel_time = min(travel_times)
#     # print(min_travel_time)
#     max_travel_time = max(travel_times)
#     # print(max_travel_time)
#     time_horizon = int(min_travel_time + (3*min_travel_time) - \
#                         max(0,min_travel_time + (3*min_travel_time)-max_travel_time))
#     # print(time_horizon)
#     time_horizons.append(time_horizon)

#     start = time.time()
#     pareto_set, redundant_label_num = get_slack_pareto_set_correcting(multimodal_graph, OD[0], OD[1], request_time_sec, \
#                                         request_time_sec, request_time_sec+time_horizon, dt, 0, 10, 0, 300)
#     end = time.time()
    
#     Pareto_set[OD] = pareto_set
#     CPU_list.append(end - start)
#     print(end-start)
#     Pareto_set_size.append(len(pareto_set))
#     Redundant_label_num.append(redundant_label_num)
#     # print(cpu_list)
#     # print(pareto_set_size)
#     # print(missed_path_percentages)
    
#     oops = False
#     for path_id1, attrs1 in pareto_set.items():
#         for path_id2, attrs2 in pareto_set.items():
#             if path_id1 == path_id2:
#                 continue
#             if attrs1['path'] == attrs2['path']:
#                 print('Duplicated paths')
#             if attrs1['label'] == attrs2['label']:
#                 continue
#             if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i>=j]) == len(attrs1['label']):
#                 oops = True
#                 print(attrs1['label'], attrs2['label'])
#                 break
#             if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i<=j]) == len(attrs1['label']):
#                 oops = True
#                 print(attrs1['label'], attrs2['label'])
#                 break         
#     if oops:
#         print('oops')
#     else:
#         print('good')

# average_CPU = sum(CPU_list)/len(CPU_list)
# stdv_CPU = statistics.stdev(CPU_list)

# average_pareto_set_size = sum(Pareto_set_size)/len(Pareto_set_size)
# stdv_pareto_set_size = statistics.stdev(Pareto_set_size)

# average_red_labels = sum(Redundant_label_num)/len(Redundant_label_num)
# stdv_average_red_labels = statistics.stdev(Redundant_label_num)
    
# with open('Pareto_set_h-DMLC-U-UB-C-R3-S0-10-0-300.pickle', 'wb') as handle:
#     pickle.dump(Pareto_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('Pareto_set_h-DMLC-U-UB-C-R3-S0-10-0-300.pickle', 'rb') as handle:
#     ParetoSet = pickle.load(handle)

# #---- normalize the labels of the Pareto Set ------------#
# normParetoSet = dict()
# for OD, attrs in ParetoSet.items():
#     normParetoSet.update({OD: dict()})
#     travel_times = list()
#     mon_costs = list()
#     trips = list()
#     walk_times = list()
#     for path_id, info in attrs.items():
#         travel_times.append(info['label'][0])
#         mon_costs.append(info['label'][1])
#         trips.append(info['label'][2])
#         walk_times.append(info['label'][3])
#     min_travel_time = min(travel_times)
#     max_travel_time = max(travel_times)
#     min_mon_cost = min(mon_costs)
#     max_mon_cost = max(mon_costs)
#     min_trips = min(trips)
#     max_trips = max(trips)
#     min_walk_time = min(walk_times)
#     max_walk_time = max(walk_times)
    
#     for path_id, info in attrs.items():
#         if min_travel_time == max_travel_time:
#             norm_tt = 0
#         else:
#             norm_tt = (info['label'][0] - min_travel_time)/(max_travel_time-min_travel_time)
#         if min_mon_cost == max_mon_cost:
#             norm_cost = 0
#         else:
#             norm_cost = (info['label'][1] - min_mon_cost)/(max_mon_cost-min_mon_cost)
#         if min_trips == max_trips:
#             norm_trip = 0
#         else:
#             norm_trip = (info['label'][2] - min_trips)/(max_trips-min_trips)
#         if min_walk_time == max_walk_time:
#             norm_wt = 0
#         else:
#             norm_wt = (info['label'][3] - min_walk_time)/(max_walk_time-min_walk_time)
#         norm_label = (norm_tt, norm_cost, norm_trip, norm_wt)
#         normParetoSet[OD].update({path_id: {'path': info['path'], 'label': norm_label}})


# with open('norm_Pareto_set_h-DMLC-U-UB-C-R3-S0-10-0-300.pickle', 'wb') as handle:
#     pickle.dump(normParetoSet, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('norm_Pareto_set_h-DMLC-U-UB-C-R3-S0-10-0-300.pickle', 'rb') as handle:
#     normParetoSet = pickle.load(handle)
    
# euclidean_distances = list()
# jaccard_distances = list()
# optimal_pareto_paths_percentages = list()

# for OD, attrs in normFullParetoSet.items():
#     eucl_dist_sum = 0
#     for path_id1, info1 in attrs.items():
#         eucl_dists = list()
#         for path_id2, info2 in normParetoSet[OD].items():
#             e_dist = math.sqrt(sum([(a - b) ** 2 for a, b in zip(info1['label'], info2['label'])]))
#             eucl_dists.append(e_dist)
#         min_e_dist = min(eucl_dists)
#         eucl_dist_sum += min_e_dist
#     euclidean_distance = eucl_dist_sum/len(normFullParetoSet[OD])
#     euclidean_distances.append(euclidean_distance)

# average_euclidean_distance = sum(euclidean_distances)/len(euclidean_distances)
# stdv_euclidean_distance = statistics.stdev(euclidean_distances)

# for OD, attrs in normFullParetoSet.items():
#     jacc_dist_sum = 0
#     for path_id1, info1 in attrs.items():
#         jacc_dists = list()
#         set1 = set(info1['path'])
#         for path_id2, info2 in normParetoSet[OD].items():
#             set2 = set(info2['path'])
#             j_dist = 1 - (len(set1.intersection(set2)) / len(set1.union(set2)))
#             jacc_dists.append(j_dist)
#         min_j_dist = min(jacc_dists)
#         jacc_dist_sum += min_j_dist
#     jaccard_distance = jacc_dist_sum/len(normFullParetoSet[OD])
#     jaccard_distances.append(jaccard_distance)

# average_jaccard_distance = sum(jaccard_distances)/len(jaccard_distances)
# stdv_jaccard_distance = statistics.stdev(jaccard_distances)

# for OD, attrs in normParetoSet.items():
#     opt_par_perc_sum = 0
#     for path_id1, info1 in attrs.items():
#         for path_id2, info2 in normFullParetoSet[OD].items():
#             if info1['path'] == info2['path']:
#                 opt_par_perc_sum += 1
#                 break
#     optimal_pareto_paths_percentages.append((opt_par_perc_sum/len(normParetoSet[OD]))*100)
    

# average_optimal_pareto_paths_percentages = sum(optimal_pareto_paths_percentages)/len(optimal_pareto_paths_percentages)
# stdv_optimal_pareto_paths_percentages = statistics.stdev(optimal_pareto_paths_percentages)


# performance_metrics = {'Average_CPU': {'μ': average_CPU, 'σ': stdv_CPU}, \
#                         'Average_Pareto_set_size': {'μ': average_pareto_set_size, 'σ': stdv_pareto_set_size}, \
#                             'Average_Euclidean_distance': {'μ': average_euclidean_distance, 'σ': stdv_euclidean_distance}, \
#                                 'Average_Jaccard_Distance': {'μ': average_jaccard_distance, 'σ': stdv_jaccard_distance}, \
#                                     'Average_Optimal_Pareto_Path_%': {'μ': average_optimal_pareto_paths_percentages, 'σ': stdv_optimal_pareto_paths_percentages}, \
#                                         'Average_redundant_labels': {'μ': average_red_labels, 'σ': stdv_average_red_labels}}
        
# print(performance_metrics)



# ---- plots for depdence of time between ODs, Pareto set size and runtimes
# with open('Pareto_set_h-DMLS-U.pickle', 'rb') as handle:
#     fullParetoSet = pickle.load(handle)

# time_horizons = list()

# for OD in OD_pairs:
#     travel_times = list()
#     for path_id, attrs in fullParetoSet[OD].items():
#         travel_times.append(attrs['label'][0])
#     min_travel_time = min(travel_times)
#     # print(min_travel_time)
#     max_travel_time = max(travel_times)
#     # print(max_travel_time)
#     time_horizon = int(min_travel_time + (3*min_travel_time) - \
#                         max(0,min_travel_time + (3*min_travel_time)-max_travel_time))
#     # print(time_horizon)
#     time_horizons.append(time_horizon)
# print(CPU_list)
# print(time_horizons)
# print(len(time_horizons))
# print(len(CPU_list))
# print(Pareto_set_size)
# fields1 = ['timeHorizon', 'runTime']
# rows1 = []
# for i in range(0,len(time_horizons)):
#     rows1.append([time_horizons[i],CPU_list[i]])
# # print(my_list1)
    
# # name of csv file  
# filename = "TR-C_revised_timeHorizon_runTime.csv"
    
# # writing to csv file  
# with open(filename, 'w', newline='') as csvfile:  
#     # creating a csv writer object  
#     csvwriter = csv.writer(csvfile)  
        
#     # writing the fields  
#     csvwriter.writerow(fields1)  
        
#     # writing the data rows  
#     csvwriter.writerows(rows1) 



# with open('Pareto_set_h-DMLC-U.pickle', 'rb') as handle:
#     test_set = pickle.load(handle)

# Pareto_set_size = list()
# for OD in test_set:
#     Pareto_set_size.append(len(test_set[OD]))
    
# time_horizons = list()
# for OD in OD_pairs:
#     time_horizon = int(walk_times_per_OD[OD])
#     time_horizons.append(time_horizon)

# fields2 = ['timeHorizon', 'paretoSetSize']

# rows2 = []
# for i in range(0,len(time_horizons)):
#     rows2.append([time_horizons[i],Pareto_set_size[i]])

# # name of csv file  
# filename = "TR-C_revised_timeHorizon_setSize.csv"
    
# # writing to csv file  
# with open(filename, 'w', newline='') as csvfile:  
#     # creating a csv writer object  
#     csvwriter = csv.writer(csvfile)  
        
#     # writing the fields  
#     csvwriter.writerow(fields2)  
        
#     # writing the data rows  
#     csvwriter.writerows(rows2)



