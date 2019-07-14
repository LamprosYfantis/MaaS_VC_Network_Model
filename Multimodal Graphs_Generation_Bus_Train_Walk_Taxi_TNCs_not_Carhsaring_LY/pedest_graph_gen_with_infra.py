import csv
import math
import time
import networkx as nx
import pandas as pd
import numpy as np
from numpy.linalg import norm
from shapely.geometry import Point, LineString
from networkx.classes.function import number_of_edges, number_of_nodes
from pedest_graph_gen_with_infra_funct import gen_walk_graph_nodes_with_infra, gen_walk_graph_edges_with_attrs, find_proj


ped_graph = nx.DiGraph()

gen_walk_graph_nodes_with_infra(ped_graph)
print(ped_graph.number_of_nodes())
gen_walk_graph_edges_with_attrs(ped_graph)
print(ped_graph.number_of_nodes())
# print(ped_graph.is_directed())
# for e in ped_graph.edges:
#     if ped_graph[e[0]][e[1]]['distance'] < 0:
#         print('oops', e)
# for n in ped_graph:
#     print(n)
print(ped_graph.nodes['w60']['zone'])
