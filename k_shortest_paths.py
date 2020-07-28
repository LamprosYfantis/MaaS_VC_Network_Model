# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 15:55:07 2019

@author: Francisco
"""

from itertools import islice
import networkx as nx

def k_shortest_paths(G, source, target, k, weight='weight'):
    return list(islice(nx.shortest_simple_paths(G, source, target, weight='weight'), k))

