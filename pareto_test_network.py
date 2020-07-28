# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 01:23:14 2020

@author: Lampros Yfantis
"""

import networkx as nx
import time
from sys import getsizeof
from collections import deque
import random
import cProfile, pstats, io
import matplotlib as plt
from networkx.drawing.nx_pylab import draw_networkx, draw_networkx_edge_labels
from networkx.algorithms.simple_paths import pareto_paths_with_attrs_backwards_test
from bisect import bisect_left


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

J = nx.DiGraph()


def gen_rand_num_dict():
    time_val = {}
    for t in range(0, 7201):
        time_val[t] = random.randint(1,500)
    return time_val

J.add_edges_from([(1, 2, {'x':gen_rand_num_dict(), 'y':gen_rand_num_dict(), 'z':gen_rand_num_dict(), 'k':gen_rand_num_dict()}), \
                  (1, 3, {'x':gen_rand_num_dict(), 'y':gen_rand_num_dict(), 'z':gen_rand_num_dict(), 'k':gen_rand_num_dict()}), \
                  (1, 4, {'x':gen_rand_num_dict(), 'y':gen_rand_num_dict(), 'z':gen_rand_num_dict(), 'k':gen_rand_num_dict()}), \
                  (2, 3, {'x':gen_rand_num_dict(), 'y':gen_rand_num_dict(), 'z':gen_rand_num_dict(), 'k':gen_rand_num_dict()}), \
                  (2, 5, {'x':gen_rand_num_dict(), 'y':gen_rand_num_dict(), 'z':gen_rand_num_dict(), 'k':gen_rand_num_dict()}), \
                  (3, 2, {'x':gen_rand_num_dict(), 'y':gen_rand_num_dict(), 'z':gen_rand_num_dict(), 'k':gen_rand_num_dict()}), \
                  (3, 5, {'x':gen_rand_num_dict(), 'y':gen_rand_num_dict(), 'z':gen_rand_num_dict(), 'k':gen_rand_num_dict()}), \
                  (3, 6, {'x':gen_rand_num_dict(), 'y':gen_rand_num_dict(), 'z':gen_rand_num_dict(), 'k':gen_rand_num_dict()}), \
                  (4, 1, {'x':gen_rand_num_dict(), 'y':gen_rand_num_dict(), 'z':gen_rand_num_dict(), 'k':gen_rand_num_dict()}), \
                  (4, 5, {'x':gen_rand_num_dict(), 'y':gen_rand_num_dict(), 'z':gen_rand_num_dict(), 'k':gen_rand_num_dict()}), \
                  (6, 4, {'x':gen_rand_num_dict(), 'y':gen_rand_num_dict(), 'z':gen_rand_num_dict(), 'k':gen_rand_num_dict()}), \
                  (6, 5, {'x':gen_rand_num_dict(), 'y':gen_rand_num_dict(), 'z':gen_rand_num_dict(), 'k':gen_rand_num_dict()})])

#start = time.time()
###@profile
###def elamou():
#pareto_paths = pareto_paths_with_attrs_backwards_test(J, 1, 5, 0, 0, 7200, 1, 'x', 'y', 'z', 'k')
#end = time.time()
#print('Algorithm path Running time: %f sec' % (end - start))
##print(par_path)
#print(pareto_paths)
##elamou()
#x = {1: 2, 3: 4, 4: 3, 2: 1, 0: 0}
#print({k: v for k, v in sorted(x.items(), key=lambda item: item[1])})
#for u, v, weight in J.edges.data():
#    
#    for i, v in weight.items():
#        pass
#    
#lam = (1, 2)
#for i in lam:
#    print(i)
#lam = [1,2,3,4]
#print(lam[-5])
l = 10
k = 0
while k <=5:
    if l == 10:
        p =2
        k = k+1
        continue
    p =100
    k = k+1
print(p)
#ken = lam[7:]
#print(ken)
#print(105310%86400)
#for i in range(1, 10):
#    print(i)
##    k_shortest_paths_LY(pt_walk_TNCs_cs_graph, OD_pair[0], OD_pair[1], request_time_sec, 20, travel_time='travel_time', distance='distance', \
##                        pt_additive_cost='pt_distance_based_cost', pt_non_additive_cost='pt_zone_to_zone_cost', taxi_fares='taxi_fares', \
##                        taxi_wait_time='taxi_wait_time', timetable='departure_time', edge_type='edge_type', node_type='node_type', \
##                        node_graph_type='node_graph_type', fare_scheme='zone_to_zone', walk_attrs_w=walk_attrs_weights, \
##                        bus_attrs_w=bus_attrs_weights, train_attrs_w=train_attrs_weights, taxi_attrs_w=taxi_attrs_weights, \
##                        sms_attrs_w=sms_attrs_weight, sms_pool_attrs_w=sms_pool_attrs_weights, cs_attrs_w=carsharing_attrs_weights, \
##                        mode_transfer_weight=mode_trf_weights)
##
##elamou()
#
##lam = {}
#
#for i in range(0, 871):
#    lam[i] = {}z
#    for j in range(0, 91):
#        lam[i][j] = {}
#        for k in range(1, 10):
#            lam[i][j][k] = 1
#            
#print(len(lam))
#
#print(getsizeof(lam))
#
#gamw = deque([7, 2, 9, 3])
#
#
#          
#lam = set()
#lam.add(1)
#lamyfa = set()
#lamyfa.update(lam)
#print(lamyfa)
#x = lam.add(1)
#print(x)
#if not(False):
#    print('!!!')
    
#lam = (4, 3, 4)
#yfa = (3, 2, 3)
#k = 0
#    
#for i,j in zip(lam,yfa):
#    if i>=j:
#        k=k+1
#        
#print(k)
#print(0!=None)
#x = {1: 2, 3: 4, 4: 5, 2: 1, 0: 0}
#for i, j in x[1][2]:
#    print(j)
#lam = deque([1,2,3])
#for i in lam:
#    print(i)
    
#def find_ge(a, x):  # binary search algorithm #'Find leftmost item greater than or equal to x'
#  i = bisect_left(a, x)
#  if i != len(a):
#    return i, a[i]
#  raise ValueError    
#print(lam)
#print(find_ge(lam, 2))
test_list = [1,2,3,4,5,6,7] 
  
# printing original list 
#print("The original list : " + str(test_list)) 
#  
## using list comprehension + zip() + slicing + enumerate() 
## Split list into lists by particular value 
size = len(test_list) 
idx_list = [idx + 1 for idx, val in
            enumerate(test_list) if val == 3] 

print(idx_list)
  
  
res = [test_list[i: j] for i, j in
        zip([0] + idx_list, idx_list + 
        ([size] if idx_list[-1] != size else []))]
        
print(res[1])
#  
## print result 
#print("The list after splitting by a value : " + str(res)) 