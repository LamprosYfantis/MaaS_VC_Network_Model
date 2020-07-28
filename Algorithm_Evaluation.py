# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 14:16:21 2020

@author: Lampros Yfantis
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

from itertools import permutations 
from networkx.algorithms.simple_paths import get_full_pareto_set, get_ε_pareto_set, \
    get_bucket_pareto_set, get_ε_ratio_pareto_set, get_ratio_bucket_pareto_set, \
        get_shortest_weighted_path

#------------------ reading the pre-generated virtual city graph from a pickle file ----------#
# start = time.time()
multimodal_graph = nx.read_gpickle("VC_multimodal_graph_discr30sec")
# end = time.time()
# print(multimodal_graph.number_of_nodes())
# print(multimodal_graph.number_of_edges())
# print('Multimodal Network formulation running time is {}sec'.format(end - start))
# # print(multimodal_graph.nodes(data=True))
# print(multimodal_graph.number_of_nodes())
# print(multimodal_graph.number_of_edges())

#------------------ reading the pre-generated walk graph from a pickle file -------#
# start = time.time()
walk_graph = nx.read_gpickle("VC_walk_graph_discr30sec")
# end = time.time()
# print(walk_graph.number_of_nodes())
# print(walk_graph.number_of_edges())
# print('Walking Network formulation running time is {}sec'.format(end - start))

#------ walk graph plot ----------#
# pos = nx.get_node_attributes(walk_graph, 'pos')
# nx.draw_networkx(walk_graph, pos, node_size=100, font_size=8)  # Graph with node attributes
# # nx.draw(walk_graph, pos)
# plt.show()

#----- gneration of a sample of ODs ---------------------#
walk_attrs_weights = [1, 1, 0, 0, 0]  # weight of ttravel time, waiting time, distance, cost and transfers
bus_attrs_weights = [1, 1, 0, 0, 0]
train_attrs_weights = [1, 1, 0, 0, 0]
taxi_attrs_weights = [1, 1, 0, 0, 0]
sms_attrs_weights = [1, 1, 0, 0, 0]
sms_pool_attrs_weights = [1, 1, 0, 0, 0] 
cs_attrs_weights = [1, 1, 0, 0, 0]
mode_transfer_weight = 0   # mt
request_time_sec = 65400
dt = 30

walk_nodes_list = list()
for node in walk_graph.nodes():
    walk_nodes_list.append(node)

perm=permutations(walk_nodes_list,2)   
perm=list(perm)
walk_times_per_OD = dict()

#------ calculation of the walking times for each OD in the VC; Dijkstra algorithm could also be used----#
for OD in perm:
    # start = time.time()
    walk_path_data = get_shortest_weighted_path(walk_graph, OD[0], OD[1], request_time_sec, request_time_sec, \
                                            request_time_sec+30000, dt, walk_attrs_weights = walk_attrs_weights, \
                                                bus_attrs_weights = bus_attrs_weights, \
                                                    train_attrs_weights = train_attrs_weights, \
                                                        taxi_attrs_weights = taxi_attrs_weights, \
                                                            sms_attrs_weights = sms_attrs_weights, \
                                                                sms_pool_attrs_weights = sms_pool_attrs_weights, \
                                                                    cs_attrs_weights = cs_attrs_weights, \
                                                                      mode_transfer_weight = mode_transfer_weight)
    # end = time.time()
    # print(end-start)
    walk_times_per_OD.update({OD: walk_path_data['info']['weight']})
#     # dist = math.sqrt(sum([(a - b) ** 2 for a, b in zip(walk_graph.nodes[OD[0]]['pos'], walk_graph.nodes[OD[1]]['pos'])]))

#------ optional: dumping the OD walk times data structure at a pickle file-----#
with open('VC_all_OD_walk_times_30sec.pickle', 'wb') as handle:
    pickle.dump(walk_times_per_OD, handle, protocol=pickle.HIGHEST_PROTOCOL)

#----- optional: reading the file and store the data in the dictionary
with open('VC_all_OD_walk_times_30sec.pickle', 'rb') as handle:
    walk_times_per_OD = pickle.load(handle)

# ODs_per_walk_time_interval = {(0,3199): list(), (3200, 6399): list(), (6400, 9599):list(), \
#                               (9600, 12799): list(), (12800, 16000):list()}
# time_interval_list = list(ODs_per_walk_time_interval.keys())
# print(time_interval_list)

# for od in walk_times_per_OD:
#     tr_t = walk_times_per_OD[od]
#     index = int(tr_t/3200)
#     key = time_interval_list[index]
#     ODs_per_walk_time_interval[key].append(od)

# for interval in ODs_per_walk_time_interval:
#     od_list = ODs_per_walk_time_interval[interval]
#     for i in range(20):
#         od_choice = random.choice(od_list)
#         od_list.remove(od_choice)
#         # if od_choice in OD_pairs:
#         #     new_od_list = od_list
#         #     new_od_list.remove(od_choice)
#         #     od_choice = random.choice(new_od_list)
#         OD_pairs.append(od_choice)
#         print(walk_times_per_OD[od_choice])
# print(len(OD_pairs))
# print(OD_pairs)


OD_pairs = list()
od_list = list(walk_times_per_OD.keys())
while len(OD_pairs) <= 100:
    od_choice = random.choice(od_list)
    orig_to_w37 = math.sqrt(sum([(a - b) ** 2 for a, b in zip(walk_graph.nodes['w37']['pos'], walk_graph.nodes[od_choice[0]]['pos'])]))
    dest_to_w37 = math.sqrt(sum([(a - b) ** 2 for a, b in zip(walk_graph.nodes['w37']['pos'], walk_graph.nodes[od_choice[1]]['pos'])]))
    if od_choice not in OD_pairs and orig_to_w37<=5300 and dest_to_w37<=5300 \
        and (od_choice[1],od_choice[0]) not in OD_pairs and walk_times_per_OD[od_choice] >=1800:
            OD_pairs.append(od_choice)

#------ the sample for the publication ----#
OD_pairs = [('w55', 'w101'), ('w71', 'w17'), ('w36', 'w42'), ('w69', 'w20'), ('w50', 'w8'), ('w15', 'w14'), ('w15', 'w42'), ('w41', 'w80'), ('w62', 'w38'), ('w59', 'w60'), ('w61', 'w56'), ('w23', 'w45'), ('w20', 'w48'), ('w28', 'w67'), ('w63', 'w40'), ('w29', 'w41'), ('w40', 'w60'), ('w10', 'w22'), ('w19', 'w62'), ('w43', 'w17'), ('w51', 'w33'), ('w18', 'w67'), ('w69', 'w67'), ('w15', 'w101'), ('w35', 'w44'), ('w32', 'w15'), ('w27', 'w61'), ('w39', 'w51'), ('w65', 'w41'), ('w32', 'w65'), ('w49', 'w36'), ('w20', 'w6'), ('w9', 'w13'), ('w67', 'w8'), ('w22', 'w35'), ('w33', 'w9'), ('w29', 'w58'), ('w23', 'w33'), ('w72', 'w57'), ('w22', 'w101'), ('w19', 'w49'), ('w18', 'w100'), ('w63', 'w35'), ('w80,1', 'w24'), ('w9', 'w37'), ('w72', 'w53'), ('w47', 'w20'), ('w49', 'w64'), ('w80,1', 'w50'), ('w100', 'w36'), ('w50', 'w101'), ('w22', 'w31'), ('w57', 'w61'), ('w19', 'w9'), ('w21', 'w39'), ('w80,1', 'w23'), ('w61', 'w33'), ('w31', 'w72'), ('w51', 'w31'), ('w30', 'w9'), ('w5', 'w8'), ('w11', 'w43'), ('w51', 'w28'), ('w52', 'w61'), ('w15', 'w22'), ('w21', 'w51'), ('w24', 'w69'), ('w44', 'w25'), ('w24', 'w9'), ('w36', 'w47'), ('w18', 'w15'), ('w65', 'w34'), ('w33', 'w80'), ('w42', 'w18'), ('w49', 'w12'), ('w34', 'w58'), ('w52', 'w18'), ('w100', 'w15'), ('w28', 'w58'), ('w8', 'w69'), ('w71', 'w48'), ('w60', 'w65'), ('w29', 'w28'), ('w31', 'w105'), ('w105', 'w42'), ('w55', 'w72'), ('w102', 'w14'), ('w51', 'w80,1'), ('w11', 'w36'), ('w56', 'w67'), ('w65', 'w39'), ('w20', 'w37'), ('w57', 'w66'), ('w51', 'w65'), ('w8', 'w40'), ('w21', 'w31'), ('w105', 'w11'), ('w11', 'w33'), ('w69', 'w28'), ('w14', 'w18'), ('w64', 'w37')]
#--- the time inteval
dt = 30
#---- the query request time - pm peak hour
request_time_sec = 65400

full_Pareto_set = dict()
# # with open('full_Pareto_set.pickle', 'rb') as handle:
# #     full_Pareto_set = pickle.load(handle)
cpu_list = list()
# # with open('cpuList.pickle', 'rb') as handle:
# #     cpu_list = pickle.load(handle)
pareto_set_size = list()
# # with open('paretoSetSize.pickle', 'rb') as handle:
# #     pareto_set_size = pickle.load(handle)
missed_path_percentages = list()
# # with open('missedPaths.pickle', 'rb') as handle:
# #     missed_path_percentages = pickle.load(handle)
time_horizons = list()
# # with open('timeHorizons.pickle', 'rb') as handle:
# #     time_horizons = pickle.load(handle)

for OD in OD_pairs:
    full_Pareto_set.update({OD: dict()})
    time_horizon = int(walk_times_per_OD[OD])
    time_horizons.append(time_horizon)
    # print(time_horizon)

    start = time.time()
    pareto_set, missed_paths_num = get_full_pareto_set(multimodal_graph, OD[0], OD[1], request_time_sec, \
                                        request_time_sec, request_time_sec+time_horizon, dt)
    end = time.time()
    
    full_Pareto_set[OD] = pareto_set
    cpu_list.append(end - start)
    pareto_set_size.append(len(pareto_set))
    missed_path_percentages.append((missed_paths_num/(len(pareto_set)+missed_paths_num))*100)
    # print(cpu_list)
    # print(pareto_set_size)
    # print(missed_path_percentages)
    
    # oops = False
    # for path_id1, attrs1 in pareto_set.items():
    #     for path_id2, attrs2 in pareto_set.items():
    #         if path_id1 == path_id2:
    #             continue
    #         if attrs1['path'] == attrs2['path']:
    #             print('Duplicated paths')
    #         if attrs1['label'] == attrs2['label']:
    #             continue
    #         if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i>=j]) == len(attrs1['label']):
    #             oops = True
    #             print(attrs1['label'], attrs2['label'])
    #             break
    #         if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i<=j]) == len(attrs1['label']):
    #             oops = True
    #             print(attrs1['label'], attrs2['label'])
    #             break         
    # if oops:
    #     print('oops')
    # else:
    #     print('good')
            
# with open('cpuList.pickle', 'wb') as handle:
#     pickle.dump(cpu_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
# with open('paretoSetSize.pickle', 'wb') as handle:
#     pickle.dump(pareto_set_size, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
# with open('missedPaths.pickle', 'wb') as handle:
#     pickle.dump(missed_path_percentages, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('timeHorizons.pickle', 'wb') as handle:
#     pickle.dump(time_horizons, handle, protocol=pickle.HIGHEST_PROTOCOL)

average_CPU = sum(cpu_list)/len(cpu_list)
stdv_CPU = statistics.stdev(cpu_list)

average_pareto_set_size = sum(pareto_set_size)/len(pareto_set_size)
stdv_pareto_set_size = statistics.stdev(pareto_set_size)

average_missed_path_percentages = sum(missed_path_percentages)/len(missed_path_percentages)
stdv_missed_path_percentages = statistics.stdev(missed_path_percentages)

average_time_horizons = sum(time_horizons)/len(time_horizons)
stdv_time_horizons = statistics.stdev(time_horizons)

performance_metrics = {'CPU': {'μ': average_CPU, 'σ': stdv_CPU}, \
                        'Pareto_set_size': {'μ': average_pareto_set_size, 'σ': stdv_pareto_set_size}, \
                        'missed_paths_%': {'μ': average_missed_path_percentages, 'σ': stdv_missed_path_percentages}, \
                            'average_time_horizons':  {'μ': average_time_horizons, 'σ': stdv_time_horizons}}
print(performance_metrics)

# with open('full_Pareto_set.pickle', 'wb') as handle:
#     pickle.dump(full_Pareto_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('full_Pareto_set.pickle', 'rb') as handle:
    fullParetoSet = pickle.load(handle)

# # #---- normalize the labels of the full Pareto Set ------------#
normFullParetoSet = dict()
for OD, attrs in fullParetoSet.items():
    normFullParetoSet.update({OD: dict()})
    travel_times = list()
    mon_costs = list()
    trips = list()
    for path_id, info in attrs.items():
        travel_times.append(info['label'][0])
        mon_costs.append(info['label'][1])
        trips.append(info['label'][2])
    min_travel_time = min(travel_times)
    max_travel_time = max(travel_times)
    min_mon_cost = min(mon_costs)
    max_mon_cost = max(mon_costs)
    min_trips = min(trips)
    max_trips = max(trips)
    
    for path_id, info in attrs.items():
        if min_travel_time == max_travel_time:
            norm_tt = 0
        else:
            norm_tt = (info['label'][0] - min_travel_time)/(max_travel_time-min_travel_time)
        if min_mon_cost == max_mon_cost:
            norm_cost = 0
        else:
            norm_cost = (info['label'][1] - min_mon_cost)/(max_mon_cost-min_mon_cost)
        if min_trips == max_trips:
            norm_trip = 0
        else:
            norm_trip = (info['label'][2] - min_trips)/(max_trips-min_trips)
        norm_label = (norm_tt, norm_cost, norm_trip)
        normFullParetoSet[OD].update({path_id: {'path': info['path'], 'label': norm_label}})

with open('norm_full_Pareto_set.pickle', 'wb') as handle:
    pickle.dump(normFullParetoSet, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('norm_full_Pareto_set.pickle', 'rb') as handle:
    normFullParetoSet = pickle.load(handle)

#------------ computation of ratio-based heuristic Pareto sets and evaluation metrics for a sample of random OD requests ---------------------#
heuristic_Pareto_set = dict()
cpu_list = list()
pareto_set_size = list()
missed_path_percentages = list()
time_horizons = list()

for OD in OD_pairs:
    heuristic_Pareto_set.update({OD: dict()})
    travel_times = list()
    for path_id, attrs in fullParetoSet[OD].items():
        travel_times.append(attrs['label'][0])
    min_travel_time = min(travel_times)
    # print(min_travel_time)
    max_travel_time = max(travel_times)
    # print(max_travel_time)
    time_horizon = int(min_travel_time + (4*min_travel_time) - \
                       max(0,min_travel_time + (4*min_travel_time)-max_travel_time))
    time_horizons.append(time_horizon)
    # print(time_horizon)

    start = time.time()
    pareto_set, missed_paths_num = get_full_pareto_set(multimodal_graph, OD[0], OD[1], request_time_sec, \
                                        request_time_sec, request_time_sec+time_horizon, dt)
    end = time.time()
    
    heuristic_Pareto_set[OD] = pareto_set
    cpu_list.append(end - start)
    pareto_set_size.append(len(pareto_set))
    missed_path_percentages.append((missed_paths_num/(len(pareto_set)+missed_paths_num))*100)
    # print(cpu_list)
    # print(pareto_set_size)
    # print(missed_path_percentages)
    
    # oops = False
    # for path_id1, attrs1 in pareto_set.items():
    #     for path_id2, attrs2 in pareto_set.items():
    #         if path_id1 == path_id2:
    #             continue
    #         if attrs1['path'] == attrs2['path']:
    #             print('Duplicated paths')
    #         if attrs1['label'] == attrs2['label']:
    #             continue
    #         if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i>=j]) == len(attrs1['label']):
    #             oops = True
    #             print(attrs1['label'], attrs2['label'])
    #             break
    #         if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i<=j]) == len(attrs1['label']):
    #             oops = True
    #             print(attrs1['label'], attrs2['label'])
    #             break         
    # if oops:
    #     print('oops')
    # else:
    #     print('good')

average_CPU = sum(cpu_list)/len(cpu_list)
stdv_CPU = statistics.stdev(cpu_list)

average_pareto_set_size = sum(pareto_set_size)/len(pareto_set_size)
stdv_pareto_set_size = statistics.stdev(pareto_set_size)

average_missed_path_percentages = sum(missed_path_percentages)/len(missed_path_percentages)
stdv_missed_path_percentages = statistics.stdev(missed_path_percentages)

average_time_horizons = sum(time_horizons)/len(time_horizons)
stdv_time_horizons = statistics.stdev(time_horizons)


with open('ratio_based_heuristic_Pareto_set_4.pickle', 'wb') as handle:
    pickle.dump(heuristic_Pareto_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('ratio_based_heuristic_Pareto_set_4.pickle', 'rb') as handle:
    heurParetoSet = pickle.load(handle)

#---- normalize the labels of the heuristic Pareto Set ------------#
normHeurParetoSet = dict()
for OD, attrs in heurParetoSet.items():
    normHeurParetoSet.update({OD: dict()})
    travel_times = list()
    mon_costs = list()
    trips = list()
    for path_id, info in attrs.items():
        travel_times.append(info['label'][0])
        mon_costs.append(info['label'][1])
        trips.append(info['label'][2])
    min_travel_time = min(travel_times)
    max_travel_time = max(travel_times)
    min_mon_cost = min(mon_costs)
    max_mon_cost = max(mon_costs)
    min_trips = min(trips)
    max_trips = max(trips)
    
    for path_id, info in attrs.items():
        if min_travel_time == max_travel_time:
            norm_tt = 0
        else:
            norm_tt = (info['label'][0] - min_travel_time)/(max_travel_time-min_travel_time)
        if min_mon_cost == max_mon_cost:
            norm_cost = 0
        else:
            norm_cost = (info['label'][1] - min_mon_cost)/(max_mon_cost-min_mon_cost)
        if min_trips == max_trips:
            norm_trip = 0
        else:
            norm_trip = (info['label'][2] - min_trips)/(max_trips-min_trips)
        norm_label = (norm_tt, norm_cost, norm_trip)
        normHeurParetoSet[OD].update({path_id: {'path': info['path'], 'label': norm_label}})

# print(normHeurParetoSet)
# print(heurParetoSet)
with open('norm_ratio_based_heuristic_Pareto_set_4.pickle', 'wb') as handle:
    pickle.dump(normHeurParetoSet, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('norm_ratio_based_heuristic_Pareto_set_4.pickle', 'rb') as handle:
    normHeurParetoSet = pickle.load(handle)

euclidean_distances = list()
jaccard_distances = list()
optimal_pareto_paths_percentages = list()

for OD, attrs in normFullParetoSet.items():
    eucl_dist_sum = 0
    for path_id1, info1 in attrs.items():
        eucl_dists = list()
        for path_id2, info2 in normHeurParetoSet[OD].items():
            e_dist = math.sqrt(sum([(a - b) ** 2 for a, b in zip(info1['label'], info2['label'])]))
            eucl_dists.append(e_dist)
        min_e_dist = min(eucl_dists)
        eucl_dist_sum += min_e_dist
    euclidean_distance = eucl_dist_sum/len(normFullParetoSet[OD])
    euclidean_distances.append(euclidean_distance)

average_euclidean_distance = sum(euclidean_distances)/len(euclidean_distances)
stdv_euclidean_distance = statistics.stdev(euclidean_distances)

for OD, attrs in normFullParetoSet.items():
    jacc_dist_sum = 0
    for path_id1, info1 in attrs.items():
        jacc_dists = list()
        set1 = set(info1['path'])
        for path_id2, info2 in normHeurParetoSet[OD].items():
            set2 = set(info2['path'])
            j_dist = 1 - (len(set1.intersection(set2)) / len(set1.union(set2)))
            jacc_dists.append(j_dist)
        min_j_dist = min(jacc_dists)
        jacc_dist_sum += min_j_dist
    jaccard_distance = jacc_dist_sum/len(normFullParetoSet[OD])
    jaccard_distances.append(jaccard_distance)

average_jaccard_distance = sum(jaccard_distances)/len(jaccard_distances)
stdv_jaccard_distance = statistics.stdev(jaccard_distances)

for OD, attrs in normHeurParetoSet.items():
    opt_par_perc_sum = 0
    for path_id1, info1 in attrs.items():
        for path_id2, info2 in normFullParetoSet[OD].items():
            if info1['path'] == info2['path']:
                opt_par_perc_sum += 1
                break
    optimal_pareto_paths_percentages.append((opt_par_perc_sum/len(normHeurParetoSet[OD]))*100)
    

average_optimal_pareto_paths_percentages = sum(optimal_pareto_paths_percentages)/len(optimal_pareto_paths_percentages)
stdv_optimal_pareto_paths_percentages = statistics.stdev(optimal_pareto_paths_percentages)

performance_metrics = {'Average_CPU': {'μ': average_CPU, 'σ': stdv_CPU}, \
                        'Average_Pareto_set_size': {'μ': average_pareto_set_size, 'σ': stdv_pareto_set_size}, \
                            'Average_Euclidean_distance': {'μ': average_euclidean_distance, 'σ': stdv_euclidean_distance}, \
                                'Average_Jaccard_Distance': {'μ': average_jaccard_distance, 'σ': stdv_jaccard_distance}, \
                                    'Average_Optimal_Pareto_Path_%': {'μ': average_optimal_pareto_paths_percentages, 'σ': stdv_optimal_pareto_paths_percentages}, \
                                        'Average_missed_paths_%': {'μ': average_missed_path_percentages, 'σ': stdv_missed_path_percentages}, \
                                            'Average_time_horizons':  {'μ': average_time_horizons, 'σ': stdv_time_horizons}}
        
print(performance_metrics)      


#------------ computation of ε-Pareto sets and evaluation metrics for a sample of random OD requests ---------------------#
heuristic_Pareto_set = dict()
cpu_list = list()
pareto_set_size = list()
missed_path_percentages = list()
time_horizons = list()
euclidean_distances = list()
jaccard_distances = list()
optimal_pareto_paths_percentages = list()

for OD in OD_pairs:
    heuristic_Pareto_set.update({OD: dict()})
    time_horizon = int(walk_times_per_OD[OD])
    time_horizons.append(time_horizon)
    # print(time_horizon)

    start = time.time()
    pareto_set, missed_paths_num = get_ε_pareto_set(multimodal_graph, OD[0], OD[1], request_time_sec, \
                                       request_time_sec, request_time_sec+time_horizon, dt, 1.2)
    end = time.time()
    
    heuristic_Pareto_set[OD] = pareto_set
    cpu_list.append(end - start)
    pareto_set_size.append(len(pareto_set))
    missed_path_percentages.append((missed_paths_num/(len(pareto_set)+missed_paths_num))*100)
    # print(cpu_list)
    # print(pareto_set_size)
    # print(missed_path_percentages)
    
    # oops = False
    # for path_id1, attrs1 in pareto_set.items():
    #     for path_id2, attrs2 in pareto_set.items():
    #         if path_id1 == path_id2:
    #             continue
    #         if attrs1['path'] == attrs2['path']:
    #             print('Duplicated paths')
    #         if attrs1['label'] == attrs2['label']:
    #             continue
    #         if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i>=j]) == len(attrs1['label']):
    #             oops = True
    #             print(attrs1['label'], attrs2['label'])
    #             break
    #         if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i<=j]) == len(attrs1['label']):
    #             oops = True
    #             print(attrs1['label'], attrs2['label'])
    #             break         
    # if oops:
    #     print('oops')
    # else:
    #     print('good')

average_CPU = sum(cpu_list)/len(cpu_list)
stdv_CPU = statistics.stdev(cpu_list)

average_pareto_set_size = sum(pareto_set_size)/len(pareto_set_size)
stdv_pareto_set_size = statistics.stdev(pareto_set_size)

average_missed_path_percentages = sum(missed_path_percentages)/len(missed_path_percentages)
stdv_missed_path_percentages = statistics.stdev(missed_path_percentages)

average_time_horizons = sum(time_horizons)/len(time_horizons)
stdv_time_horizons = statistics.stdev(time_horizons)
    
with open('ε_heuristic_Pareto_set_1.05.pickle', 'wb') as handle:
    pickle.dump(heuristic_Pareto_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('ε_heuristic_Pareto_set_1.05.pickle', 'rb') as handle:
    heurParetoSet = pickle.load(handle)

#---- normalize the labels of the heuristic Pareto Set ------------#
normHeurParetoSet = dict()
for OD, attrs in heurParetoSet.items():
    normHeurParetoSet.update({OD: dict()})
    travel_times = list()
    mon_costs = list()
    trips = list()
    for path_id, info in attrs.items():
        travel_times.append(info['label'][0])
        mon_costs.append(info['label'][1])
        trips.append(info['label'][2])
    min_travel_time = min(travel_times)
    max_travel_time = max(travel_times)
    min_mon_cost = min(mon_costs)
    max_mon_cost = max(mon_costs)
    min_trips = min(trips)
    max_trips = max(trips)
    
    for path_id, info in attrs.items():
        if min_travel_time == max_travel_time:
            norm_tt = 0
        else:
            norm_tt = (info['label'][0] - min_travel_time)/(max_travel_time-min_travel_time)
        if min_mon_cost == max_mon_cost:
            norm_cost = 0
        else:
            norm_cost = (info['label'][1] - min_mon_cost)/(max_mon_cost-min_mon_cost)
        if min_trips == max_trips:
            norm_trip = 0
        else:
            norm_trip = (info['label'][2] - min_trips)/(max_trips-min_trips)
        norm_label = (norm_tt, norm_cost, norm_trip)
        normHeurParetoSet[OD].update({path_id: {'path': info['path'], 'label': norm_label}})
        # info['label'] = norm_label    

# print(normHeurParetoSet)
# print(heurParetoSet)
with open('norm_ε_heuristic_Pareto_set_1.05.pickle', 'wb') as handle:
    pickle.dump(normHeurParetoSet, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('norm_ε_heuristic_Pareto_set_1.05.pickle', 'rb') as handle:
    normHeurParetoSet = pickle.load(handle)

for OD, attrs in normFullParetoSet.items():
    eucl_dist_sum = 0
    for path_id1, info1 in attrs.items():
        eucl_dists = list()
        for path_id2, info2 in normHeurParetoSet[OD].items():
            e_dist = math.sqrt(sum([(a - b) ** 2 for a, b in zip(info1['label'], info2['label'])]))
            eucl_dists.append(e_dist)
        min_e_dist = min(eucl_dists)
        eucl_dist_sum += min_e_dist
    euclidean_distance = eucl_dist_sum/len(normFullParetoSet[OD])
    euclidean_distances.append(euclidean_distance)

average_euclidean_distance = sum(euclidean_distances)/len(euclidean_distances)
stdv_euclidean_distance = statistics.stdev(euclidean_distances)

for OD, attrs in normFullParetoSet.items():
    jacc_dist_sum = 0
    for path_id1, info1 in attrs.items():
        jacc_dists = list()
        set1 = set(info1['path'])
        for path_id2, info2 in normHeurParetoSet[OD].items():
            set2 = set(info2['path'])
            j_dist = 1 - (len(set1.intersection(set2)) / len(set1.union(set2)))
            jacc_dists.append(j_dist)
        min_j_dist = min(jacc_dists)
        jacc_dist_sum += min_j_dist
    jaccard_distance = jacc_dist_sum/len(normFullParetoSet[OD])
    jaccard_distances.append(jaccard_distance)

average_jaccard_distance = sum(jaccard_distances)/len(jaccard_distances)
stdv_jaccard_distance = statistics.stdev(jaccard_distances)

for OD, attrs in normHeurParetoSet.items():
    opt_par_perc_sum = 0
    for path_id1, info1 in attrs.items():
        for path_id2, info2 in normFullParetoSet[OD].items():
            if info1['path'] == info2['path']:
                opt_par_perc_sum += 1
                break
    optimal_pareto_paths_percentages.append((opt_par_perc_sum/len(normHeurParetoSet[OD]))*100)
    

average_optimal_pareto_paths_percentages = sum(optimal_pareto_paths_percentages)/len(optimal_pareto_paths_percentages)
stdv_optimal_pareto_paths_percentages = statistics.stdev(optimal_pareto_paths_percentages)

performance_metrics = {'Average_CPU': {'μ': average_CPU, 'σ': stdv_CPU}, \
                        'Average_Pareto_set_size': {'μ': average_pareto_set_size, 'σ': stdv_pareto_set_size}, \
                            'Average_Euclidean_distance': {'μ': average_euclidean_distance, 'σ': stdv_euclidean_distance}, \
                                'Average_Jaccard_Distance': {'μ': average_jaccard_distance, 'σ': stdv_jaccard_distance}, \
                                    'Average_Optimal_Pareto_Path_%': {'μ': average_optimal_pareto_paths_percentages, 'σ': stdv_optimal_pareto_paths_percentages}, \
                                        'Average_missed_paths_%': {'μ': average_missed_path_percentages, 'σ': stdv_missed_path_percentages}, \
                                            'Average_time_horizons':  {'μ': average_time_horizons, 'σ': stdv_time_horizons}}
        
print(performance_metrics)     

#------------ computation of Pareto sets with Buckets and evaluation metrics for a sample of random OD requests ---------------------#
heuristic_Pareto_set = dict()
cpu_list = list()
pareto_set_size = list()
missed_path_percentages = list()
time_horizons = list()
euclidean_distances = list()
jaccard_distances = list()
optimal_pareto_paths_percentages = list()
for OD in OD_pairs:
    heuristic_Pareto_set.update({OD: dict()})
    time_horizon = int(walk_times_per_OD[OD])
    time_horizons.append(time_horizon)
    # print(time_horizon)

    start = time.time()
    pareto_set, missed_paths_num = get_bucket_pareto_set(multimodal_graph, OD[0], OD[1], request_time_sec, \
                                       request_time_sec, request_time_sec+time_horizon, dt, 60, 5)
    end = time.time()
    
    heuristic_Pareto_set[OD] = pareto_set
    cpu_list.append(end - start)
    pareto_set_size.append(len(pareto_set))
    missed_path_percentages.append((missed_paths_num/(len(pareto_set)+missed_paths_num))*100)
    # print(cpu_list)
    # print(pareto_set_size)
    # print(missed_path_percentages)
    
    # oops = False
    # for path_id1, attrs1 in pareto_set.items():
    #     for path_id2, attrs2 in pareto_set.items():
    #         if path_id1 == path_id2:
    #             continue
    #         if attrs1['path'] == attrs2['path']:
    #             print('Duplicated paths')
    #         if attrs1['label'] == attrs2['label']:
    #             continue
    #         if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i>=j]) == len(attrs1['label']):
    #             oops = True
    #             print(attrs1['label'], attrs2['label'])
    #             break
    #         if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i<=j]) == len(attrs1['label']):
    #             oops = True
    #             print(attrs1['label'], attrs2['label'])
    #             break         
    # if oops:
    #     print('oops')
    # else:
    #     print('good')

average_CPU = sum(cpu_list)/len(cpu_list)
stdv_CPU = statistics.stdev(cpu_list)

average_pareto_set_size = sum(pareto_set_size)/len(pareto_set_size)
stdv_pareto_set_size = statistics.stdev(pareto_set_size)

average_missed_path_percentages = sum(missed_path_percentages)/len(missed_path_percentages)
stdv_missed_path_percentages = statistics.stdev(missed_path_percentages)

average_time_horizons = sum(time_horizons)/len(time_horizons)
stdv_time_horizons = statistics.stdev(time_horizons)
    
with open('bucket_heuristic_Pareto_set_60_5.pickle', 'wb') as handle:
    pickle.dump(heuristic_Pareto_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('bucket_heuristic_Pareto_set_60_5.pickle', 'rb') as handle:
    heurParetoSet = pickle.load(handle)

#---- normalize the labels of the heuristic Pareto Set ------------#
normHeurParetoSet = dict()
for OD, attrs in heurParetoSet.items():
    normHeurParetoSet.update({OD: dict()})
    travel_times = list()
    mon_costs = list()
    trips = list()
    for path_id, info in attrs.items():
        travel_times.append(info['label'][0])
        mon_costs.append(info['label'][1])
        trips.append(info['label'][2])
    min_travel_time = min(travel_times)
    max_travel_time = max(travel_times)
    min_mon_cost = min(mon_costs)
    max_mon_cost = max(mon_costs)
    min_trips = min(trips)
    max_trips = max(trips)
    
    for path_id, info in attrs.items():
        if min_travel_time == max_travel_time:
            norm_tt = 0
        else:
            norm_tt = (info['label'][0] - min_travel_time)/(max_travel_time-min_travel_time)
        if min_mon_cost == max_mon_cost:
            norm_cost = 0
        else:
            norm_cost = (info['label'][1] - min_mon_cost)/(max_mon_cost-min_mon_cost)
        if min_trips == max_trips:
            norm_trip = 0
        else:
            norm_trip = (info['label'][2] - min_trips)/(max_trips-min_trips)
        norm_label = (norm_tt, norm_cost, norm_trip)
        normHeurParetoSet[OD].update({path_id: {'path': info['path'], 'label': norm_label}})
        # info['label'] = norm_label    

# print(normHeurParetoSet)
# print(heurParetoSet)
with open('norm_bucket_heuristic_Pareto_set_60_5.pickle', 'wb') as handle:
    pickle.dump(normHeurParetoSet, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('norm_bucket_heuristic_Pareto_set_60_5.pickle', 'rb') as handle:
    normHeurParetoSet = pickle.load(handle)

for OD, attrs in normFullParetoSet.items():
    eucl_dist_sum = 0
    for path_id1, info1 in attrs.items():
        eucl_dists = list()
        for path_id2, info2 in normHeurParetoSet[OD].items():
            e_dist = math.sqrt(sum([(a - b) ** 2 for a, b in zip(info1['label'], info2['label'])]))
            eucl_dists.append(e_dist)
        min_e_dist = min(eucl_dists)
        eucl_dist_sum += min_e_dist
    euclidean_distance = eucl_dist_sum/len(normFullParetoSet[OD])
    euclidean_distances.append(euclidean_distance)

average_euclidean_distance = sum(euclidean_distances)/len(euclidean_distances)
stdv_euclidean_distance = statistics.stdev(euclidean_distances)

for OD, attrs in normFullParetoSet.items():
    jacc_dist_sum = 0
    for path_id1, info1 in attrs.items():
        jacc_dists = list()
        set1 = set(info1['path'])
        for path_id2, info2 in normHeurParetoSet[OD].items():
            set2 = set(info2['path'])
            j_dist = 1 - (len(set1.intersection(set2)) / len(set1.union(set2)))
            jacc_dists.append(j_dist)
        min_j_dist = min(jacc_dists)
        jacc_dist_sum += min_j_dist
    jaccard_distance = jacc_dist_sum/len(normFullParetoSet[OD])
    jaccard_distances.append(jaccard_distance)

average_jaccard_distance = sum(jaccard_distances)/len(jaccard_distances)
stdv_jaccard_distance = statistics.stdev(jaccard_distances)

for OD, attrs in normHeurParetoSet.items():
    opt_par_perc_sum = 0
    for path_id1, info1 in attrs.items():
        for path_id2, info2 in normFullParetoSet[OD].items():
            if info1['path'] == info2['path']:
                opt_par_perc_sum += 1
                break
    optimal_pareto_paths_percentages.append((opt_par_perc_sum/len(normHeurParetoSet[OD]))*100)
    

average_optimal_pareto_paths_percentages = sum(optimal_pareto_paths_percentages)/len(optimal_pareto_paths_percentages)
stdv_optimal_pareto_paths_percentages = statistics.stdev(optimal_pareto_paths_percentages)

performance_metrics = {'Average_CPU': {'μ': average_CPU, 'σ': stdv_CPU}, \
                        'Average_Pareto_set_size': {'μ': average_pareto_set_size, 'σ': stdv_pareto_set_size}, \
                            'Average_Euclidean_distance': {'μ': average_euclidean_distance, 'σ': stdv_euclidean_distance}, \
                                'Average_Jaccard_Distance': {'μ': average_jaccard_distance, 'σ': stdv_jaccard_distance}, \
                                    'Average_Optimal_Pareto_Path_%': {'μ': average_optimal_pareto_paths_percentages, 'σ': stdv_optimal_pareto_paths_percentages}, \
                                        'Average_missed_paths_%': {'μ': average_missed_path_percentages, 'σ': stdv_missed_path_percentages}, \
                                            'Average_time_horizons':  {'μ': average_time_horizons, 'σ': stdv_time_horizons}}
        
print(performance_metrics)     

#------------ computation of epsilon and ratio-based heuristic Pareto sets and evaluation metrics for a sample of random OD requests ---------------------#
heuristic_Pareto_set = dict()
cpu_list = list()
pareto_set_size = list()
missed_path_percentages = list()
time_horizons = list()
euclidean_distances = list()
jaccard_distances = list()
optimal_pareto_paths_percentages = list()

for OD in OD_pairs:
    heuristic_Pareto_set.update({OD: dict()})
    travel_times = list()
    for path_id, attrs in fullParetoSet[OD].items():
        travel_times.append(attrs['label'][0])
    min_travel_time = min(travel_times)
    # print(min_travel_time)
    max_travel_time = max(travel_times)
    # print(max_travel_time)
    time_horizon = int(min_travel_time + (3*min_travel_time) - \
                       max(0,min_travel_time + (3*min_travel_time)-max_travel_time))
    # print(time_horizon)
    time_horizons.append(time_horizon)

    start = time.time()
    pareto_set, missed_paths_num = get_ε_ratio_pareto_set(multimodal_graph, OD[0], OD[1], request_time_sec, \
                                        request_time_sec, request_time_sec+time_horizon, dt, 1.05)
    end = time.time()
    
    heuristic_Pareto_set[OD] = pareto_set
    cpu_list.append(end - start)
    pareto_set_size.append(len(pareto_set))
    missed_path_percentages.append((missed_paths_num/(len(pareto_set)+missed_paths_num))*100)
    # print(cpu_list)
    # print(pareto_set_size)
    # print(missed_path_percentages)
    
    # oops = False
    # for path_id1, attrs1 in pareto_set.items():
    #     for path_id2, attrs2 in pareto_set.items():
    #         if path_id1 == path_id2:
    #             continue
    #         if attrs1['path'] == attrs2['path']:
    #             print('Duplicated paths')
    #         if attrs1['label'] == attrs2['label']:
    #             continue
    #         if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i>=j]) == len(attrs1['label']):
    #             oops = True
    #             print(attrs1['label'], attrs2['label'])
    #             break
    #         if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i<=j]) == len(attrs1['label']):
    #             oops = True
    #             print(attrs1['label'], attrs2['label'])
    #             break         
    # if oops:
    #     print('oops')
    # else:
    #     print('good')

average_CPU = sum(cpu_list)/len(cpu_list)
stdv_CPU = statistics.stdev(cpu_list)

average_pareto_set_size = sum(pareto_set_size)/len(pareto_set_size)
stdv_pareto_set_size = statistics.stdev(pareto_set_size)

average_missed_path_percentages = sum(missed_path_percentages)/len(missed_path_percentages)
stdv_missed_path_percentages = statistics.stdev(missed_path_percentages)

average_time_horizons = sum(time_horizons)/len(time_horizons)
stdv_time_horizons = statistics.stdev(time_horizons)


with open('ε_ratio_based_heuristic_Pareto_set_1.05_3.pickle', 'wb') as handle:
    pickle.dump(heuristic_Pareto_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('ε_ratio_based_heuristic_Pareto_set_1.05_3.pickle', 'rb') as handle:
    heurParetoSet = pickle.load(handle)

#---- normalize the labels of the heuristic Pareto Set ------------#
normHeurParetoSet = dict()
for OD, attrs in heurParetoSet.items():
    normHeurParetoSet.update({OD: dict()})
    travel_times = list()
    mon_costs = list()
    trips = list()
    for path_id, info in attrs.items():
        travel_times.append(info['label'][0])
        mon_costs.append(info['label'][1])
        trips.append(info['label'][2])
    min_travel_time = min(travel_times)
    max_travel_time = max(travel_times)
    min_mon_cost = min(mon_costs)
    max_mon_cost = max(mon_costs)
    min_trips = min(trips)
    max_trips = max(trips)
    
    for path_id, info in attrs.items():
        if min_travel_time == max_travel_time:
            norm_tt = 0
        else:
            norm_tt = (info['label'][0] - min_travel_time)/(max_travel_time-min_travel_time)
        if min_mon_cost == max_mon_cost:
            norm_cost = 0
        else:
            norm_cost = (info['label'][1] - min_mon_cost)/(max_mon_cost-min_mon_cost)
        if min_trips == max_trips:
            norm_trip = 0
        else:
            norm_trip = (info['label'][2] - min_trips)/(max_trips-min_trips)
        norm_label = (norm_tt, norm_cost, norm_trip)
        normHeurParetoSet[OD].update({path_id: {'path': info['path'], 'label': norm_label}})

# print(normHeurParetoSet)
# print(heurParetoSet)
with open('norm_ε_ratio_based_heuristic_Pareto_set_1.05_3.pickle', 'wb') as handle:
    pickle.dump(normHeurParetoSet, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('norm_ε_ratio_based_heuristic_Pareto_set_1.05_3.pickle', 'rb') as handle:
    normHeurParetoSet = pickle.load(handle)

for OD, attrs in normFullParetoSet.items():
    eucl_dist_sum = 0
    for path_id1, info1 in attrs.items():
        eucl_dists = list()
        for path_id2, info2 in normHeurParetoSet[OD].items():
            e_dist = math.sqrt(sum([(a - b) ** 2 for a, b in zip(info1['label'], info2['label'])]))
            eucl_dists.append(e_dist)
        min_e_dist = min(eucl_dists)
        eucl_dist_sum += min_e_dist
    euclidean_distance = eucl_dist_sum/len(normFullParetoSet[OD])
    euclidean_distances.append(euclidean_distance)

average_euclidean_distance = sum(euclidean_distances)/len(euclidean_distances)
stdv_euclidean_distance = statistics.stdev(euclidean_distances)

for OD, attrs in normFullParetoSet.items():
    jacc_dist_sum = 0
    for path_id1, info1 in attrs.items():
        jacc_dists = list()
        set1 = set(info1['path'])
        for path_id2, info2 in normHeurParetoSet[OD].items():
            set2 = set(info2['path'])
            j_dist = 1 - (len(set1.intersection(set2)) / len(set1.union(set2)))
            jacc_dists.append(j_dist)
        min_j_dist = min(jacc_dists)
        jacc_dist_sum += min_j_dist
    jaccard_distance = jacc_dist_sum/len(normFullParetoSet[OD])
    jaccard_distances.append(jaccard_distance)

average_jaccard_distance = sum(jaccard_distances)/len(jaccard_distances)
stdv_jaccard_distance = statistics.stdev(jaccard_distances)

for OD, attrs in normHeurParetoSet.items():
    opt_par_perc_sum = 0
    for path_id1, info1 in attrs.items():
        for path_id2, info2 in normFullParetoSet[OD].items():
            if info1['path'] == info2['path']:
                opt_par_perc_sum += 1
                break
    optimal_pareto_paths_percentages.append((opt_par_perc_sum/len(normHeurParetoSet[OD]))*100)
    

average_optimal_pareto_paths_percentages = sum(optimal_pareto_paths_percentages)/len(optimal_pareto_paths_percentages)
stdv_optimal_pareto_paths_percentages = statistics.stdev(optimal_pareto_paths_percentages)

performance_metrics = {'Average_CPU': {'μ': average_CPU, 'σ': stdv_CPU}, \
                        'Average_Pareto_set_size': {'μ': average_pareto_set_size, 'σ': stdv_pareto_set_size}, \
                            'Average_Euclidean_distance': {'μ': average_euclidean_distance, 'σ': stdv_euclidean_distance}, \
                                'Average_Jaccard_Distance': {'μ': average_jaccard_distance, 'σ': stdv_jaccard_distance}, \
                                    'Average_Optimal_Pareto_Path_%': {'μ': average_optimal_pareto_paths_percentages, 'σ': stdv_optimal_pareto_paths_percentages}, \
                                        'Average_missed_paths_%': {'μ': average_missed_path_percentages, 'σ': stdv_missed_path_percentages}, \
                                            'Average_time_horizons':  {'μ': average_time_horizons, 'σ': stdv_time_horizons}}
        
print(performance_metrics)

print(heuristic_Pareto_set)



#------------ computation of buckets and ratio-based heuristic Pareto sets and evaluation metrics for a sample of random OD requests ---------------------#
# lam = [(4,60,5),(4,60,10),(4,60,15), (4,60,20), (4,120,5), (4,120,10), (4,120,15), (4,120,20),(3,60,5), \
#        (3,60,10),(3,60,15), (3,60,20), (3,120,5), (3,120,10), (3,120,15), (3,120,20),(2,60,5),(2,60,10), \
#            (2,60,15), (2,60,20), (2,120,5), (2,120,10), (2,120,15), (2,120,20)]
heuristic_Pareto_set = dict()
cpu_list = list()
pareto_set_size = list()
missed_path_percentages = list()
time_horizons = list()
euclidean_distances = list()
jaccard_distances = list()
optimal_pareto_paths_percentages = list()
for OD in OD_pairs:
    heuristic_Pareto_set.update({OD: dict()})
    travel_times = list()
    for path_id, attrs in fullParetoSet[OD].items():
        travel_times.append(attrs['label'][0])
    min_travel_time = min(travel_times)
    max_travel_time = max(travel_times)
    time_horizon = int(min_travel_time + (3*min_travel_time) - \
                       max(0,min_travel_time + (3*min_travel_time)-max_travel_time))
    # print(time_horizon)
    time_horizons.append(time_horizon)

    start = time.time()
    pareto_set, missed_paths_num = get_ratio_bucket_pareto_set(multimodal_graph, OD[0], OD[1], request_time_sec, \
                                        request_time_sec, request_time_sec+time_horizon, dt, 60, 5)
    end = time.time()
    
    heuristic_Pareto_set[OD] = pareto_set
    cpu_list.append(end - start)
    pareto_set_size.append(len(pareto_set))
    missed_path_percentages.append((missed_paths_num/(len(pareto_set)+missed_paths_num))*100)
    # print(cpu_list)
    # print(pareto_set_size)
    # print(missed_path_percentages)
    
    # oops = False
    # for path_id1, attrs1 in pareto_set.items():
    #     for path_id2, attrs2 in pareto_set.items():
    #         if path_id1 == path_id2:
    #             continue
    #         if attrs1['path'] == attrs2['path']:
    #             print('Duplicated paths')
    #         if attrs1['label'] == attrs2['label']:
    #             continue
    #         if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i>=j]) == len(attrs1['label']):
    #             oops = True
    #             print(attrs1['label'], attrs2['label'])
    #             break
    #         if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i<=j]) == len(attrs1['label']):
    #             oops = True
    #             print(attrs1['label'], attrs2['label'])
    #             break         
    # if oops:
    #     print('oops')
    # else:
    #     print('good')

average_CPU = sum(cpu_list)/len(cpu_list)
stdv_CPU = statistics.stdev(cpu_list)

average_pareto_set_size = sum(pareto_set_size)/len(pareto_set_size)
stdv_pareto_set_size = statistics.stdev(pareto_set_size)

average_missed_path_percentages = sum(missed_path_percentages)/len(missed_path_percentages)
stdv_missed_path_percentages = statistics.stdev(missed_path_percentages)

average_time_horizons = sum(time_horizons)/len(time_horizons)
stdv_time_horizons = statistics.stdev(time_horizons)


with open('buck_ratio_based_heuristic_Pareto_set.pickle', 'wb') as handle:
    pickle.dump(heuristic_Pareto_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('buck_ratio_based_heuristic_Pareto_set.pickle', 'rb') as handle:
    heurParetoSet = pickle.load(handle)

#---- normalize the labels of the heuristic Pareto Set ------------#
normHeurParetoSet = dict()
for OD, attrs in heurParetoSet.items():
    normHeurParetoSet.update({OD: dict()})
    travel_times = list()
    mon_costs = list()
    trips = list()
    for path_id, info in attrs.items():
        travel_times.append(info['label'][0])
        mon_costs.append(info['label'][1])
        trips.append(info['label'][2])
    min_travel_time = min(travel_times)
    max_travel_time = max(travel_times)
    min_mon_cost = min(mon_costs)
    max_mon_cost = max(mon_costs)
    min_trips = min(trips)
    max_trips = max(trips)
    
    for path_id, info in attrs.items():
        if min_travel_time == max_travel_time:
            norm_tt = 0
        else:
            norm_tt = (info['label'][0] - min_travel_time)/(max_travel_time-min_travel_time)
        if min_mon_cost == max_mon_cost:
            norm_cost = 0
        else:
            norm_cost = (info['label'][1] - min_mon_cost)/(max_mon_cost-min_mon_cost)
        if min_trips == max_trips:
            norm_trip = 0
        else:
            norm_trip = (info['label'][2] - min_trips)/(max_trips-min_trips)
        norm_label = (norm_tt, norm_cost, norm_trip)
        normHeurParetoSet[OD].update({path_id: {'path': info['path'], 'label': norm_label}})

# print(normHeurParetoSet)
# print(heurParetoSet)
with open('buck_ratio_based_heuristic_Pareto_set.pickle', 'wb') as handle:
    pickle.dump(normHeurParetoSet, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('buck_ratio_based_heuristic_Pareto_set.pickle', 'rb') as handle:
    normHeurParetoSet = pickle.load(handle)

for OD, attrs in normFullParetoSet.items():
    eucl_dist_sum = 0
    for path_id1, info1 in attrs.items():
        eucl_dists = list()
        for path_id2, info2 in normHeurParetoSet[OD].items():
            e_dist = math.sqrt(sum([(a - b) ** 2 for a, b in zip(info1['label'], info2['label'])]))
            eucl_dists.append(e_dist)
        min_e_dist = min(eucl_dists)
        eucl_dist_sum += min_e_dist
    euclidean_distance = eucl_dist_sum/len(normFullParetoSet[OD])
    euclidean_distances.append(euclidean_distance)

average_euclidean_distance = sum(euclidean_distances)/len(euclidean_distances)
stdv_euclidean_distance = statistics.stdev(euclidean_distances)

for OD, attrs in normFullParetoSet.items():
    jacc_dist_sum = 0
    for path_id1, info1 in attrs.items():
        jacc_dists = list()
        set1 = set(info1['path'])
        for path_id2, info2 in normHeurParetoSet[OD].items():
            set2 = set(info2['path'])
            j_dist = 1 - (len(set1.intersection(set2)) / len(set1.union(set2)))
            jacc_dists.append(j_dist)
        min_j_dist = min(jacc_dists)
        jacc_dist_sum += min_j_dist
    jaccard_distance = jacc_dist_sum/len(normFullParetoSet[OD])
    jaccard_distances.append(jaccard_distance)

average_jaccard_distance = sum(jaccard_distances)/len(jaccard_distances)
stdv_jaccard_distance = statistics.stdev(jaccard_distances)

for OD, attrs in normHeurParetoSet.items():
    opt_par_perc_sum = 0
    for path_id1, info1 in attrs.items():
        for path_id2, info2 in normFullParetoSet[OD].items():
            if info1['path'] == info2['path']:
                opt_par_perc_sum += 1
                break
    optimal_pareto_paths_percentages.append((opt_par_perc_sum/len(normHeurParetoSet[OD]))*100)
    

average_optimal_pareto_paths_percentages = sum(optimal_pareto_paths_percentages)/len(optimal_pareto_paths_percentages)
stdv_optimal_pareto_paths_percentages = statistics.stdev(optimal_pareto_paths_percentages)

performance_metrics = {'Average_CPU': {'μ': average_CPU, 'σ': stdv_CPU}, \
                        'Average_Pareto_set_size': {'μ': average_pareto_set_size, 'σ': stdv_pareto_set_size}, \
                            'Average_Euclidean_distance': {'μ': average_euclidean_distance, 'σ': stdv_euclidean_distance}, \
                                'Average_Jaccard_Distance': {'μ': average_jaccard_distance, 'σ': stdv_jaccard_distance}, \
                                    'Average_Optimal_Pareto_Path_%': {'μ': average_optimal_pareto_paths_percentages, 'σ': stdv_optimal_pareto_paths_percentages}, \
                                        'Average_missed_paths_%': {'μ': average_missed_path_percentages, 'σ': stdv_missed_path_percentages}, \
                                            'Average_time_horizons':  {'μ': average_time_horizons, 'σ': stdv_time_horizons}}
        
print(performance_metrics)

#------------ computation of epsilon and ratio-based heuristic Pareto sets and evaluation metrics for a sample of random OD requests ---------------------#
heuristic_Pareto_set = dict()
cpu_list = list()
pareto_set_size = list()
missed_path_percentages = list()
time_horizons = list()
euclidean_distances = list()
jaccard_distances = list()
optimal_pareto_paths_percentages = list()

for OD in OD_pairs:
    heuristic_Pareto_set.update({OD: dict()})
    travel_times = list()
    for path_id, attrs in fullParetoSet[OD].items():
        travel_times.append(attrs['label'][0])
    min_travel_time = min(travel_times)
    # print(min_travel_time)
    max_travel_time = max(travel_times)
    # print(max_travel_time)
    time_horizon = int(min_travel_time + (3*min_travel_time) - \
                       max(0,min_travel_time + (3*min_travel_time)-max_travel_time))
    # print(time_horizon)
    # time_horizon_2 = int(4*min_travel_time)
    # print(time_horizon_2)
    time_horizons.append(time_horizon)

    start = time.time()
    pareto_set, missed_paths_num = get_ε_ratio_pareto_set(multimodal_graph, OD[0], OD[1], request_time_sec, \
                                        request_time_sec, request_time_sec+time_horizon, dt, 1.05)
    end = time.time()
    
    heuristic_Pareto_set[OD] = pareto_set
    cpu_list.append(end - start)
    pareto_set_size.append(len(pareto_set))
    missed_path_percentages.append((missed_paths_num/(len(pareto_set)+missed_paths_num))*100)
    # print(cpu_list)
    # print(pareto_set_size)
    # # print(missed_path_percentages)
    # print(time_horizons)
    
    # oops = False
    # for path_id1, attrs1 in pareto_set.items():
    #     for path_id2, attrs2 in pareto_set.items():
    #         if path_id1 == path_id2:
    #             continue
    #         if attrs1['path'] == attrs2['path']:
    #             print('Duplicated paths')
    #         if attrs1['label'] == attrs2['label']:
    #             continue
    #         if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i>=j]) == len(attrs1['label']):
    #             oops = True
    #             print(attrs1['label'], attrs2['label'])
    #             break
    #         if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i<=j]) == len(attrs1['label']):
    #             oops = True
    #             print(attrs1['label'], attrs2['label'])
    #             break         
    # if oops:
    #     print('oops')
    # else:
    #     print('good')

average_CPU = sum(cpu_list)/len(cpu_list)
stdv_CPU = statistics.stdev(cpu_list)

average_pareto_set_size = sum(pareto_set_size)/len(pareto_set_size)
stdv_pareto_set_size = statistics.stdev(pareto_set_size)

average_missed_path_percentages = sum(missed_path_percentages)/len(missed_path_percentages)
stdv_missed_path_percentages = statistics.stdev(missed_path_percentages)

average_time_horizons = sum(time_horizons)/len(time_horizons)
stdv_time_horizons = statistics.stdev(time_horizons)


with open('ε_ratio_based_heuristic_Pareto_set_1.05_3.pickle', 'wb') as handle:
    pickle.dump(heuristic_Pareto_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('ε_ratio_based_heuristic_Pareto_set_1.05_3.pickle', 'rb') as handle:
    heurParetoSet = pickle.load(handle)

#---- normalize the labels of the heuristic Pareto Set ------------#
normHeurParetoSet = dict()
for OD, attrs in heurParetoSet.items():
    normHeurParetoSet.update({OD: dict()})
    travel_times = list()
    mon_costs = list()
    trips = list()
    for path_id, info in attrs.items():
        travel_times.append(info['label'][0])
        mon_costs.append(info['label'][1])
        trips.append(info['label'][2])
    min_travel_time = min(travel_times)
    max_travel_time = max(travel_times)
    min_mon_cost = min(mon_costs)
    max_mon_cost = max(mon_costs)
    min_trips = min(trips)
    max_trips = max(trips)
    
    for path_id, info in attrs.items():
        if min_travel_time == max_travel_time:
            norm_tt = 0
        else:
            norm_tt = (info['label'][0] - min_travel_time)/(max_travel_time-min_travel_time)
        if min_mon_cost == max_mon_cost:
            norm_cost = 0
        else:
            norm_cost = (info['label'][1] - min_mon_cost)/(max_mon_cost-min_mon_cost)
        if min_trips == max_trips:
            norm_trip = 0
        else:
            norm_trip = (info['label'][2] - min_trips)/(max_trips-min_trips)
        norm_label = (norm_tt, norm_cost, norm_trip)
        normHeurParetoSet[OD].update({path_id: {'path': info['path'], 'label': norm_label}})

# print(normHeurParetoSet)
# print(heurParetoSet)
with open('norm_ε_ratio_based_heuristic_Pareto_set_1.05_3.pickle', 'wb') as handle:
    pickle.dump(normHeurParetoSet, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('norm_ε_ratio_based_heuristic_Pareto_set_1.05_3.pickle', 'rb') as handle:
    normHeurParetoSet = pickle.load(handle)

for OD, attrs in normFullParetoSet.items():
    eucl_dist_sum = 0
    for path_id1, info1 in attrs.items():
        eucl_dists = list()
        for path_id2, info2 in normHeurParetoSet[OD].items():
            e_dist = math.sqrt(sum([(a - b) ** 2 for a, b in zip(info1['label'], info2['label'])]))
            eucl_dists.append(e_dist)
        min_e_dist = min(eucl_dists)
        eucl_dist_sum += min_e_dist
    euclidean_distance = eucl_dist_sum/len(normFullParetoSet[OD])
    euclidean_distances.append(euclidean_distance)

average_euclidean_distance = sum(euclidean_distances)/len(euclidean_distances)
stdv_euclidean_distance = statistics.stdev(euclidean_distances)

for OD, attrs in normFullParetoSet.items():
    jacc_dist_sum = 0
    for path_id1, info1 in attrs.items():
        jacc_dists = list()
        set1 = set(info1['path'])
        for path_id2, info2 in normHeurParetoSet[OD].items():
            set2 = set(info2['path'])
            j_dist = 1 - (len(set1.intersection(set2)) / len(set1.union(set2)))
            jacc_dists.append(j_dist)
        min_j_dist = min(jacc_dists)
        jacc_dist_sum += min_j_dist
    jaccard_distance = jacc_dist_sum/len(normFullParetoSet[OD])
    jaccard_distances.append(jaccard_distance)

average_jaccard_distance = sum(jaccard_distances)/len(jaccard_distances)
stdv_jaccard_distance = statistics.stdev(jaccard_distances)

for OD, attrs in normHeurParetoSet.items():
    opt_par_perc_sum = 0
    for path_id1, info1 in attrs.items():
        for path_id2, info2 in normFullParetoSet[OD].items():
            if info1['path'] == info2['path']:
                opt_par_perc_sum += 1
                break
    optimal_pareto_paths_percentages.append((opt_par_perc_sum/len(normHeurParetoSet[OD]))*100)
    

average_optimal_pareto_paths_percentages = sum(optimal_pareto_paths_percentages)/len(optimal_pareto_paths_percentages)
stdv_optimal_pareto_paths_percentages = statistics.stdev(optimal_pareto_paths_percentages)

performance_metrics = {'Average_CPU': {'μ': average_CPU, 'σ': stdv_CPU}, \
                        'Average_Pareto_set_size': {'μ': average_pareto_set_size, 'σ': stdv_pareto_set_size}, \
                            'Average_Euclidean_distance': {'μ': average_euclidean_distance, 'σ': stdv_euclidean_distance}, \
                                'Average_Jaccard_Distance': {'μ': average_jaccard_distance, 'σ': stdv_jaccard_distance}, \
                                    'Average_Optimal_Pareto_Path_%': {'μ': average_optimal_pareto_paths_percentages, 'σ': stdv_optimal_pareto_paths_percentages}, \
                                        'Average_missed_paths_%': {'μ': average_missed_path_percentages, 'σ': stdv_missed_path_percentages}, \
                                            'Average_time_horizons':  {'μ': average_time_horizons, 'σ': stdv_time_horizons}}
        
print(performance_metrics)

# ---- plots for depdence of time between ODs, Pareto set size and runtimes

fields1 = ['time', 'runtime']
rows1 = []
for i in range(0,len(time_horizons)):
    rows1.append([time_horizons[i],cpu_list[i]])
# print(my_list1)
    
# name of csv file  
filename = "time_runtime1.csv"
    
# writing to csv file  
with open(filename, 'w', newline='') as csvfile:  
    # creating a csv writer object  
    csvwriter = csv.writer(csvfile)  
        
    # writing the fields  
    csvwriter.writerow(fields1)  
        
    # writing the data rows  
    csvwriter.writerows(rows1) 

fields2 = ['time', 'size']

rows2 = []
for i in range(0,len(time_horizons)):
    rows2.append([time_horizons[i],pareto_set_size[i]])

# name of csv file  
filename = "time_size1.csv"
    
# writing to csv file  
with open(filename, 'w', newline='') as csvfile:  
    # creating a csv writer object  
    csvwriter = csv.writer(csvfile)  
        
    # writing the fields  
    csvwriter.writerow(fields2)  
        
    # writing the data rows  
    csvwriter.writerows(rows2)


# #----------------------- Ellipse ---------#
# heuristic_Pareto_set = dict()
# cpu_list = list()
# pareto_set_size = list()
# missed_path_percentages = list()
# time_horizons = list()
# euclidean_distances = list()
# jaccard_distances = list()
# optimal_pareto_paths_percentages = list()
# for OD in OD_pairs:
#     heuristic_Pareto_set.update({OD: dict()})
#     time_horizon = int(walk_times_per_OD[OD])
#     time_horizons.append(time_horizon)
#     print(time_horizon)

#     start = time.time()
#     pareto_set, missed_paths_num = get_ellipse_pareto_set(multimodal_graph, OD[0], OD[1], request_time_sec, \
#                                         request_time_sec, request_time_sec+time_horizon, dt, 1.1)
#     end = time.time()
    
#     heuristic_Pareto_set[OD] = pareto_set
#     cpu_list.append(end - start)
#     pareto_set_size.append(len(pareto_set))
#     missed_path_percentages.append((missed_paths_num/(len(pareto_set)+missed_paths_num))*100)
#     print(cpu_list)
#     print(pareto_set_size)
#     print(missed_path_percentages)
    
#     # oops = False
#     # for path_id1, attrs1 in pareto_set.items():
#     #     for path_id2, attrs2 in pareto_set.items():
#     #         if path_id1 == path_id2:
#     #             continue
#     #         if attrs1['path'] == attrs2['path']:
#     #             print('Duplicated paths')
#     #         if attrs1['label'] == attrs2['label']:
#     #             continue
#     #         if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i>=j]) == len(attrs1['label']):
#     #             oops = True
#     #             print(attrs1['label'], attrs2['label'])
#     #             break
#     #         if len([True for i,j in zip(attrs1['label'],attrs2['label']) if i<=j]) == len(attrs1['label']):
#     #             oops = True
#     #             print(attrs1['label'], attrs2['label'])
#     #             break         
#     # if oops:
#     #     print('oops')
#     # else:
#     #     print('good')

# average_CPU = sum(cpu_list)/len(cpu_list)
# stdv_CPU = statistics.stdev(cpu_list)

# average_pareto_set_size = sum(pareto_set_size)/len(pareto_set_size)
# stdv_pareto_set_size = statistics.stdev(pareto_set_size)

# average_missed_path_percentages = sum(missed_path_percentages)/len(missed_path_percentages)
# stdv_missed_path_percentages = statistics.stdev(missed_path_percentages)

# average_time_horizons = sum(time_horizons)/len(time_horizons)
# stdv_time_horizons = statistics.stdev(time_horizons)


# with open('buck_ratio_based_heuristic_Pareto_set.pickle', 'wb') as handle:
#     pickle.dump(heuristic_Pareto_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('buck_ratio_based_heuristic_Pareto_set.pickle', 'rb') as handle:
#     heurParetoSet = pickle.load(handle)

# #---- normalize the labels of the heuristic Pareto Set ------------#
# normHeurParetoSet = dict()
# for OD, attrs in heurParetoSet.items():
#     normHeurParetoSet.update({OD: dict()})
#     travel_times = list()
#     mon_costs = list()
#     trips = list()
#     for path_id, info in attrs.items():
#         travel_times.append(info['label'][0])
#         mon_costs.append(info['label'][1])
#         trips.append(info['label'][2])
#     min_travel_time = min(travel_times)
#     max_travel_time = max(travel_times)
#     min_mon_cost = min(mon_costs)
#     max_mon_cost = max(mon_costs)
#     min_trips = min(trips)
#     max_trips = max(trips)
    
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
#         norm_label = (norm_tt, norm_cost, norm_trip)
#         normHeurParetoSet[OD].update({path_id: {'path': info['path'], 'label': norm_label}})

# # print(normHeurParetoSet)
# # print(heurParetoSet)
# with open('buck_ratio_based_heuristic_Pareto_set.pickle', 'wb') as handle:
#     pickle.dump(normHeurParetoSet, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('buck_ratio_based_heuristic_Pareto_set.pickle', 'rb') as handle:
#     normHeurParetoSet = pickle.load(handle)

# for OD, attrs in normFullParetoSet.items():
#     eucl_dist_sum = 0
#     for path_id1, info1 in attrs.items():
#         eucl_dists = list()
#         for path_id2, info2 in normHeurParetoSet[OD].items():
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
#         for path_id2, info2 in normHeurParetoSet[OD].items():
#             set2 = set(info2['path'])
#             j_dist = 1 - (len(set1.intersection(set2)) / len(set1.union(set2)))
#             jacc_dists.append(j_dist)
#         min_j_dist = min(jacc_dists)
#         jacc_dist_sum += min_j_dist
#     jaccard_distance = jacc_dist_sum/len(normFullParetoSet[OD])
#     jaccard_distances.append(jaccard_distance)

# average_jaccard_distance = sum(jaccard_distances)/len(jaccard_distances)
# stdv_jaccard_distance = statistics.stdev(jaccard_distances)

# for OD, attrs in normHeurParetoSet.items():
#     opt_par_perc_sum = 0
#     for path_id1, info1 in attrs.items():
#         for path_id2, info2 in normFullParetoSet[OD].items():
#             if info1['path'] == info2['path']:
#                 opt_par_perc_sum += 1
#                 break
#     optimal_pareto_paths_percentages.append((opt_par_perc_sum/len(normHeurParetoSet[OD]))*100)
    

# average_optimal_pareto_paths_percentages = sum(optimal_pareto_paths_percentages)/len(optimal_pareto_paths_percentages)
# stdv_optimal_pareto_paths_percentages = statistics.stdev(optimal_pareto_paths_percentages)

# performance_metrics = {'Average_CPU': {'μ': average_CPU, 'σ': stdv_CPU}, \
#                         'Average_Pareto_set_size': {'μ': average_pareto_set_size, 'σ': stdv_pareto_set_size}, \
#                             'Average_Euclidean_distance': {'μ': average_euclidean_distance, 'σ': stdv_euclidean_distance}, \
#                                 'Average_Jaccard_Distance': {'μ': average_jaccard_distance, 'σ': stdv_jaccard_distance}, \
#                                     'Average_Optimal_Pareto_Path_%': {'μ': average_optimal_pareto_paths_percentages, 'σ': stdv_optimal_pareto_paths_percentages}, \
#                                         'Average_missed_paths_%': {'μ': average_missed_path_percentages, 'σ': stdv_missed_path_percentages}, \
#                                             'Average_time_horizons':  {'μ': average_time_horizons, 'σ': stdv_time_horizons}}
        
# print(performance_metrics)

