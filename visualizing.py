# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 17:33:35 2019

@author: Francisco
"""
##%matplotlib qt
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import math
import pylab as P


# Draw multiple points.


nodes = pd.read_csv('Road_nodes_coord.csv', delimiter=',', index_col=False) ## Importing node data
nodes_d=nodes.to_dict() # Converting into dict

l = pd.read_csv('Road_links.csv', delimiter=',', usecols=[0,3,4], index_col=False) ## Importing links data
l_tt = pd.read_csv('Road_links_default_travel_times.csv', delimiter=',', usecols=[4,4], index_col=False) ## Importing default travel times per link
l=l.assign(weight=l_tt) ## Adding the travel times to the links data
l_length=turning= pd.read_csv('links_length.csv', usecols=[2,2], delimiter=',', index_col=False)## Importing distances (length) per link
l=l.assign(length=l_length) ## Adding the distances to the links data
l=l.round({'weight':3, 'length':3}) ## Round to 3 decimals
links_dict=l.to_dict()# Converting into dict


x_number_list = nodes.x

    # y axis value list.
y_number_list = nodes.y

labels=  nodes.id
    # Draw point based on above x, y axis values.
plt.scatter(x_number_list, y_number_list, s=50, marker = 'o')
for label, x, y in zip(labels, x_number_list ,  y_number_list ):
    plt.annotate(
                label,
                xy=(x, y), xytext=(-15, 15),
                textcoords='offset points', ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.1', fc='yellow', alpha=0.1),
       )


links_p = pd.read_csv('Road_links_polyline.csv', delimiter=',', index_col=False)
links_p= links_p.sort_values(['id','seq_id'])
v=links_p['id'].unique()

links_lengths=pd.DataFrame(columns=['id', 'length'])
for i in range(len(v)):
    links_segments=pd.DataFrame(columns=['id','seq_id','x', 'y'])
    o=0
    for j in range(o,len(links_p)):
        if v[i] == links_p.id[j]:
            coor = pd.DataFrame([[links_p.id[j], links_p.seq_id[j],links_p.x[j],links_p.y[j]]],columns=['id','seq_id','x', 'y'])
            links_segments=links_segments.append(coor, ignore_index=True)
            o=0
            u=len(links_segments)
            o=u+o
    
    x_number_values = links_segments.x
    y_number_values = links_segments.y
    label=links_segments.id
    plt.plot(x_number_values, y_number_values, linewidth=3)
    i=0
    for i in range(0, len(label), len(label)-1):
      
        plt.annotate(
                label[i],
                xy=( x_number_values[i], y_number_values[i]), xytext=(-5, 5),
                textcoords='offset points', ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.1', fc='m', alpha=0.5),
       )
       
    for r in range(len(links_segments)-1):
        P.arrow(x_number_values[r], y_number_values[r], x_number_values[r+1]-x_number_values[r], y_number_values[r+1]-y_number_values[r], fc="r", ec="r", head_width=5
                , head_length=10)

plt.show()



