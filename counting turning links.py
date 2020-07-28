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

t = pd.read_csv('Road_turning_groups.csv', delimiter=',', usecols=[0,1,2, 3], index_col=False)
v=t['from_link'].unique()
b=pd.DataFrame()
c=pd.DataFrame()
for j in range (len(v)):
    a=0
    for i in range(len(t)):
        if v[j]==t.from_link[i]:
            a=a+1
        
    b=pd.DataFrame([[v[j],a]])
    c=c.append(b)
    
v=t['to_link'].unique()     
d=pd.DataFrame()
e=pd.DataFrame()
for j in range (len(v)):
    a=0
    for i in range(len(t)):
        if v[j]==t.to_link[i]:
            a=a+1
        
    d=pd.DataFrame([[v[j],a]])
    e=e.append(d) 
    
c.sum(axis=0, skipna=True)
e.sum(axis=0, skipna=True)

s=t['node_id'].unique() 
r=pd.DataFrame()
u=pd.DataFrame()
for j in range (len(s)):
    a=0
    for i in range(len(t)):
        if s[j]==t.node_id[i]:
            a=a+1
        
    r=pd.DataFrame([[s[j],a]])
    u=u.append(r) 
     