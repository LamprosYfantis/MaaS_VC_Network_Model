# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 17:07:45 2019

@author: Francisco
"""

def import_data(nodes,b,c):
    a = dict(pd.read_csv('Road_nodes_coord.csv', delimiter=',', index_col=False)) ## Importing node data
    return(a)
    
