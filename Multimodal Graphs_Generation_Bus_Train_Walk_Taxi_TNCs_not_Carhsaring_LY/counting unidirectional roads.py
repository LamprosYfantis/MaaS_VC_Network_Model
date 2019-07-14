# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 17:10:53 2019

@author: Francisco
"""


##%matplotlib qt
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import approximation as approx

l = pd.read_csv('Road_links.csv', delimiter=',', usecols=[0,3,4], index_col=False)
l=l.sort_values(['from_node','to_node'])
l=l.reset_index()

l_prima = l[['id','to_node','from_node']]
l_prima= l_prima.sort_values(['to_node','from_node' ])
l_prima=l_prima.reset_index()
v=l['from_node'].unique()
v.sort()
b=pd.DataFrame(columns=['node_id','outgoing'])
c=pd.DataFrame(columns=['node_id','outgoing'])
for j in range (len(v)):
    a=0
    for i in range(len(l)):
        if v[j]==l.from_node[i]:
            a=a+1
        
    b=pd.DataFrame([[v[j],a]],columns=['node_id','outgoing'])
    c=c.append(b, ignore_index=True)
    
v=l['to_node'].unique()   
v.sort()  
d=pd.DataFrame(columns=['node_id','incoming'])
e=pd.DataFrame(columns=['node_id','incoming'])
for j in range (len(v)):
    a=0
    for i in range(len(l)):
        if v[j]==l.to_node[i]:
            a=a+1
        
    d=pd.DataFrame([[v[j],a]],columns=['node_id','incoming'])
    e=e.append(d, ignore_index=True) 
     
a=0  
for i in range(len(c)):
    if c['outgoing'][i]==e['incoming'][i]:
        a=a+11

a=0


for i in range(len(l)):
    for j in range(len(l_prima)):
        if l['from_node'][i]==l_prima['to_node'][j] and l['to_node'][i]==l_prima['from_node'][j]:
            a=a+1
        else:
            print(l['from_node'][i],l['to_node'][i])
            print(l_prima['from_node'][j], l_prima['to_node'][j])
            
            
l.isin([l_prima['from_node'][j], l_prima['to_node'][j]])
    
     