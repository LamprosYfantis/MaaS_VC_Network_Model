# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 09:26:47 2019

@author: Francisco
"""


import pandas as pd

def import_data():
    a = dict(pd.read_csv('Road_nodes_coord.csv', delimiter=',', index_col=False))## Importing nodes data
    l = pd.read_csv('Road_links.csv', delimiter=',', usecols=[0,3,4], index_col=False) ## Importing links data
    l_length= pd.read_csv('links_length.csv', usecols=[2,2], delimiter=',', index_col=False)## Importing distances (length) per link
    l=l.assign(length=l_length) ## Adding the distances to the links data
    l=l.round({'weight':3, 'length':3}) ## Round to 3 decimals
    b=l.to_dict()# Converting into dict
    c=pd.read_csv('Road_turning_groups.csv', delimiter=',', usecols=[2,3], index_col=False)  ## Importing turning groups data (from link to link)
    c=c.to_dict()# Converting into dict
    return(a,b,c)
    

def add_nodes(a):
    for i in range(len(a['id'])):
        G.add_node(a['id'][i], pos=(a['x'][i],a['y'][i]))
        return(G)
    






 

def PathTT(x,links_dict):
    d=0 ## seconds
    m=0 ## minutes
    h=0 ## hours
    s=0 ## length
    for i in range(1,len(x)-1):
        for j in range(len(links_dict['id'])):
            if x[i]==links_dict['id'][j]:
                u=links_dict['weight'][j]
                v=links_dict['length'][j]
                d=u+d
                s=v+s
    ##Printing the path
    print()
    print('Path: %s' %x) 
    
    ##Printing the length 
    if s>1000:
        s=s/1000
        print('Length = %.2f km' %s)
    else: 
        print('Length = %.2f m' %s)
        
    ##Printing the travel time
    if d>60:
        m=m+d//60
        d=d-60*m
        print('Travel time = %.f m %.2f s' %(m,d))
    else:
        print('Travel time = %.2f s' %d)
  
        
    
    
            