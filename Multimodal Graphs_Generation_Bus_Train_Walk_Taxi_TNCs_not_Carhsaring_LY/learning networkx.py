# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 14:43:01 2019

@author: Francisco
"""
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import approximation as approx


links = pd.read_csv('test links.csv', delimiter=',', index_col=False)
l= pd.read_csv('test links.csv', delimiter=',', usecols=[1,2], index_col=False)
turning= pd.read_csv('turning_groups.csv', delimiter=',', index_col=False)
links_dict=links.to_dict()
l_length=turning= pd.read_csv('links_length.csv', usecols=[1,2], delimiter=',', index_col=False)


G=nx.DiGraph() ### crea un grafo vacio

link_id=links['id'].tolist()
l_from_to=l.values.tolist()
weight=links['weight'].tolist()
H_from_to=turning.values.tolist()
H_from=turning['from_link'].values.tolist()
H_to=turning['to_link'].values.tolist()

G.add_node(1, pos=(0,1))
G.add_node(2, pos=(1,1))
G.add_node(3, pos=(1,0))
G.add_node(4, pos=(0,0))


i=0
for i in range(len(links)):
    G.add_edge(*l_from_to[i], id=link_id[i], dist=l_length[i], weight=weight[i],)
    i=i+1
    
    
H=nx.DiGraph() ## building the dual graph

## adding the links of G as nodes of H
for i in range(len(link_id)): 
    H.add_node(link_id[i])
      
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
for i in range(len(H_from_to)):
    for j in range(len(links.id)):
            if H_from_to[i][0]==links.id[j]:
                H.add_edge(*H_from_to[i], weight=weight[j]) 
                
print(G.number_of_nodes()) ## nodes = 4
print(G.number_of_edges()) ## edges = 9

print(H.number_of_nodes()) ## nodes = 17
print(H.number_of_edges()) ## edges = 30                
                    


print(nx.shortest_path(G, 1, 4, method='dijkstra', weight='weight'))
print(nx.dijkstra_path_length(G,1,4))

print(nx.shortest_path(H, '1o', '4d', method='dijkstra', weight='weight'))
print(nx.dijkstra_path_length(H,'1o','4d'))

H.remove_edge('A','E') ## removing edges


## just bullshit


    
nx.shortest_path(G, 1, 4, method='dijkstra', weight='weight')
nx.dijkstra_path_length(G,1,4)

nx.shortest_path(H, 'A', 'B', method='dijkstra', weight='weight')
nx.dijkstra_path_length(H,'A','B')
nx.shortest_path(H, 'A', 'E', method='dijkstra', weight='weight')
nx.dijkstra_path_length(H,'A','E')
nx.shortest_path(H, 'A', 'G', method='dijkstra', weight='weight')
nx.dijkstra_path_length(H,'A','G')

nx.shortest_path(H, 'B', 'B', method='dijkstra', weight='weight')
nx.dijkstra_path_length(H,'B','B')
nx.shortest_path(H, 'B', 'E', method='dijkstra', weight='weight')
nx.dijkstra_path_length(H,'B','E')
nx.shortest_path(H, 'B', 'G', method='dijkstra', weight='weight')
nx.dijkstra_path_length(H,'B','G')

H.remove_edge('A','E') ## removing edges
H.number_of_edges()

H.node['B']['weight']=100

nx.shortest_path(H, 'A', 'B', method='dijkstra', weight='weight')
nx.dijkstra_path_length(H,'A','B')
nx.shortest_path(H, 'A', 'E', method='dijkstra', weight='weight')
nx.dijkstra_path_length(H,'A','E')
nx.shortest_path(H, 'A', 'G', method='dijkstra', weight='weight')
nx.dijkstra_path_length(H,'A','G')

nx.shortest_path(H, 'B', 'B', method='dijkstra', weight='weight')
nx.dijkstra_path_length(H,'B','B')
nx.shortest_path(H, 'B', 'E', method='dijkstra', weight='weight')
nx.dijkstra_path_length(H,'B','E')
nx.shortest_path(H, 'B', 'G', method='dijkstra', weight='weight')
nx.dijkstra_path_length(H,'B','G')


G.number_of_nodes() ## nodes = 4
G.number_of_edges() ## edges = 9

H.number_of_nodes() ## nodes = 9
H.number_of_edges() ## edges = 11


   



    
G.add_node(1, pos=(0,1))
G.add_node(2, pos=(1,1))
G.add_node(3, pos=(1,0))
G.add_node(4, pos=(0,0))

G.add_weighted_edges_from([(1,2,30),(1,4,45),(2,1,45),(2,3,30),(2,4,5),(3,2,45),(3,4,30),(4,1,30),(4,3,45)])


pos=nx.get_node_attributes(G,'pos')
nx.draw(G,pos, with_labels=True)

nx.draw_networkx_edge_labels(G,pos)

plt.show() 

for path in nx.all_simple_paths(G,source=3,target=1): ## shows all the path between 3 and 1
    print(path)
 
paths= nx.all_simple_paths(G, source=3, target=1) ## shows all the path between 3 and 1 per edges
for path in map(nx.utils.pairwise, paths):
    print(list(path))
    
nx.shortest_path(G, 3, 1, method='dijkstra', weight='weight')
nx.shortest_path(G, 1, 3, method='dijkstra', weight='weight')
nx.shortest_path_length(G,3,1,weight='weight')
nx.average_shortest_path_length(G, weight='weight')

G[4][1]['weight']
G.add_node(1) ### adding a node with name = 1

G.add_nodes_from([2,3]) ### adding two nodes, 2 and 3

H=nx.path_graph(10) ### creates a graph composed of subsuquents nodes and egdes forming a path from the 
                    ### origin to the destination



G.add_node(H) ### add H as a node of G

H.nodes() ## shows the nodes of H
G.add_nodes_from(H) ## add the nodes of H as nodes of G. 



G.remove_node(H) ### removes node H

G.nodes() # shows all the nodes of G


G.add_edge(1,2) ## adds and edge between nodes 1 and 2

e=(2,3) 

G.add_edge(*e)## add a new edge between 2 and 3

G.add_edges_from([(1,2),(1,3)]) ## add a list of edges


G.add_edges_from(H.edges)## add the edges of H as edges of G



G.clear() ### Remove all nodes and edges

G.add_edges_from([(1,2),(1,3)]) ### Add edges between 1-2 and 1-3. 
                                ### At the same time creates the nodes 1,2,3 if they havent been declared yet
G.add_node(1) ### add node 1. Redundant

G.add_edge(1,2) ### add edge 1-2. Redundant

G.add_node("spam") ### Add a node called spam

G.add_nodes_from("spam") ### Add 4 nodes called s,p,a and m

G.add_edge(3,'m') ### Creates a Link between 3 and m

G.degree()

G.edges([2,'m']) # Gives information about the edges incident in this subset of nodes

G.degree([2,3]) # Gives the number of edGes incident to these subset of nodes

G.remove_node(2) ### remove the node 2

G.remove_nodes_from("spam") ### removes the nodes s, p, a and m

a=list(G.nodes)

G.remove_edge(1,3)

b=list(G.edges)

G.add_edge(1,2)

H=nx.DiGraph(G)
list(H.edges())
H.nodes()
edgelist=[(0,1),(1,2),(2,3)]
H=nx.Graph(edgelist)
H.nodes()
H.edges()

FG=nx.Graph()
FG.add_weighted_edges_from([(1,2,0.125), (1,3,0.75), (2,4,1.2), (3,4,0.375)])

for (u, v, wt) in FG.edges.data('weight'):
       print('(%d, %d, %.3f)' % (u, v, wt))
       
G=nx.Graph(day="Friday")

G.add_node(1,time='5pm')

G.add_nodes_from([3],time='2pm')
G.nodes[1]['room']=714


DG=nx.DiGraph()
DG.add_weighted_edges_from([(1,2,0.5), (3,1,0.75)])
DG.edges()
DG.nodes()
list(DG.successors(1))
list(DG.successors(3))

G=nx.petersen_graph()
plt.subplot(121)
nx.draw(G, with_labels=True, font_weight='bold')
plt.subplot(122)
nx.draw_shell(G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
plt.show()
      