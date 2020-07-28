# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 10:27:40 2019

@author: Francisco
"""

##Determining links length
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import math


links_p = pd.read_csv('Road_links_polyline.csv', delimiter=',', index_col=False)
links_p= links_p.sort_values(['id','seq_id'])
v=links_p['id'].unique()

links_lengths=pd.DataFrame(columns=['id', 'length'])

for i in range(len(v)):
    links_segments=pd.DataFrame(columns=['seq_id','x', 'y'])
    o=0
    for j in range(o,len(links_p)):
        if v[i] == links_p.id[j]:
            coor = pd.DataFrame([[links_p.seq_id[j],links_p.x[j],links_p.y[j]]],columns=['seq_id','x', 'y'])
            links_segments=links_segments.append(coor, ignore_index=True)
            o=0
            u=len(links_segments)
            o=u+o
      
    d=0
    for c in range(len(links_segments)-1):
        a=math.sqrt((links_segments.x[c+1]-links_segments.x[c])**2+(links_segments.y[c+1]-links_segments.y[c])**2)
        d=a+d
        m = pd.DataFrame([[i+1,d]],columns=['id', 'length'])
    links_lengths=links_lengths.append(m, ignore_index=True)    

links_lengths.to_csv('links_length.csv')
