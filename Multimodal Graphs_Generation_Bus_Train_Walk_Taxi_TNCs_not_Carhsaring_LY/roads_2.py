# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 14:29:06 2019

@author: Francisco
"""


##%matplotlib qt
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from k_shortest_paths import k_shortest_paths
from PathTT import PathTT

## 1.IMPORTING THE DATA

nodes = pd.read_csv('Road_nodes_coord.csv', delimiter=',', index_col=False) ## Importing node data
nodes_d=nodes.to_dict() # Converting into dict

l = pd.read_csv('Road_links.csv', delimiter=',', usecols=[0,3,4], index_col=False) ## Importing links data
l_tt = pd.read_csv('Road_links_default_travel_times.csv', delimiter=',', usecols=[4,4], index_col=False) ## Importing default travel times per link
l=l.assign(weight=l_tt) ## Adding the travel times to the links data
l_length=turning= pd.read_csv('links_length.csv', usecols=[2,2], delimiter=',', index_col=False)## Importing distances (length) per link
l=l.assign(length=l_length) ## Adding the distances to the links data
l=l.round({'weight':3, 'length':3}) ## Round to 3 decimals
links_dict=l.to_dict()# Converting into dict

turning=pd.read_csv('Road_turning_groups.csv', delimiter=',', usecols=[2,3], index_col=False)  ## Importing turning groups data (from link to link)
turning_d=turning.to_dict()# Converting into dict


## 2. BUILDING THE ORIGINAL GRAPH (G)

G=nx.MultiDiGraph()

##Adding the nodes with coordinates
for i in range(len(nodes_d['id'])):
    G.add_node(nodes_d['id'][i], pos=(nodes_d['x'][i],nodes_d['y'][i]))

##Adding the edges with the id, travel time and length
for i in range(len(links_dict['id'])):
    G.add_edge(links_dict['from_node'][i],links_dict['to_node'][i], id= links_dict['id'][i],dist=links_dict['length'][i],weight=links_dict['weight'][i])
    

pos=nx.get_node_attributes(G,'pos')  #Storing the nodes location
nx.draw(G,pos, with_labels=True) # Graph with node attributes
nx.draw_networkx_edge_labels(G,pos) ## Graph with edge attributes
plt.show() 

unique_g=np.unique(list(dict.values(links_dict['id'])))
##%matplotlib qt
G.number_of_nodes() ## nodes = 95
G.number_of_edges()## edges = 254


## 3. BUILDING THE DUAL GRAPH (H)
H=nx.DiGraph() 

## adding the links of G as nodes of H
for i in range(len(links_dict['id'])): 
    H.add_node(links_dict['id'][i])
      
## Adding the nodes of G as H dummy nodes for origin and destination    
## Getting the unique values of origin nodes
unique_o=np.unique(list(dict.values(links_dict['from_node'])))
unique_d=np.unique(list(dict.values(links_dict['to_node'])))


## Adding the label 'o' to the from_nodes
for i in range (len(links_dict['from_node'])):
    for j in range (len(unique_o)):
        if unique_o[j]==links_dict['from_node'][i]:
               links_dict['from_node'][i]=str(links_dict['from_node'][i])+'o'

## Adding the label 'd' to the to_nodes
for i in range (len(links_dict['to_node'])):
    for j in range (len(unique_d)):
        if unique_d[j]==links_dict['to_node'][i]:
               links_dict['to_node'][i]=str(links_dict['to_node'][i])+'d'

## Adding the from_node and to_nodes as H nodes
for i in range (len(links_dict['from_node'])):
    H.add_node(links_dict['from_node'][i])
    H.add_node(links_dict['to_node'][i])


 ## Adding the edges that links the dummy origins with the H  nodes (G edges)
for i in range (len(links_dict['from_node'])):  
    H.add_edge(links_dict['from_node'][i], links_dict['id'][i], weight=0)

## Adding the edges that links the the H  nodes (G edges) with the dummy destinations with the weight of the preceding G link (node in our case) 
for i in range (len(links_dict['to_node'])):  
    H.add_edge(links_dict['id'][i], links_dict['to_node'][i], weight=links_dict['weight'][i])
    
                    
## Adding the edges that link the nodes (G links) with the weight of the preceding G link (node in our case)         
for i in range(len(turning_d['from_link'])):
    for j in range(len(links_dict['id'])):
            if turning_d['from_link'][i]==links_dict['id'][j]:
                H.add_edge(turning_d['from_link'][i],turning_d['to_link'][i], weight=links_dict['weight'][j]) 
                
print(G.number_of_nodes()) ## nodes = 95
print(G.number_of_edges()) ## edges = 254

print(H.number_of_nodes()) ## nodes = 444
print(H.number_of_edges()) ## edges = 1029                
                    
    
print(nx.shortest_path(G,80,79, method='dijkstra', weight='weight'))##[96, 98, 85, 84, 83, 102, 6]
print(nx.dijkstra_path_length(G,80,79)) ##♠221.6125

print(nx.shortest_path(H, '80o', '79d', method='dijkstra', weight='weight')) ##  ['96o', 252, 168, 195, 199, 202, 164, '6d']
print(nx.dijkstra_path_length(H,'80o', '79d')) ## 221.6125

a=nx.shortest_path(H, '80o', '79d', method='dijkstra', weight='weight')



PathTT((nx.shortest_path(H, '80o', '79d', method='dijkstra', weight='weight')),links_dict)   
### displaying the length and travel time of the shortest path

PathTT(nx.shortest_path(H, '80o', '79d', method='dijkstra', weight='weight'),links_dict)   

for i in range(len(k_shortest_paths(H, '75o', '79d', 5,weight='weight'))):
    PathTT(k_shortest_paths(H, '75o', '79d', 5,weight='weight')[i],links_dict) 
    
       
## K shortest path

for path in k_shortest_paths(H, '80o', '79d', 5,weight='weight'):
    print(path)

a=k_shortest_paths(H, '80o', '79d', 5,weight='weight')




