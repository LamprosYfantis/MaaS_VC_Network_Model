import csv
import math
import time
import networkx as nx
import pandas as pd
import numpy as np
from numpy.linalg import norm
from shapely.geometry import Point, LineString
from networkx.classes.function import number_of_edges, number_of_nodes
from pedest_graph_gen_with_infra_funct import find_proj, gen_walk_graph_nodes_with_infra, gen_walk_graph_edges_with_attrs


ped_graph = nx.DiGraph()

gen_walk_graph_nodes_with_infra(ped_graph)
#print(ped_graph.number_of_nodes())
gen_walk_graph_edges_with_attrs(ped_graph)
#print(ped_graph.number_of_edges())
neighs = ped_graph.succ
#print(neighs)
#print(neighs('w7'))
#print(next(neighs('w7')))
#print(next(neighs('w7')))
#print(next(neighs('w7')))
#
#for node in ped_graph.successors('w7'):
#    print(node)
print(ped_graph.nodes['w7'].items())



#print(ped_graph._succ)
#for node, el in neighs('w10').items():
#    print(node, el)
#ignore_nodes = ('w7', 'w10', 'w75')
#Gsucc = ped_graph.succ
#print(Gsucc)

#for n in Gsucc('w6'):
#    print(n)

    # support optional nodes filter
#if ignore_nodes:
#    def filter_iter(nodes):
#        def iterate(v):
#            for w in nodes(v):
#                if w not in ignore_nodes:
#                    yield w
#        return iterate
#
#    Gsucc = filter_iter(Gsucc)
#
#lam = ('1')
#Gsucc = {'1': {'2': {'x': 1, 'y':2}, '3': {'x': 10, 'y': 15}}, '2': {'1': {'x': 1, 'y':2}, '3': {'x': 10, 'y': 15}}, '3': {'1': {'x': 1, 'y':2}, '2': {'x': 10, 'y': 15}}}
#
#if lam:
#    def filter_iter(nodes):
#        def iterate(v):
#            for w, attrs in nodes[v].items():
#                if w not in lam:
#                    yield w, attrs
#        return iterate
#
#    Gsucc = filter_iter(Gsucc)
#    
#
#neighs = Gsucc
#for n, els in neighs('2'):
#    print(n, els)

#for n in neighs('1'):
#    print(n)
#for n in Gsucc(0):
#    print(n)

# support optional edges filter
#if ignore_edges:
#    def filter_succ_iter(succ_iter):
#        def iterate(v):
#            for w in succ_iter(v):
#                if (v, w) not in ignore_edges:
#                    yield w
#        return iterate
#
#    Gsucc = filter_succ_iter(Gsucc)

#def _LY_dijkstra(G, source, target, time_of_request, travel_time_data, distance_data, pt_additive_cost_data, pt_non_additive_cost_data, taxi_fares, taxi_wait_time, timetable_data, edge_type_data, node_type_data, node_graph_type_data, fare_scheme, ignore_nodes, ignore_edges, init_weight, init_travel_time, init_wait_time, init_distance, init_cost, init_num_line_trfs, init_num_mode_trfs, last_edge_type, last_upstr_node_graph_type, last_pt_veh_run_id, current_time, last_edge_cost, pt_trip_orig_zone, previous_edge_mode, walk_attrs_w, bus_attrs_w, train_attrs_w, taxi_attrs_w, sms_attrs_w, sms_pool_attrs_w, cs_attrs_w, mode_transfer_weight, orig_source, pred=None, paths=None):
#
#  # handles only directed
#    Gsucc = G.succ
#    # support optional nodes filter
#    if ignore_nodes:
#        def filter_iter(nodes):
#            def iterate(v):
#                for w, attrs in nodes[v].items():
#                    if w not in ignore_nodes:
#                        yield w, attrs
#            return iterate
#
#        Gsucc = filter_iter(Gsucc)
#        neighs = Gsucc
#    else:
#        def neighbours(nodes):
#            def iterate(v):
#                for w, attrs in nodes[v].items():
#                    yield w, attrs
#            return iterate
#        Gsucc = neighbours(Gsucc)
#        neighs = Gsucc
#
#    # support optional edges filter
##    if ignore_edges:
##        def filter_succ_iter(succ_iter):
##            def iterate(v):
##                for w in succ_iter(v):
##                    if (v, w) not in ignore_edges:
##                        yield w
##            return iterate
##
##        Gsucc = filter_succ_iter(Gsucc)
#
#    push = heappush
#    pop = heappop
#
#
#    weight_label = {}  # dictionary of best weight
#    travel_time_label = {}
#    wait_time_label = {}
#    distance_label = {}
#    mon_cost_label = {}
#    line_trans_num_label = {}
#    mode_trans_num_label = {}
#    prev_edge_type_label = {}
#    prev_upstr_node_graph_type_label = {}
#    last_pt_veh_run_id_label = {}
#    current_time_label = {}
#    prev_edge_cost_label = {}
#    pt_trip_start_zone_label = {}
#    prev_mode_label = {}
#    seen = {}
#
#
#    c = count()   # use the count c to avoid comparing nodes (may not be able to)
#    fringe = []  # fringe is heapq with 3-tuples (distance,c,node) -and I change it to a 4-tuple to store the type of the previous edge
#
#
#    prev_edge_type = last_edge_type
#    prev_upstr_node_graph_type = last_upstr_node_graph_type
#    run_id_till_node_u = last_pt_veh_run_id
#    previous_edge_cost = last_edge_cost
#    zone_at_start_of_pt_trip = pt_trip_orig_zone
#    prev_mode = previous_edge_mode
#
#    curr_time = current_time
#    seen[source] = init_weight
#
#    push(fringe, (init_weight, next(c), source, init_travel_time, init_wait_time, init_distance, init_cost, init_num_line_trfs, init_num_mode_trfs, prev_edge_type, prev_upstr_node_graph_type, run_id_till_node_u, curr_time, previous_edge_cost, zone_at_start_of_pt_trip, prev_mode))                      # LY: added initial time of request as argument and prev_edge_type
#
#    while fringe:
#        (gen_w, _, v, tt, wtt, d, mon_c, n_l_ts, n_m_ts, pr_ed_tp, pre_upstr_n_gr_tp, lt_run_id, curr_time, pr_e_cost, pt_tr_st_z, pr_md) = pop(fringe)
#
#        if v in weight_label:
#            continue  # already searched this node.
#
#        weight_label[v] = gen_w
#        travel_time_label[v] = tt
#        wait_time_label[v] = wtt
#        distance_label[v] = d
#        mon_cost_label[v] = mon_c
#        line_trans_num_label[v] = n_l_ts
#        mode_trans_num_label[v] = n_m_ts
#        prev_edge_type_label[v] = pr_ed_tp
#        prev_upstr_node_graph_type_label[v] = pre_upstr_n_gr_tp
#        last_pt_veh_run_id_label[v] = lt_run_id
#        current_time_label[v] = curr_time
#        prev_edge_cost_label[v] = pr_e_cost
#        pt_trip_start_zone_label[v] = pt_tr_st_z
#        prev_mode_label[v] = pr_md
#        
#        node_gr_type_data = nx.get_node_attributes(G, 'node_graph_type')
#
#        if v == target:
#          break
##        if v == '11,5_2,5':
##            print('stop')
##        if v == '40,3_1,6':
##            print('stop')
##        if v == '60,5_2,7':
##            print('stop')
##        if v ==  'w_bus_stop47':
##            print('oops')
##        if v == 'b47':
##            print('oops')
##        if v == 'b38':
##            print('oops')
#
#        for u, e in neighs(v):
##          if u == '40,3_1,6':
##            print('stop')
#          e_type = edge_type_data(v, u, e)
#          # n_type = node_type_data(v, G.nodes[v])
#          n_gr_type = node_gr_type_data[v]
#          prev_mode = pr_md
#          zone_at_start_of_pt_trip = pt_tr_st_z
#          previous_edge_cost = pr_e_cost
#
#
#          if e_type == 'car_sharing_station_egress_edge' or e_type == 'car_sharing_station_access_edge':
#            penalty = 0
#            e_tt = 0
#            e_wait_time = e['wait_time']
#            e_cost=0
#            e_distance = 0
#            e_num_lin_trf = 0
#            e_num_mode_trf = 0
#
#            travel_time_till_u = travel_time_label[v] + e_tt
#            wait_time_till_u = wait_time_label[v] + e_wait_time
#            distance_till_u = distance_label[v] + e_distance
#            cost_till_u = mon_cost_label[v] + e_cost
#            line_trasnf_num_till_u = line_trans_num_label[v] + e_num_lin_trf
#            mode_transf_num_till_u = mode_trans_num_label[v] + e_num_mode_trf
#            time_till_u = curr_time + e_tt + e_wait_time
#
#            if e_type == 'car_sharing_station_egress_edge' and pr_ed_tp != 'access_edge':
#              penalty = math.inf
#
#            vu_dist = weight_label[v] + cs_attrs_w[0]*e_tt + cs_attrs_w[1]*e_wait_time + cs_attrs_w[2]*e_distance + cs_attrs_w[3]*e_cost + cs_attrs_w[4]*e_num_lin_trf + penalty
#
#
#          if e_type == 'car_sharing_orig_dummy_edge':
#            e_wait_time = 0
#            e_tt = 0
#            e_distance = 0
#            e_cost = 0
#            e_num_mode_trf = 0
#            e_num_lin_trf = 0
#
#            travel_time_till_u = travel_time_label[v] + e_tt
#            wait_time_till_u = wait_time_label[v] + e_wait_time
#            distance_till_u = distance_label[v] + e_distance
#            cost_till_u = mon_cost_label[v] + e_cost
#            line_trasnf_num_till_u = line_trans_num_label[v] + e_num_lin_trf
#            mode_transf_num_till_u = mode_trans_num_label[v] + e_num_mode_trf
#            time_till_u = curr_time + e_tt + e_wait_time
#
#            vu_dist = weight_label[v] + cs_attrs_w[0]*e_tt + cs_attrs_w[1]*e_wait_time + cs_attrs_w[2]*e_distance + cs_attrs_w[3]*e_cost + cs_attrs_w[4]*e_num_lin_trf
#
#          if e_type == 'car_sharing_dest_dummy_edge' or e_type == 'car_sharing_dual_edge':
#            e_wait_time = 0
#            tt_d = travel_time_data(v, u, e)
#            if tt_d is None:
#              print('Missing in_veh_tt value in edge {}'.format((v, u)))
#              continue
#            e_tt = get_time_dep_taxi_travel_time(curr_time+e_wait_time, tt_d) # used this function cause it works the way it should, need to however have some generic function to extract data from different type of dictionaries without being mode-specific
#            e_distance = distance_data(v, u, e)
#            if e_distance is None:
#              print('Missing distance value in edge {}'.format((v, u)))
#              continue
#            e_cost_data = e['car_sharing_fares']
#            e_cost = get_time_dep_taxi_cost(curr_time, e_cost_data) # # used this function cause it works the way it should, need to however have some generic function to extract data from different type of dictionaries without being mode-specific
#            e_num_mode_trf = 0
#            e_num_lin_trf = 0
#
#            travel_time_till_u = travel_time_label[v] + e_tt
#            wait_time_till_u = wait_time_label[v] + e_wait_time
#            distance_till_u = distance_label[v] + e_distance
#            cost_till_u = mon_cost_label[v] + e_cost
#            line_trasnf_num_till_u = line_trans_num_label[v] + e_num_lin_trf
#            mode_transf_num_till_u = mode_trans_num_label[v] + e_num_mode_trf
#            time_till_u = curr_time + e_tt + e_wait_time
#
#            vu_dist = weight_label[v] + cs_attrs_w[0]*e_tt + cs_attrs_w[1]*e_wait_time + cs_attrs_w[2]*e_distance + cs_attrs_w[3]*e_cost + cs_attrs_w[4]*e_num_lin_trf
#
#
#          if e_type == 'taxi_edge' or e_type == 'on_demand_single_taxi_edge' or e_type == 'on_demand_shared_taxi_edge':
#            e_wait_time_data = taxi_wait_time(v, u, e)
#            e_wait_time = get_time_dep_taxi_wait_time(curr_time, e_wait_time_data)
#            tt_d = travel_time_data(v, u, e)
#            if tt_d is None:
#              print('Missing in_veh_tt value in edge {}'.format((v, u)))
#              continue
#            e_tt = get_time_dep_taxi_travel_time(curr_time+e_wait_time, tt_d)
#            e_distance = distance_data(v, u, e)        # funtion that extracts the edge's distance attribute
#            if e_distance is None:
#              print('Missing distance value in edge {}'.format((v, u)))
#              continue
#            e_num_mode_trf = 0
#            e_num_lin_trf = 0
#
#            # if pr_ed_tp == 'access_edge':
#            #   zone_at_start_of_pt_trip = G.nodes[v]['zone']
#            #   previous_edge_cost = 0
#
#
#            e_cost_data = taxi_fares(v, u, e)
#            e_cost = get_time_dep_taxi_cost(curr_time, e_cost_data)
#
#
#            travel_time_till_u = travel_time_label[v] + e_tt
#            wait_time_till_u = wait_time_label[v] + e_wait_time
#            distance_till_u = distance_label[v] + e_distance
#            cost_till_u = mon_cost_label[v] + e_cost
#            line_trasnf_num_till_u = line_trans_num_label[v] + e_num_lin_trf
#            mode_transf_num_till_u = mode_trans_num_label[v] + e_num_mode_trf
#            time_till_u = curr_time + e_tt + e_wait_time
#
#            if e_type == 'taxi_edge':
#              vu_dist = weight_label[v] + taxi_attrs_w[0]*e_tt + taxi_attrs_w[1]*e_wait_time + taxi_attrs_w[2]*e_distance + taxi_attrs_w[3]*e_cost + taxi_attrs_w[4]*e_num_lin_trf
#            elif e_type == 'on_demand_single_taxi_edge':
#              vu_dist = weight_label[v] + sms_attrs_w[0]*e_tt + sms_attrs_w[1]*e_wait_time + sms_attrs_w[2]*e_distance + sms_attrs_w[3]*e_cost + sms_attrs_w[4]*e_num_lin_trf
#            elif e_type == 'on_demand_shared_taxi_edge':
#              vu_dist = weight_label[v] + sms_pool_attrs_w[0]*e_tt + sms_pool_attrs_w[1]*e_wait_time + sms_pool_attrs_w[2]*e_distance + sms_pool_attrs_w[3]*e_cost + sms_pool_attrs_w[4]*e_num_lin_trf
#
#          if e_type == 'walk_edge':
#            e_tt = travel_time_data(v, u, e)  # funtion that extracts the edge's in-vehicle travel time attribute
#            if e_tt is None:
#              print('Missing in_veh_tt value in edge {}'.format((v, u)))
#              continue
#            e_wait_time = 0
#            e_distance = distance_data(v, u, e)        # funtion that extracts the edge's distance attribute
#            if e_distance is None:
#              print('Missing distance value in edge {}'.format((v, u)))
#              continue
#            e_cost = 0
#            e_num_mode_trf = 0
#            e_num_lin_trf = 0
#
#            travel_time_till_u = travel_time_label[v] + e_tt
#            wait_time_till_u = wait_time_label[v] + e_wait_time
#            distance_till_u = distance_label[v] + e_distance
#            cost_till_u = mon_cost_label[v] + e_cost
#            line_trasnf_num_till_u = line_trans_num_label[v] + e_num_lin_trf
#            mode_transf_num_till_u = mode_trans_num_label[v] + e_num_mode_trf
#            
#
#            time_till_u = curr_time + e_tt + e_wait_time
#
#            vu_dist = weight_label[v] + walk_attrs_w[0]*e_tt + walk_attrs_w[1]*e_wait_time + walk_attrs_w[2]*e_distance + walk_attrs_w[3]*e_cost + walk_attrs_w[4]*e_num_lin_trf
#          # if e_type == 'orig_dummy_edge':
#          #   road_edge_cost = weight(v, u, G[v][u])
#          #   if road_edge_cost is None:
#          #     continue
#          #   vu_dist = dist[v] + road_edge_cost
#          # if e_type == 'dest_dummy_edge' or e_type == 'dual_edge':
#          #   road_edge_cost = calc_road_link_tt(dist[v], G[v][u])             # the travel time assigned here is the travel time of the corresponding 5min interval based on historic data
#          #   if road_edge_cost is None:
#          #     continue
#          #   vu_dist = dist[v] + road_edge_cost
#          if e_type == 'access_edge':
#            penalty = 0
#            # when we are at an access edge that connects graphs we need to penalize unreasonable connections and path loops; e.g., from walk node to another mode-specific node and back to walk node, from a taxi/carsharing trip to a walk trip and back to taxi/carsharing trip
#            if (pr_md == 'taxi_graph' or pr_md == 'on_demand_single_taxi_graph' or pr_md == 'on_demand_shared_taxi_graph' or pr_md == 'car_sharing_graph') and (G.nodes[u]['node_graph_type'] == 'taxi_graph' or G.nodes[u]['node_graph_type'] == 'on_demand_single_taxi_graph' or G.nodes[u]['node_graph_type'] == 'on_demand_shared_taxi_graph' or G.nodes[u]['node_graph_type'] == 'car_sharing_graph'):
#              penalty = math.inf
#            if pr_ed_tp == 'access_edge':
#              if (pre_upstr_n_gr_tp == 'Walk' and G.nodes[u]['node_graph_type'] == 'Walk') or (pre_upstr_n_gr_tp == 'Bus' and G.nodes[u]['node_graph_type'] == 'Bus') or (pre_upstr_n_gr_tp == 'Train' and G.nodes[u]['node_graph_type'] == 'Tain'):
#                penalty = math.inf
#            if G.nodes[u]['node_type'] == 'car_sharing_station_node':
#              if G.nodes[u]['stock_level'] == 0:
#                penalty = math.inf
#            if G.nodes[v]['node_type'] == 'car_sharing_station_node':
#              if G.nodes[v]['stock_level'] == G.nodes[v]['capacity']:
#                penalty = math.inf
#            # restraint pick up and drop off
#            if G.nodes[v]['node_graph_type'] == 'Walk' and (G.nodes[u]['node_graph_type'] == 'taxi_graph' or G.nodes[u]['node_graph_type'] == 'on_demand_single_taxi_graph' or G.nodes[u]['node_graph_type'] == 'on_demand_shared_taxi_graph'):
#              if G.nodes[orig_source]['node_graph_type'] == 'Walk' and v != orig_source and pr_md==None:
#                  penalty = math.inf
#            if G.nodes[u]['node_graph_type'] == 'Walk' and (G.nodes[v]['node_graph_type'] == 'taxi_graph' or G.nodes[v]['node_graph_type'] == 'on_demand_single_taxi_graph' or G.nodes[v]['node_graph_type'] == 'on_demand_shared_taxi_graph'):
#              if G.nodes[u]['zone'] == G.nodes[target]['zone'] and u != target:
#                penalty = math.inf
#
#            e_tt = 0
#            e_wait_time = 0
#            e_distance = 0
#            e_cost = 0
#            e_num_mode_trf = 0
#            e_num_lin_trf = 0
#            
#            # from mode and line transfers we store the previous path mode (not considering walk as a mode) and if a path with a new mode starts then we have a mode transfer, if with the same mode then a line transfer
#            if G.nodes[v]['node_graph_type'] == 'Walk':
#              if pr_md != None and G.nodes[u]['node_graph_type'] != pr_md:
#                e_num_mode_trf = 1
#                e_num_lin_trf = 0
#              elif (pr_md =='Train' or pr_md =='Bus') and G.nodes[u]['node_graph_type'] == pr_md:
#                e_num_mode_trf = 0
#                e_num_lin_trf = 1
#            if G.nodes[u]['node_graph_type'] == 'Walk':
#              prev_mode = G.nodes[v]['node_graph_type']
#
#            # # following two conditions are just because we lack proper walk graph representation in VC
#            # if G.nodes[v]['node_graph_type'] == 'Bus' and G.nodes[u]['node_graph_type'] == 'Train':
#            #   e_num_mode_trf = 1
#            #   e_num_lin_trf = 0
#            #   prev_mode = G.nodes[v]['node_graph_type']
#            # if G.nodes[u]['node_graph_type'] == 'Bus' and G.nodes[v]['node_graph_type'] == 'Train':
#            #   e_num_mode_trf = 1
#            #   e_num_lin_trf = 0
#            #   prev_mode = G.nodes[v]['node_graph_type']
#
#            time_till_u = curr_time + e_tt + e_wait_time
#
#            travel_time_till_u = travel_time_label[v] + e_tt
#            wait_time_till_u = wait_time_label[v] + e_wait_time
#            distance_till_u = distance_label[v] + e_distance
#            cost_till_u = mon_cost_label[v] + e_cost
#            line_trasnf_num_till_u = line_trans_num_label[v] + e_num_lin_trf
#            mode_transf_num_till_u = mode_trans_num_label[v] + e_num_mode_trf
#
#            vu_dist = weight_label[v] + bus_attrs_w[4]*e_num_lin_trf + mode_transfer_weight*e_num_mode_trf + penalty
#          # cost calculation process for a transfer edge in bus or train stops/stations
#
#          if e_type == 'pt_transfer_edge':
#            # for zone_to_zone pt fare scheme we store the zone of the stop/station in which a pt trip started (origin); this zone will be used for the calculcation of the edge cost based on which pt stop the algorithm checks and hence the final stop of the pt trip
#            if fare_scheme == 'zone_to_zone':
#              if pr_ed_tp == 'access_edge':
#                if pr_md != 'Bus' and pr_md != 'Train':
#                  zone_at_start_of_pt_trip = G.nodes[v]['zone']
#                  previous_edge_cost = 0
#            e_tt = travel_time_data(v, u, e)  # funtion that extracts the edge's in-vehicle travel time attribute
#            if e_tt is None:
#              print('Missing in_veh_tt value in edge {}'.format((v, u)))
#              continue
#            e_wait_time = 0
#            e_distance = distance_data(v, u, e)        # funtion that extracts the edge's distance attribute
#            if e_distance is None:
#              print('Missing distance value in edge {}'.format((v, u)))
#              continue
#            e_num_mode_trf = 0
#            # to cmpute line transfers in pt we check the previous edge type; if the previous edge type is also a tranfer edge then we have a line transfer; this constraint allows us to avoid adding a line transfer when the algorithm traverses a transfer edge at the start of a pt trip
#            if pr_ed_tp == 'pt_transfer_edge':
#              e_num_lin_trf = 1
#            else:
#              e_num_lin_trf = 0
#
#            e_cost = 0
#
#            time_till_u = curr_time + e_tt + e_wait_time
#
#            travel_time_till_u = travel_time_label[v] + e_tt
#            wait_time_till_u = wait_time_label[v] + e_wait_time
#            distance_till_u = distance_label[v] + e_distance
#            cost_till_u = mon_cost_label[v] + e_cost
#            line_trasnf_num_till_u = line_trans_num_label[v] + e_num_lin_trf
#            mode_transf_num_till_u = mode_trans_num_label[v] + e_num_mode_trf
#
#            if G.nodes[u]['node_graph_type'] == 'Bus' and G.nodes[v]['node_graph_type'] == 'Bus':
#              vu_dist = weight_label[v] + bus_attrs_w[0]*e_tt + bus_attrs_w[1]*e_wait_time + bus_attrs_w[2]*e_distance + bus_attrs_w[3]*e_cost + bus_attrs_w[4]*e_num_lin_trf
#            else:
#              vu_dist = weight_label[v] + train_attrs_w[0]*e_tt + train_attrs_w[1]*e_wait_time + train_attrs_w[2]*e_distance + train_attrs_w[3]*e_cost + train_attrs_w[4]*e_num_lin_trf
#
#          # cost calculation process for a pt route edge in bus or train stops/stations
#          if e_type == 'pt_route_edge':
#            # for pt route edges the waiting time and travel time is calculated differently; based on the time-dependent model and the FIFO assumption, if the type of previous edge is transfer edge, we assume that the fastest trip will be the one with the first departing bus/train after the current time (less waiting time) and the travel time will be the one of the corresponding pt vehicle run_id; but if the type of the previous edge is a route edge, then for this line/route a pt_vehcile has already been chosen and the edge travel time will be the one for this specific vehicle of the train/bus line (in this case the wait time is 0)
#
#            if pr_ed_tp == 'pt_transfer_edge':
#              dep_timetable = timetable_data(v, u, e)  # fuction that extracts the stop's/station's timetable dict
#              if dep_timetable is None:
#                print('Missing timetable value in edge'.format((v, u)))
#                continue
#              e_wait_time, pt_vehicle_run_id = calc_plat_wait_time_and_train_id(curr_time, dep_timetable)  # function that extracts waiting time for next pt vehicle and the vehicle_id; the next departing vehicle is being found using a binary search algorithm that operates on a sorted list of the deparure times for this edge (departure times of the downstream stop/station)
#              if e_wait_time is None:
#                print('Missing wait_time value in edge'.format((v, u)))
#                continue
#              tt_d = travel_time_data(v, u, e)  # fuction that extracts the travel time dict
#              if tt_d is None:
#                print('Missing in_veh_tt value in edge'.format((v, u)))
#                continue
#              e_tt = tt_d[pt_vehicle_run_id] #calc_pt_route_edge_in_veh_tt_for_run_id(tt_d, pt_vehicle_run_id)  # fuction that travel time for corresponding pt vehicle run_id
#            elif pr_ed_tp == 'pt_route_edge':
#              e_wait_time = 0
#              pt_vehicle_run_id = lt_run_id
#              e_tt = e['departure_time'][pt_vehicle_run_id] - curr_time + e['travel_time'][pt_vehicle_run_id]  # the subtraction fo the first two terms is the dwell time in the downstream station and the 3rd term is the travel time of the pt vehicle run_id that has been selected for the previous route edge
#              if e_tt is None:
#                print('Missing in_veh_tt value in edge'.format((v, u)))
#                continue
#            e_distance = distance_data(v, u, e)  # fuction that extracts the travel time dict
#            if e_distance is None:
#              print('Missing distance value in edge'.format((v, u)))
#              continue
#            # edge costs for pt depend on the pt fare scheme; if it is additive (distance_based) or zone_to_zone !! consider adding a price cap !!
#            if fare_scheme == 'distance_based':
#              dist_bas_cost = pt_additive_cost_data(v, u, e)  # fuction that extracts the time-dependent distance-based cost dict
#              if dist_bas_cost is None:
#                print('Missing dist_bas_cost value in edge'.format((v, u)))
#                continue
#              e_cost = calc_time_dep_distance_based_cost(dist_bas_cost, curr_time)  # fuction that extracts the cost based on time-dependent distance-based cost dict and the current time (finds in which time-zone we currently are)
#              cost_till_u = mon_cost_label[v] + e_cost #- pr_e_cost
#            elif fare_scheme == 'zone_to_zone':
#              zn_to_zn_cost = pt_non_additive_cost_data(v, u, e)  # fuction that extracts the time-dependent zone_to_zone cost dict
#              if zn_to_zn_cost is None:
#                print('Missing zn_to_zn_cost value in edge'.format((v, u)))
#                continue
#              pt_cur_cost = calc_time_dep_zone_to_zone_cost(zn_to_zn_cost, curr_time, pt_tr_st_z, G.nodes[u]['zone'])  # function that extracts the cost of the edge based on the zone at the start of the pt trip, the zone of current stop/station and the current time we are in
##              if pt_cur_cost == None or pr_e_cost == None:
##                  print('stop')
#              if pt_cur_cost < pr_e_cost:
#                e_cost = 0
#                previous_edge_cost = pr_e_cost
#              else:
#                e_cost = pt_cur_cost - pr_e_cost
#                previous_edge_cost = pt_cur_cost  # here only for the case of zone_to_zone pt fare schemes we update the previous edge cost only after the label (edge weight) calculation
#              # if pt_cur_cost<pr_e_cost:
#              #   print('Previous cost is higher than new cost in {}'.format(paths[v]))
#            e_num_lin_trf = 0
#            e_num_mode_trf = 0
#
#            time_till_u = curr_time + e_tt + e_wait_time
#
#            travel_time_till_u = travel_time_label[v] + e_tt
#            wait_time_till_u = wait_time_label[v] + e_wait_time
#            distance_till_u = distance_label[v] + e_distance
#            cost_till_u = mon_cost_label[v] + e_cost
#            line_trasnf_num_till_u = line_trans_num_label[v] + e_num_lin_trf
#            mode_transf_num_till_u = mode_trans_num_label[v] + e_num_mode_trf
#
#            if G.nodes[u]['node_graph_type'] == 'Bus' and G.nodes[v]['node_graph_type'] == 'Bus':
#              vu_dist = weight_label[v] + bus_attrs_w[0]*e_tt + bus_attrs_w[1]*e_wait_time + bus_attrs_w[2]*e_distance + bus_attrs_w[3]*e_cost + bus_attrs_w[4]*e_num_lin_trf
#            else:
#              vu_dist = weight_label[v] + train_attrs_w[0]*e_tt + train_attrs_w[1]*e_wait_time + train_attrs_w[2]*e_distance + train_attrs_w[3]*e_cost + train_attrs_w[4]*e_num_lin_trf
#
#
#          if u in weight_label:
#            if vu_dist < weight_label[u]:
#              # print(weight_label, weight_label[u], paths[v])
#              print('Negative weight in node {}, in edge {}, {}?'.format(u, v, u))
#              raise ValueError('Contradictory paths found:',
#                               'negative weights?')
#          elif u not in seen or vu_dist < seen[u]:
#            seen[u] = vu_dist
#            if e_type == 'pt_route_edge' and pr_ed_tp != 'pt_route_edge':
#              push(fringe, (vu_dist, next(c), u, travel_time_till_u, wait_time_till_u, distance_till_u, cost_till_u, line_trasnf_num_till_u, mode_transf_num_till_u, e_type, n_gr_type, pt_vehicle_run_id, time_till_u, previous_edge_cost, zone_at_start_of_pt_trip, prev_mode))
#            elif e_type == 'pt_route_edge' and pr_ed_tp == 'pt_route_edge':
#              push(fringe, (vu_dist, next(c), u, travel_time_till_u, wait_time_till_u, distance_till_u, cost_till_u, line_trasnf_num_till_u, mode_transf_num_till_u, e_type, n_gr_type, pt_vehicle_run_id, time_till_u, previous_edge_cost, zone_at_start_of_pt_trip, prev_mode))
#            elif e_type == 'pt_transfer_edge':
#              push(fringe, (vu_dist, next(c), u, travel_time_till_u, wait_time_till_u, distance_till_u, cost_till_u, line_trasnf_num_till_u, mode_transf_num_till_u, e_type, n_gr_type, None, time_till_u, previous_edge_cost, zone_at_start_of_pt_trip, prev_mode))
#            elif e_type != 'pt_route_edge' and e_type != 'pt_transfer_edge':
#              push(fringe, (vu_dist, next(c), u, travel_time_till_u, wait_time_till_u, distance_till_u, cost_till_u, line_trasnf_num_till_u, mode_transf_num_till_u, e_type, n_gr_type, None, time_till_u, previous_edge_cost, zone_at_start_of_pt_trip, prev_mode))
#            if paths is not None:
#              paths[u] = paths[v] + [u]
#            if pred is not None:
#              pred[u] = [v]
#          elif vu_dist == seen[u]:
#            if pred is not None:
#              pred[u].append(v)
#
#        # The optional predecessor and path dictionaries can be accessed
#        # by the caller via the pred and paths objects passed as arguments.
#
#    try:
#        return (weight_label[target], paths[target], travel_time_label[target], wait_time_label[target], distance_label[target], mon_cost_label[target], line_trans_num_label[target], mode_trans_num_label[target], travel_time_label, wait_time_label, distance_label, mon_cost_label, line_trans_num_label, mode_trans_num_label, weight_label, prev_edge_type_label, prev_upstr_node_graph_type_label, last_pt_veh_run_id_label, current_time_label, prev_edge_cost_label, pt_trip_start_zone_label, prev_mode_label)
#    except KeyError:
#        raise nx.NetworkXNoPath("Node %s not reachable from %s" % (target, source))
#
