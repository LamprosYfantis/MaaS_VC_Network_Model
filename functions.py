# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 09:26:47 2019

@author: Francisco
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools
import math
import networkx as nx


def import_data():
    
    a = dict(pd.read_csv('Road_nodes_coord.csv', delimiter=',', index_col=False))## Importing nodes data
    a['id']=a['id'].astype(str)
    
    l= pd.read_csv('Road_links.csv', delimiter=',', usecols=[0,3,4], index_col=False) ## Importing links data
    l_tt = pd.read_csv('Road_links_default_travel_times.csv', delimiter=',', usecols=[4,4], index_col=False) ## Importing default travel times per link
    l=l.assign(weight=l_tt) ## Adding the travel times to the links data
    l_length= pd.read_csv('links_length.csv', usecols=[2,2], delimiter=',', index_col=False)## Importing distances (length) per link
    l=l.assign(length=l_length) ## Adding the distances to the links data
    l=l.round({'weight':3, 'length':3}) ## Round to 3 decimals
    l=l.to_dict()# Converting into dict
    
    l_dual= pd.read_csv('Road_links.csv', delimiter=',', usecols=[0,3,4], index_col=False) ## Importing links data
    l_dual=l_dual.assign(weight=l_tt) ## Adding the travel times to the links data
    l_dual=l_dual.assign(length=l_length) ## Adding the distances to the links data
    l_dual=l_dual.round({'weight':3, 'length':3}) ## Round to 3 decimals
    l_dual=l_dual.to_dict()# Converting into dict

   
    ## Getting the unique values of origin nodes
    unique_o=np.unique(list(dict.values(l_dual['from_node'])))
    unique_d=np.unique(list(dict.values(l_dual['to_node'])))
## Adding the label 'o' to the from_nodes
    for i in range (len(l_dual['from_node'])):
        for j in range (len(unique_o)):
            if unique_o[j]==l_dual['from_node'][i]:
                l_dual['from_node'][i]=str(l_dual['from_node'][i])+'o'

    ## Adding the label 'd' to the to_nodes
    for i in range (len(l_dual['to_node'])):
        for j in range (len(unique_d)):
            if unique_d[j]==l_dual['to_node'][i]:
               l_dual['to_node'][i]=str(l_dual['to_node'][i])+'d'
    
    return(a,l,l_dual) ## a: dict of nodes data, l: dicts of links data
    
def length(): ## Determining the links length 
                ## Output: a .csv file with the links id and length
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
    

def import_tt():
    
  
    
    ## Importing the travel times per turning for all the 288 5-min time intervals
    
    ## NOTE: there is no information about some links at some time interval meaning that no car 
    ## transversed this link at those time intervals.
    ##There are also some turnings that are not included in the 521 turning groups (CHECK THIS)
    ## They are generated during the simulation by Simmobility in case there is no path 
    ## between OD, due to network misspecification , in order to allow a car to come back to 
    ## the origin ( CHECK THIS)

    tt= pd.read_csv('link_travel_time_per_5_min.csv', delimiter=';', index_col=False, header=None ) ##  Importing the file with the 288 5-min time intervals
    tt.columns = ['from_link','to_link','start_time','end_time', 'travel_time'] ## Adding the columns names
    tt.from_link=tt.from_link.astype(str) ## Converting the links id to str
    tt.to_link=tt.to_link.astype(str)


    tt=tt.set_index(['from_link','to_link']) ## Setting the df index as the link pairs
    
    tt[['hh_s','mm_s','ss_s']] = tt.start_time.str.split(":",expand=True,) ## Splitting the start_time into h, m and s
    tt[['hh_e','mm_e','ss_e']] = tt.end_time.str.split(":",expand=True,) ## Splitting the end_time into h, m and s
    
#    tt['d']=tt.index
#    tt.d=tt.d.astype(str)
#    tt.iloc[(1,161), 'd']
    
    ## Converting the h, m and s into integers
    tt.hh_s=tt.hh_s.astype(int)
    tt.mm_s=tt.mm_s.astype(int)
    tt.ss_s=tt.ss_s.astype(int)
    tt.hh_e=tt.hh_e.astype(int)
    tt.mm_e=tt.mm_e.astype(int)
    tt.ss_e=tt.ss_e.astype(int)
    

    tt['start_time_s']=(tt.hh_s*60+tt.mm_s)*60+tt.ss_s ## Adding a new column to store the start_time in seconds
    tt['end_time_s']=(tt.hh_e*60+tt.mm_e)*60+tt.ss_e ## Adding a new column to store the end_time in seconds
    tt=tt.drop(['hh_s','mm_s','ss_s','hh_e','mm_e','ss_e'], axis=1) ## Removing the h, m and s columns
    tt=tt[['start_time','end_time','start_time_s','end_time_s','travel_time']] ## Changing the columns order
   
    
    return(tt) ## tt: df with all the available link travel times per 5 min during 24 h
                   

def index_column(m): ## time interval in minutes
    a=pd.DataFrame()
    st=0
    et=st+m*60-1
    for i in range(int((24*60*60)/(m*60))):
        a[(st,et)]=0
        st=et+1
        et=st+m*60-1
    
    return(a)
    
def index_dual():
    turnings=pd.read_csv('Road_turning_groups.csv', delimiter=',', usecols=[2,3], index_col=False)  ## Importing turning groups data (from link to link)
    turnings.from_link=turnings.from_link.astype(str)
    turnings.to_link=turnings.to_link.astype(str)
    turnings=turnings.set_index(['from_link','to_link'])    
    turnings=turnings.sort_index()
    return(turnings)
    
    
def index_dum():
    ## importing l_dual
    
    l= pd.read_csv('Road_links.csv', delimiter=',', usecols=[0,3,4], index_col=False) ## Importing links data
    l_tt = pd.read_csv('Road_links_default_travel_times.csv', delimiter=',', usecols=[4,4], index_col=False) ## Importing default travel times per link
    l=l.assign(weight=l_tt) ## Adding the travel times to the links data
    l_length= pd.read_csv('links_length.csv', usecols=[2,2], delimiter=',', index_col=False)## Importing distances (length) per link
    l=l.assign(length=l_length) ## Adding the distances to the links data
    l=l.round({'weight':3, 'length':3}) ## Round to 3 decimals
    l=l.to_dict()# Converting into dict
    
  
   
   
    ## Getting the unique values of origin nodes
    unique_o=np.unique(list(dict.values(l['from_node'])))
    unique_d=np.unique(list(dict.values(l['to_node'])))
## Adding the label 'o' to the from_nodes
    for i in range (len(l['from_node'])):
        for j in range (len(unique_o)):
            if unique_o[j]==l['from_node'][i]:
                l['from_node'][i]=str(l['from_node'][i])+'o'

    ## Adding the label 'd' to the to_nodes
    for i in range (len(l['to_node'])):
        for j in range (len(unique_d)):
            if unique_d[j]==l['to_node'][i]:
               l['to_node'][i]=str(l['to_node'][i])+'d'
    
    
    
    
    index=pd.DataFrame(l)
    index.id=index.id.astype(str)
    index.to_node=index.to_node.astype(str)
    index=index.set_index(['id','to_node'])
    index=index.drop(['from_node','weight','length'], axis=1)
    index=index.sort_index()

    return(index)
    
def dicts_tt(tt,l):
    
    ##Importing the default travel times per link
    tt_d = pd.read_csv('Road_links_default_travel_times.csv', delimiter=',', usecols=[0,4], index_col=False) ## Importing default travel times per link
    tt_d.link_id=tt_d.link_id.astype(str) ## Converting the link ids to str
    tt_d=tt_d.set_index('link_id') ## Setting the links id as the df index
    
    ## Importing the turnings groups with the link pairs as index
    tt_dual=pd.DataFrame(index=index_dual().index)  ## Importing turning groups data (from link to link)
    tt_dual['travel_time']=np.nan ## Adding a new column for the default travel time
#    tt_dual=tt_dual.sort_index() ## Sorting the rows by the index 
#    tt_dual=tt_dual.reset_index() ## 
#    tt_dual.from_link=tt_dual.from_link.astype(str)
#    tt_dual.to_link=tt_dual.to_link.astype(str)
#    tt_dual=tt_dual.set_index(['from_link','to_link'])
#    tt_u= tt_u.sort_values(['from_link','to_link','start_time','end_time']) ## sorting the values
#    tt_u=tt_u.reset_index(drop=True) #Reseting the index
    
    ## Assigning the default travel time and the length to the different turnings
     
    for ind in tt_dual.index:
        tt_dual.travel_time[ind]=round(tt_d.travel_time[ind[0]],2)
        
    
    
    
#    ##Storing the unique time intervals
#    a=pd.DataFrame(tt.start_time_s.drop_duplicates(keep='first'))
#    a['end_time_s']=tt.end_time_s.drop_duplicates(keep='first')
#    a=a.reset_index(drop=True)
#    
    tt_dict=pd.DataFrame(index=tt_dual.index)
#   
    for column in index_column(5).columns: ## assigns the 288 5 intervals as columns od the df usinf index_column()
        tt_dict[column]=0
      
    tt_dict=tt_dict.to_dict()
    tt_dict=pd.DataFrame(tt_dict)
    tt_dict=tt_dict.sort_index()
    
    for i in tt_dict.index:
        for j in tt_dual.index:
            if i==j:
                tt_dict.loc[i,:]=tt_dual.travel_time[j]
     
    tt_dict=tt_dict.T.to_dict()
    
    ##dummy dict
    
    tt_dum_dict=pd.DataFrame(index=index_dum().index)
#    tt_dum_dict.id=tt_dum_dict.id.astype(str)
#    tt_dum_dict.to_node=tt_dum_dict.to_node.astype(str)
#    tt_dum_dict=tt_dum_dict.set_index(['id','to_node'])
#    tt_dum_dict=tt_dum_dict.drop(['from_node','weight','length'], axis=1)
  
    
    for column in index_column(5).columns: ## assigns the 288 5 intervals as columns od the df usinf index_column()
        tt_dum_dict[column]=0

#    for i in range(len(a)):
#        tt_dum_dict[(a.start_time_s[i],a.end_time_s[i])]=0
    
    tt_dum_dict=tt_dum_dict.to_dict()
    tt_dum_dict=pd.DataFrame(tt_dum_dict)  
    
    for i in tt_dum_dict.index:
        for j in tt_dual.index:
            if i[0]==j[0]:
                tt_dum_dict.loc[i,:]=tt_dual.travel_time[j]
    tt_dum_dict=tt_dum_dict.T.to_dict()
           
    return(tt_dict,tt_dum_dict)
    

def dist():
    
#    if isinstance(dict_tt,dict)==True:
#        dict_tt=pd.DataFrame.from_dict(dict_tt, orient='index')  
#    
#    if isinstance(dum_dict_tt,dict)==True:
#        dum_dict_tt=pd.DataFrame.from_dict(dum_dict_tt, orient='index') 
     ##Importing the default travel times per link
    d = pd.read_csv('links_length.csv', usecols=[1,2], delimiter=',', index_col=False) ## Importing default travel times per link
    d.id=d.id.astype(str)
    d=d.set_index('id')
    dist_dual=pd.DataFrame(index=index_dual().index)
    dist_dual['distance']=0.0
    
    for ind in dist_dual.index:
       dist_dual.distance[ind]=d.length[ind[0]].round(3)
    
    dist_dual=dist_dual.T.to_dict() 
                
    ## dummy dist
    dum_dist=pd.DataFrame(index=index_dum().index)    
    dum_dist['distance']=0.0
    
    for ind in dum_dist.index:
      dum_dist.distance[ind]=d.length[ind[0]].round(3)
            
    dum_dist=dum_dist.T.to_dict()
     
    return(dist_dual,dum_dist)
   
# 
#    
    
def update_dicts_tt(dict_tt, dum_dict_tt,tt,t,H,y): #INPUT: dict_tt, dum_dict_tt=dict of dummy destinationes edges tt, tt:df with all the i min interval per link, 
                                 # t: time at the update is done, H: time horizon to update in min
    links=list(dict_tt.keys())
    dict_tt=pd.DataFrame.from_dict(dict_tt, orient='index')

    

    t='23:35:00'                # i: interval of the travel time per links in minutes
    H=15
    y=5
    H=H*60                             
    h=float(t[0:2])
    m=float(t[3:5])
    s=float(t[6:8])
    ts=(h*60+m)*60+s
    
    
    if ts<y*60:   #Taking the (23:55,23:59:59) interval 
      a=tt[(tt.end_time_s>=86400-ts)]
      a=a.rename(columns={'travel_time':(a.start_time_s[0],a.end_time_s[0])})

    
   
    else:
       a=tt[(tt.end_time_s>=ts-y*60)]
       a=a[(a.start_time_s<=ts-y*60)]
       a=a.rename(columns={'travel_time':(a.start_time_s[0],a.end_time_s[0])})

    
    for ind in a.index: ##  Removing the a links that are different from the 521 turning groups  
       if ind not in links:
           a=a.drop([ind])
    
    
    for col in dict_tt.columns:
        if col[0]>ts-y*60 and col[1]<ts+H+y*60:
            print(col)
            dict_tt[(col)]=a[(a.start_time_s[0],a.end_time_s[0])]
        if  ts-86399<H:
            if col[0]<H-86399+ts:
                print(col)
                dict_tt[(col)]=a[(a.start_time_s[0],a.end_time_s[0])]
#    if ts-86399<H:
    dict_tt=dict_tt.T.to_dict()   
       
    
    ## updating the dummy
    
    dum_dict_tt=pd.DataFrame(dum_dict_tt)
    
    dum_dict_tt=dum_dict_tt.T
     
    b = pd.DataFrame(index=dum_dict_tt.index)
    for i in range(len(a.columns)-1):
      
         b[a.columns[i]]=a.iloc[0,i]
    
    b= b.reset_index(drop=True, level=1)
    b['links']=dum_dict_tt.index
    b['travel_time']=np.nan
    c= a.reset_index(drop=False, level=1) 
    c=c.rename(columns={(a.start_time_s[0],a.end_time_s[0]):'travel_time'})
    c=c.drop(c.index[2])

    for ind in b.index:
        if ind in c.index:
            b.loc[ind,'travel_time']=c.loc[ind,'travel_time'].min()
    
    b=b.dropna()
    b=b.rename(columns={'travel_time':(a.start_time_s[0],a.end_time_s[0])})
    b=b.set_index(b.links) 
    
    for col in dum_dict_tt.columns: 
        if col[1]>=ts-y*60 and col[1]<ts+H+y*60:
            print(col)
            dum_dict_tt[(col)]=b[(b.start_time_s[0],b.end_time_s[0])]
    
    dum_dict_tt=dum_dict_tt.T.to_dict()

#   
    return(dict_tt,dum_dict_tt)        

    
def add_nodes(G,a): ## a: dict of nodes data
    for i in range(len(a['id'])):
        G.add_node(a['id'][i], pos=(a['x'][i],a['y'][i]))
    return(G) 
    
def add_edges(G,a): ## a: dict of links data
    for i in range(len(a['id'])):
        G.add_edge(str(a['from_node'][i]),str(a['to_node'][i]), id= a['id'][i],dist=a['length'][i],weight=a['weight'][i])
    return(G)


    

def graph(G):
    pos=nx.get_node_attributes(G,'pos')  #Storing the nodes location
    nx.draw(G,pos, with_labels=True) # Graph with node attributes
#    nx.draw_networkx_edge_labels(G,pos) ## Graph with edge attributes
    plt.show() 

def add_dual_nodes(G,a): ## a: dict of links data
    for i in range(len(a['id'])): 
        G.add_node(str(a['id'][i]),  node_type='dual_node')
    return(G)

def add_dummy_nodes(G,a): ## a: dict of nodes
    ## Getting the unique values of origin node
    
## Adding the from_node and to_nodes as H nodes
    for i in range(len(a['id'])): 
        G.add_node(str(a['id'][i])+'o',id =a['id'][i], pos=(a['x'][i],a['y'][i]), node_type='dummy_node')
        G.add_node(str(a['id'][i])+'d', id =a['id'][i], pos=(a['x'][i],a['y'][i]), node_type='dummy_node')
    
    return(G)
       
#def updating_tt(a,tt,tt_u): ## a: time in string format
#    
#    unique_st=list(tt.start_time.unique())
#    
#    if (a in unique_st): 
#        tt_x=tt[tt.start_time==a]
#        tt_x=tt_x.reset_index(drop=True)
#        ##assigning the travel times 
#        for i in range(len(tt_x)):
#            for j in range(len(tt_u)):
#                if tt_x.from_link[i]==tt_u.from_link[j] and tt_x.to_link[i]==tt_u.to_link[j]:
#                    tt_u.loc[j,'travel_time']=tt_x.loc[i,'travel_time']
#                    tt_u.loc[j,'start_time']=tt_x.loc[i,'start_time']
#                    tt_u.loc[j,'end_time']=tt_x.loc[i,'end_time']
#      
#        k=pd.concat([tt_u,tt_x]) ## joining tt_x and tt_u
#        k=k.drop_duplicates(keep=False) ## storing the non duplicates values
#        tt_u=pd.concat([tt_u,k])   ## joining tt_u with the non duplicates values     
#        tt_u=tt_u.drop_duplicates(keep='first') ## removing the duplicates
#        tt_u= tt_u.sort_values(['from_link','to_link','start_time','end_time']) ## sorting
#        tt_u=tt_u.reset_index(drop=True) 
#    return(tt_u) ## tt_u: df with the link travel times at time a
    
def add_dummy_edges(G,a): ## a: dict of links data
                               
    ## Adding the edges that links the dummy origins with the H  nodes (G edges)
    for i in range (len(a['from_node'])):  
        G.add_edge(str(a['from_node'][i]), str(a['id'][i]), weight=0, dist=0, cost=0, departure_time=None, edge_type='orig_dummy_edge')
 ## Adding the edges that links the the H  nodes (G edges) with the dummy destinations with the minimum travel time of the preceding G link (node in our case) 
    for edge in index_dum().index:  
         G.add_edge(*edge, weight=0, departure_time=None, edge_type='dest_dummy_edge')
#        G.add_edge(ind, weight=dum_dict_tt[edge], dist=round(tt_u['distance'][i],3), cost=round(tt_u['distance'][i]*5,3), departure_time=None, edge_type='dest_dummy_edge')
    
    return(G)
    


    
 ## Adding the edges that link the nodes (G links) with the weight of the preceding G link (node in our case)         
def add_dual_edges(G): #b: tt_u
    for edge in index_dual().index:
        G.add_edge(*edge, departure_time=None, edge_type='dual_edge') 
    
    return(G)



#def add_dual_edges(G,tt_u):
#    for i in range(len(tt_u)):
#        G.add_edge(tt_u.from_link[i],tt_u.to_link[i],weight= tt_u.travel_time[i], dist=round(tt_u.distance[i],3), cost=round(tt_u.distance[i]*5,3), departure_time=None, edge_type='dual_edge') 
#    return(G)


def toll(ti,tf): ##dict_tt, ti: cogestion charge starting, tf: congestion charge ending
    
#    ti=25200#'07:00:00'                # i: interval of the travel time per links in minutes
#    tf=64800#'18:00:00'                          
    hi=float(ti[0:2])
    mi=float(ti[3:5])
    si=float(ti[6:8])
    ti=(hi*60+mi)*60+si
    
    hf=float(tf[0:2])
    mf=float(tf[3:5])
    sf=float(tf[6:8])
    tf=(hf*60+mf)*60+sf
    
    
#toll_l=pd.DataFrame({'links':[(12,11),(106,9),(6,22),(57,22),(19,23),(41,23),(41,40),(39,40),(15,37),(16,36),(33,34),(32,29)]})
    
#    if isinstance(dict_tt,dict)==True:
#        dict_tt=pd.DataFrame.from_dict(dict_tt, orient='index')  
#    
#    if isinstance(dum_dict_tt,dict)==True:
#        dum_dict_tt=pd.DataFrame.from_dict(dum_dict_tt, orient='index') 
        
    toll_l=pd.read_csv('Road_links_tolls.csv', delimiter=',', index_col=False)
    toll_l.from_node=toll_l.from_node.astype(str)
    toll_l.to_node=toll_l.to_node.astype(str)
    toll_l.id=toll_l.id.astype(str)
    toll_l=toll_l.set_index(['from_node','to_node'])
    
    
    toll=pd.DataFrame(index=index_dual().index)
    toll['toll']=0
    
    for ind in toll.index:
        for id in toll_l.id:
            if id==ind[0]:
                toll.toll[id]=1
    
    toll_dual=pd.DataFrame(columns=index_column(5).columns, index=index_dual().index)
    toll_dual=toll_dual.fillna(0)
    
    
    for col in toll_dual.columns: 
        if col[0]>=ti and col[1]<tf:
             toll_dual[(col)]=toll.toll
    ## dummy tolls    
    toll_d=pd.DataFrame(index=index_dum().index)
    toll_d['toll']=0
    
    for ind in toll_d.index:
        for id in toll_l.id:
            if id==ind[0]:
                toll_d.toll[id]=1
    
    toll_dum=pd.DataFrame(columns=index_column(5).columns, index=index_dum().index)
    toll_dum=toll_dum.fillna(0)
    
    
    for col in toll_dum.columns: 
        if col[0]>=ti and col[1]<tf:
             toll_dum[(col)]=toll_d.toll
    
    return(toll_dual,toll_dum)        

def cost(dict_tt,dum_dict_tt,tt_u,dist_dum, toll_dual,toll_dum, mode, service): ## mode: taxi, service: normal/minivan
    ## tt_u: dist_dual

    a=pd.DataFrame.from_dict(dict_tt, orient='index')
    b=pd.DataFrame.from_dict(dum_dict_tt, orient='index')

    dist_dual=pd.DataFrame.from_dict(tt_u, orient='index')

    
    dist_dum=pd.DataFrame.from_dict(dist_dum, orient='index')
    
    
    if mode=='taxi' and service=='normal':
        cost_dual=pd.DataFrame(8.5*dist_dual.to_numpy()/1000+5.75*a.to_numpy()/60+toll_dual.to_numpy()*150, columns=a.columns)
        cost_dual=cost_dual.set_index(a.index)
        
        ## dum cost
        
        cost_dum=pd.DataFrame(8.5*dist_dum.to_numpy()/1000+5.75*b.to_numpy()/60+toll_dum.to_numpy()*150, columns=b.columns)
        cost_dum=cost_dum.set_index(b.index)
        
        
#        
        
    elif mode=='taxi' and service=='minivan':
        cost_dual=pd.DataFrame(12*dist_dual.to_numpy()/1000+6.67*a.to_numpy()/60+toll_dual.to_numpy()*150, columns=a.columns)
        cost_dual=cost_dual.set_index(a.index)
        
        cost_dum=pd.DataFrame(12*dist_dum.to_numpy()/1000+6.67*b.to_numpy()/60+toll_dum.to_numpy()*150, columns=b.columns)
        cost_dum=cost_dum.set_index(b.index)
#       
    cost_dual=cost_dual.round(2)
    cost_dum=cost_dum.round(2)
    cost_dual=cost_dual.T.to_dict()
    cost_dum=cost_dum.T.to_dict()
    
    return(cost_dual,cost_dum)

def add_edge_attributes(G,dict_tt,dum_dict_tt,dist_dual,dist_dum,cost_dual,cost_dum):
    for edge in dict_tt:
        G.add_edge(*edge, weight=dict_tt[edge], dist=dist_dual[edge], cost=cost_dual[edge])
    
    for edge in dum_dict_tt:
        G.add_edge(*edge, weight=dum_dict_tt[edge], dist=dist_dum[edge], cost=cost_dum[edge])        

#        G.add_edge(*edge, weight=dict_tt[edge]['weight'])
  
    return(G)


def k_shortest_paths(G, source, target, k, weight='weight'):
    return list(islice(nx.shortest_simple_paths(G, source, target, weight='weight'), k))    

def PathTT(x,a,G):
    
    
   
    
    for i in range(len(x)):
        print()
        print('Path %s: %s' %(i+1,x[i]))
        d=0 ## travel time
        m=0 ## minutes
        h=0 ## hours
        for j in range(len(x[i])-1):
            u=G[x[i][j]][x[i][j+1]]['weight']
            d=u+d
            
        if d>60:
            m=m+d//60
            d=d-60*m
            print('Travel time = %.f m %.2f s' %(m,d))
        else:
            print('Travel time = %.2f s' %d)
    
       
           
        for j in range(1,len(x[i])-1):
            s=0 ## length
            for n in range(len(a)):
                if a['id'][n]==x[i][j]:
                    v=a['length'][n]
                    s=v+s
            ##Printing the length 
        if s>1000:
            s=s/1000
            print('Length = %.2f km' %s)
        else: 
                print('Length = %.2f m' %s)
        
   
def from_link_to_node(x):
    
    
    a=pd.read_csv('Road_links.csv', delimiter=',', usecols=[0,3,4], index_col=False) ## Importing links data
    path=list()
    for j in range(1,len(x)-1):
        for i in range(len(a)):
            if a.id[i]==x[j]:
                if j==1:
                    path.append(a.from_node[i])
                    path.append(a.to_node[i])
                else:       
                    path.append(a.to_node[i])
  
    return(path)
    


## ehail graph
    
## 

def gen_taxi_tt_dict():
    
    a=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
    a['incoming_node']=a.zone_id
    b=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
    b['outgoing_node']=b.zone_id
    
   ## Adding the label 'i' to the incoming nodes
#    for index in a.index:
#        a.incoming_node[index]=a.incoming_node[index]+'i'
#
#     ## Adding the label 'o' to the outgoing nodes    
#    for index in b.index:
#        b.outgoing_node[index]=b.outgoing_node[index]+'o'
    
    taz_pairs=pd.DataFrame(columns=['from_node','to_node','from_zone','to_zone'])
  
    
    for i in b.index:
        for j in a.index:
#            if b.zone_id[i]!=a.zone_id[j]:
            taz_pairs=taz_pairs.append({'from_node':a.incoming_node[j], 'to_node': b.outgoing_node[i], 'from_zone':a.zone_id[j], 'to_zone':b.zone_id[i]}, ignore_index=True)
#            else:
#                taz_pairs=taz_pairs.append({'from_node':a.incoming_node[j], 'to_node': b.outgoing_node[i], 'from_zone':a.zone_id[j], 'to_zone':b.zone_id[i]}, ignore_index=True)

    taz_pairs=taz_pairs.sort_values(['from_node','to_node'])
     
          
#    a=a.append(b)
#    taz=pd.read_csv('taz_2012.csv', delimiter=',',index_col=False)
#    taz_pairs=pd.DataFrame([p for p in itertools.product(a.zone_id, repeat=2)])
#    taz_pairs[0]=taz_pairs[0].astype(str)
#    taz_pairs[1]=taz_pairs[1].astype(str)
#    taz_tt=pd.DataFrame(columns=index_column(5).columns)
#    taz_tt=pd.DataFrame()
#    taz_tt['origin_taz']=taz_pairs[0]
#    taz_tt['dest_taz']=taz_pairs[1]
    
#    taz_tt=pd.DataFrame(columns=index_column(5).columns)
    taz_tt=pd.DataFrame()        
    taz_tt['from_node']=taz_pairs['from_node']
    taz_tt['to_node']=taz_pairs['to_node']
    taz_tt=taz_tt.set_index(['from_node','to_node'])
    
 
    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
    trips.columns = ['person_id','trip_origin_node','trip_dest_node','from_zone', 'to_zone','subtrip_origin_type','subtrip_dest_type','travel_mode','arrival_time','travel_time','pt_line']
    
    y=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)
#    y.node_id=y.node_id.astype(str)
#    y.taz=y.taz.astype(str)
    
    
    x=trips.loc[(trips.travel_mode=='ON_TAXI')|(trips.travel_mode=='ON_SMS_Veh')|(trips.travel_mode=='ON_RAIL_SMS_Veh')]
    x=x.reset_index(drop=True)
    x.from_zone=x.from_zone.astype(int)
    x.to_zone=x.to_zone.astype(int)
    
    x.from_zone=x.from_zone.replace(list(y.node_id),list(y.taz))
    x.to_zone=x.to_zone.replace(list(y.node_id),list(y.taz))
    
#    x.from_zone=x.from_zone.astype(str)
#    x.to_zone=x.to_zone.astype(str)
#    
#    x['from_taz']=x.from_zone
#    x['to_taz']=x.to_zone
#    
#    x.from_zone=x.from_zone+'i'
#    x.to_zone=x.to_zone+'o'
    
#    x.from_zone[x.from_taz==x.to_taz]=x.from_zone[x.from_taz==x.to_taz]+'i'
#    x.to_zone[x.from_taz==x.to_taz]=x.to_zone[x.from_taz==x.to_taz]+'o'
    
#    x=x.drop(['from_taz','to_taz'], axis=1)

#    x['from_zone']=0
#    x['to_zone']=0
#    x.trip_origin_id=x.trip_origin_id.astype(str)
#    x.trip_dest_id=x.trip_dest_id.astype(str)
    

#    for i in range(len(y)):
#        x.origin_taz.loc[x.trip_origin_id==y.node_id[i]]=y.taz[i]
#        x.dest_taz.loc[x.trip_dest_id==y.node_id[i]]=y.taz[i]    
    
    x[['hh_s','mm_s','ss_s']] = x.arrival_time.str.split(":",expand=True,) ## Splitting the start_time into h, m and s
#    x[['hh_e','mm_e','ss_e']] = x.end_time.str.split(".",expand=True,) ## Splitting the end_time into h, m and s
    
#    tt['d']=tt.index
#    tt.d=tt.d.astype(str)
#    tt.iloc[(1,161), 'd']
    
    ## Converting the h, m and s into integers
    x.hh_s=x.hh_s.astype(int)
    x.mm_s=x.mm_s.astype(int)
    x.ss_s=x.ss_s.astype(int)
#    x.hh_e=x.hh_e.astype(int)
#    x.mm_e=x.mm_e.astype(int)
#    x.ss_e=x.ss_e.astype(int)
#    

    x['arrival_time_s']=(x.hh_s*60+x.mm_s)*60+x.ss_s ## Adding a new column to store the start_time in seconds
#    x['end_time_s']=(x.hh_e*60+x.mm_e)*60+x.ss_e ## Adding a new column to store the end_time in seconds
#    x=x.drop(['hh_s','mm_s','ss_s','hh_e','mm_e','ss_e'], axis=1)
    x=x.drop(['hh_s','mm_s','ss_s'], axis=1)
    
    
    x=x.sort_values(['arrival_time_s'])## Removing the h, m and s columns
    x=x.reset_index(drop=True)
#    y=y.set_index([('origin_taz','destination_taz')])
#    start=time.time() 
    for interval in index_column(5).columns:
    
        c=pd.DataFrame(index=taz_tt.index)
#        taz_tt[interval]=0
        c[interval]=0

        d=x[x.arrival_time_s>=interval[0]]
        d=d[d.arrival_time_s<= interval[1]]
        
       
        if len(d)!=0:
            
            d=d.set_index(['from_zone','to_zone'])
            
            for index in d.index:
                 c.loc[index,:]=round(d.travel_time[index].mean(),0) 
                 
#            else: 
#              continue               
#                 taz_tt.loc[(index[0],index[1]),(interval[0],interval[1])]
#                 taz_tt.loc[:,(0,299)]
        taz_tt[interval]=c[interval]


    for index in taz_tt.index:
         taz_tt.loc[index,:]=taz_tt.loc[index,:].where(taz_tt.loc[index,:]!=0,np.sum(np.array(taz_tt.loc[index,:]))/np.count_nonzero(np.array(taz_tt.loc[index,:])))
    taz_tt=taz_tt.fillna(0)
    
    taz_tt=taz_tt.round(0)
    
    
     
    for index in taz_tt.index:
        if np.count_nonzero(np.array(taz_tt.loc[index]))==0:
            taz_tt.loc[index[0],index[1]]=taz_tt.loc[index[1],index[0]]
    
         
    for index in taz_tt.index:
        if np.count_nonzero(np.array(taz_tt.loc[index]))==0:
            print(index)
    
    
    x=trips.loc[(trips.travel_mode=='ON_CAR')]
    
    x=x.reset_index(drop=True)
    x.from_zone=x.from_zone.astype(int)
    x.to_zone=x.to_zone.astype(int)
    
    x.from_zone=x.from_zone.replace(list(y.node_id),list(y.taz))
    x.to_zone=x.to_zone.replace(list(y.node_id),list(y.taz))
    x[['hh_s','mm_s','ss_s']] = x.arrival_time.str.split(":",expand=True,) ## Splitting the start_time into h, m and s
    ## Converting the h, m and s into integers
    x.hh_s=x.hh_s.astype(int)
    x.mm_s=x.mm_s.astype(int)
    x.ss_s=x.ss_s.astype(int)


    x['arrival_time_s']=(x.hh_s*60+x.mm_s)*60+x.ss_s ## Adding a new column to store the start_time in seconds

    x=x.drop(['hh_s','mm_s','ss_s'], axis=1)
    

    x=x.sort_values(['arrival_time_s'])## Removing the h, m and s columns
    x=x.reset_index(drop=True)
#    x.from_zone=x.from_zone.astype(str)
#    x.to_zone=x.to_zone.astype(str)
#   
    taz_tt_car=pd.DataFrame()        
    taz_tt_car['from_node']=taz_pairs['from_node']
    taz_tt_car['to_node']=taz_pairs['to_node']
    taz_tt_car=taz_tt_car.set_index(['from_node','to_node'])
 
    for index in taz_tt.index:
        if np.count_nonzero(np.array(taz_tt.loc[index]))!=0:
            taz_tt_car=taz_tt_car.drop([index])
            
        
    for interval in index_column(5).columns:
        c=pd.DataFrame(index=taz_tt_car.index)
#        taz_tt[interval]=0
        c[interval]=0

        d=x[x.arrival_time_s>=interval[0]]
        d=d[d.arrival_time_s<= interval[1]]
        
       
        if len(d)!=0:
            
            d=d.set_index(['from_zone','to_zone'])
            
            for index in d.index:
                 c.loc[index,:]=round(d.travel_time[index].mean(),0) 
         
        taz_tt_car[interval]=c[interval]     

    for index in taz_tt_car.index:
         taz_tt_car.loc[index,:]=taz_tt_car.loc[index,:].where(taz_tt_car.loc[index,:]!=0,np.sum(np.array(taz_tt_car.loc[index,:]))/np.count_nonzero(np.array(taz_tt_car.loc[index,:])))
    
    
    taz_tt_car=taz_tt_car.fillna(0)
    
    
#    for index in taz_tt.index:
#        if np.count_nonzero(np.array(taz_tt.loc[index]))==0:
    
    
    taz_tt=taz_tt.T.to_dict()
            
    return(taz_tt)   




def gen_ehail_tt_dict():
    
    a=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
#    a.zone_id=a.zone_id.astype(str)
    a['incoming_node']=a.zone_id
    b=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
#    b.zone_id=b.zone_id.astype(str)
    b['outgoing_node']=b.zone_id
    
#   ## Adding the label 'i' to the incoming nodes
#    for index in a.index:
#        a.incoming_node[index]=a.incoming_node[index]+'i'
#
#     ## Adding the label 'o' to the outgoing nodes    
#    for index in b.index:
#        b.outgoing_node[index]=b.outgoing_node[index]+'o'
    
    taz_pairs=pd.DataFrame(columns=['from_node','to_node','from_zone','to_zone'])
    
    
    for i in b.index:
        for j in a.index:
#            if b.zone_id[i]!=a.zone_id[j]:
            taz_pairs=taz_pairs.append({'from_node':a.incoming_node[j], 'to_node': b.outgoing_node[i], 'from_zone':a.zone_id[j], 'to_zone':b.zone_id[i]}, ignore_index=True)
#            else:
#                taz_pairs=taz_pairs.append({'from_node':a.incoming_node[j], 'to_node': b.outgoing_node[i], 'from_zone':a.zone_id[j], 'to_zone':b.zone_id[i]}, ignore_index=True)
#    
#           
#    a=a.append(b)
#    taz=pd.read_csv('taz_2012.csv', delimiter=',',index_col=False)
#    taz_pairs=pd.DataFrame([p for p in itertools.product(a.zone_id, repeat=2)])
#    taz_pairs[0]=taz_pairs[0].astype(str)
#    taz_pairs[1]=taz_pairs[1].astype(str)
#    taz_tt=pd.DataFrame(columns=index_column(5).columns)
#    taz_tt=pd.DataFrame()
#    taz_tt['origin_taz']=taz_pairs[0]
#    taz_tt['dest_taz']=taz_pairs[1]
    
#    taz_tt=pd.DataFrame(columns=index_column(5).columns)
    taz_tt=pd.DataFrame()        
    taz_tt['from_node']=taz_pairs['from_node']
    taz_tt['to_node']=taz_pairs['to_node']
    taz_tt=taz_tt.set_index(['from_node','to_node'])
    
 
    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
    trips.columns = ['person_id','trip_origin_node','trip_dest_node','from_zone', 'to_zone','subtrip_origin_type','subtrip_dest_type','travel_mode','arrival_time','travel_time','pt_line']
    
    y=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)
#    y.node_id=y.node_id.astype(str)
#    y.taz=y.taz.astype(str)
    
    
    x=trips.loc[(trips.travel_mode=='ON_SMS_Veh')|(trips.travel_mode=='ON_RAIL_SMS_Veh')]
    x=x.reset_index(drop=True)
    x.from_zone=x.from_zone.astype(int)
    x.to_zone=x.to_zone.astype(int)
    
    x.from_zone=x.from_zone.replace(list(y.node_id),list(y.taz))
    x.to_zone=x.to_zone.replace(list(y.node_id),list(y.taz))
    
#    x.from_zone=x.from_zone.astype(str)
#    x.to_zone=x.to_zone.astype(str)
#    
#    x['from_taz']=x.from_zone
#    x['to_taz']=x.to_zone
#    
#    x.from_zone=x.from_zone+'i'
#    x.to_zone=x.to_zone+'o'
#    
#    x.from_zone[x.from_taz==x.to_taz]=x.from_zone[x.from_taz==x.to_taz]+'i'
#    x.to_zone[x.from_taz==x.to_taz]=x.to_zone[x.from_taz==x.to_taz]+'o'
#    
#    x=x.drop(['from_taz','to_taz'], axis=1)

#    x['from_zone']=0
#    x['to_zone']=0
#    x.trip_origin_id=x.trip_origin_id.astype(str)
#    x.trip_dest_id=x.trip_dest_id.astype(str)
    

#    for i in range(len(y)):
#        x.origin_taz.loc[x.trip_origin_id==y.node_id[i]]=y.taz[i]
#        x.dest_taz.loc[x.trip_dest_id==y.node_id[i]]=y.taz[i]    
    
    x[['hh_s','mm_s','ss_s']] = x.arrival_time.str.split(":",expand=True,) ## Splitting the start_time into h, m and s
#    x[['hh_e','mm_e','ss_e']] = x.end_time.str.split(".",expand=True,) ## Splitting the end_time into h, m and s
    
#    tt['d']=tt.index
#    tt.d=tt.d.astype(str)
#    tt.iloc[(1,161), 'd']
    
    ## Converting the h, m and s into integers
    x.hh_s=x.hh_s.astype(int)
    x.mm_s=x.mm_s.astype(int)
    x.ss_s=x.ss_s.astype(int)
#    x.hh_e=x.hh_e.astype(int)
#    x.mm_e=x.mm_e.astype(int)
#    x.ss_e=x.ss_e.astype(int)
#    

    x['arrival_time_s']=(x.hh_s*60+x.mm_s)*60+x.ss_s ## Adding a new column to store the start_time in seconds
#    x['end_time_s']=(x.hh_e*60+x.mm_e)*60+x.ss_e ## Adding a new column to store the end_time in seconds
#    x=x.drop(['hh_s','mm_s','ss_s','hh_e','mm_e','ss_e'], axis=1)
    x=x.drop(['hh_s','mm_s','ss_s'], axis=1)
    
    
    x=x.sort_values(['arrival_time_s'])## Removing the h, m and s columns
    x=x.reset_index(drop=True)
#    y=y.set_index([('origin_taz','destination_taz')])
#    start=time.time() 
    
 
    
    for interval in index_column(5).columns:
    
        c=pd.DataFrame(index=taz_tt.index)
#        taz_tt[interval]=0
        c[interval]=0

        d=x[x.arrival_time_s>=interval[0]]
        d=d[d.arrival_time_s<= interval[1]]
        
       
        if len(d)!=0:
            
            d=d.set_index(['from_zone','to_zone'])
            
            for index in d.index:
                 c.loc[index,:]=round(d.travel_time[index].mean(),0) 
                 
#            else: 
#              continue               
#                 taz_tt.loc[(index[0],index[1]),(interval[0],interval[1])]
#                 taz_tt.loc[:,(0,299)]
        taz_tt[interval]=c[interval]


    for index in taz_tt.index:
         taz_tt.loc[index,:]=taz_tt.loc[index,:].where(taz_tt.loc[index,:]!=0,np.sum(np.array(taz_tt.loc[index,:]))/np.count_nonzero(np.array(taz_tt.loc[index,:])))
    taz_tt=taz_tt.fillna(0)
    taz_tt=taz_tt.round(0)
    
    
    
    
#    taz_tt=taz_tt.T.to_dict()



    return(taz_tt)   

# taz_list=pd.DataFrame()
#    taz_list['origin_taz']=0
#    taz_list['destination_taz']=0
#taz_tt['taz_pairs']=0
#    for tazid in taz.zone_id:
#        for tazid2 in taz.zone_id:
##            taz_list.extend([(str(tazid),str(tazid2))])
#            taz_list=taz_list.append({'origin_taz':str(tazid),'destination_taz':str(tazid2)},ignore_index=True)


#    a=[p for p in itertools.product(taz.zone_id, repeat=2)] #https://stackoverflow.com/questions/3099987/generating-permutations-with-repetitions-in-python
   
 
    
# Print the obtained permutations 
#for i in list(perm): 
#    print(i) 
    
    
#    
#    for tazid in list(perm):
##            taz_list.extend([(str(tazid),str(tazid2))])
#        taz_tt=taz_tt.append({'origin_taz':str(tazid[0]),'dest_taz':str(tazid[1])},ignore_index=True)

 
    

#    x=subtrip[subtrip.travel_mode=='TaxiTravel']                             
#end=time.time()
#print('Running time: %f min' %((end-start)/60))
            
#      dict_tt[(col)]=a[(a.start_time_s[0],a.end_time_s[0])]           
        
            
#        for index in y.index.unique():
#            print(index, interval)
#            a=x[x.origin_taz==index[0]]
#            a=a[a.destination_taz==index[1]]
#            a=a[a.end_time_s>=interval[0]]
#            a=a[a.end_time_s<= interval[1]]
#            
#        
#        for index in x.index.unique():
#            if x.end_time_s[index]>=interval[0] and x.end_time_s[index]<= interval[1]:
#                a=a.append(x.loc[index,:])
#                a=a.append(a)        
#        a.origin_taz=a.origin_taz.astype(str)
#        a.destination_taz=a.destination_taz.astype(str)
#        a=a.set_index(['origin_taz','destination_taz'])
#        
#        if len(a)!=0:
#                b=pd.DataFrame(index=taz_tt.index)
#                b[interval]=0
#      
#                for zone in a.index:
#                    b.loc[zone,:]=a.travel_time[zone].mean()
#                for col in b.columns:
#                     taz_tt[(col)]=b
                     
#                    x.travel_time[x.travel_time==0]
    
                    
            
#          dum_dict_tt[(col)]=b[(b.start_time_s[0],b.end_time_s[0])]
        
#        if x.e
#        print(interval[1])
#    x=tt[['start_time','end_time','start_time_s','end_time_s','travel_time']] 
    
    

#a=pd.DataFrame.from_dict(a, orient='index')
def gen_ehail_wt_dict(): ##a:tt_dual
    
    ## importing the taz 
    taz=pd.read_csv('taz_2012.csv', delimiter=',',index_col=False)
    
    ##creates a df with the same columns as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
    taz_wt=pd.DataFrame(columns=index_column(5).columns)##creates a df with the same columns as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
    taz_wt['zone_id']=taz.zone_id ##adding a new column with the zone id
    taz_wt.zone_id= taz_wt.zone_id.astype(str) ## converting the zone id to str
    taz_wt=taz_wt.set_index('zone_id') ## sets the zone id as the index of taz_wt
    
#    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
    trips.columns = ['person_id','trip_origin_node','trip_dest_node','from_zone', 'to_zone','subtrip_origin_type','subtrip_dest_type','travel_mode','arrival_time','travel_time','pt_line']
    
    y=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)
#    y.node_id=y.node_id.astype(str)
#    y.taz=y.taz.astype(str)
    
    
    x=trips.loc[(trips.travel_mode=='WAIT_SMS')|(trips.travel_mode=='WAIT_RAIL_SMS')]
    x=x.reset_index(drop=True)
    x.from_zone=x.from_zone.astype(int)
    x=x.drop(['to_zone'], axis=1)
   
    
    
    x.from_zone=x.from_zone.replace(list(y.node_id),list(y.taz))
    x.from_zone=x.from_zone.astype(str)  
    x=x.rename(columns={'from_zone':'zone', 'travel_time':'waiting_time'})
    


#    x['from_zone']=0
#    x['to_zone']=0
#    x.trip_origin_id=x.trip_origin_id.astype(str)
#    x.trip_dest_id=x.trip_dest_id.astype(str)
    

#    for i in range(len(y)):
#        x.origin_taz.loc[x.trip_origin_id==y.node_id[i]]=y.taz[i]
#        x.dest_taz.loc[x.trip_dest_id==y.node_id[i]]=y.taz[i]    
    
    x[['hh_s','mm_s','ss_s']] = x.arrival_time.str.split(":",expand=True,) ## Splitting the start_time into h, m and s
#    x[['hh_e','mm_e','ss_e']] = x.end_time.str.split(".",expand=True,) ## Splitting the end_time into h, m and s
    
#    tt['d']=tt.index
#    tt.d=tt.d.astype(str)
#    tt.iloc[(1,161), 'd']
    
    ## Converting the h, m and s into integers
    x.hh_s=x.hh_s.astype(int)
    x.mm_s=x.mm_s.astype(int)
    x.ss_s=x.ss_s.astype(int)
#    x.hh_e=x.hh_e.astype(int)
#    x.mm_e=x.mm_e.astype(int)
#    x.ss_e=x.ss_e.astype(int)
#    

    x['arrival_time_s']=(x.hh_s*60+x.mm_s)*60+x.ss_s ## Adding a new column to store the start_time in seconds
#    x['end_time_s']=(x.hh_e*60+x.mm_e)*60+x.ss_e ## Adding a new column to store the end_time in seconds
#    x=x.drop(['hh_s','mm_s','ss_s','hh_e','mm_e','ss_e'], axis=1)
    x=x.drop(['hh_s','mm_s','ss_s'], axis=1)
    
    
    x=x.sort_values(['arrival_time_s'])## Removing the h, m and s columns
    x=x.reset_index(drop=True) 
    
    for interval in index_column(5).columns:
        c=pd.DataFrame(index=taz_wt.index)
        c[interval]=0
        
        d=x[x.arrival_time_s>=interval[0]]
        d=d[d.arrival_time_s<= interval[1]]
        
       
        if len(d)!=0:
            
            d=d.set_index(['zone'])
            
            for index in d.index:
                 c.loc[index,:]=round(d.waiting_time[index].mean(),0) 
                 
#            else: 
#              continue               
#                 taz_tt.loc[(index[0],index[1]),(interval[0],interval[1])]
#                 taz_tt.loc[:,(0,299)]
        taz_wt[interval]=c[interval]


    for index in taz_wt.index:
         taz_wt.loc[index,:]=taz_wt.loc[index,:].where(taz_wt.loc[index,:]!=0,np.sum(np.array(taz_wt.loc[index,:]))/np.count_nonzero(np.array(taz_wt.loc[index,:])))
    taz_wt=taz_wt.round(0)
#    taz_wt=taz_wt.T.to_dict()
 
#    for column in taz_wt.columns:
#        if column[0]>=27000 and column[1]<=34200:## peak hours 7:30-09:30 am (between 4-8 min)
#            mu, sigma = 360, 60 # mean and standard deviation 
#            taz_wt[column] = np.round(np.random.normal(mu, sigma, len(taz_wt)),0)
#        elif column[0]>= 61200  and column[1]<=72000: ##05:00-08:00 pm (between 3-7 min)
#            mu, sigma = 300, 60 # mean and standard deviation 
#            taz_wt[column] = np.round(np.random.normal(mu, sigma, len(taz_wt)),0)
#        else: ## off peak hours: the rest of intervals
#            mu, sigma = 240, 60 ## between 1-5 min
#            taz_wt[column] = np.round(np.random.normal(mu, sigma, len(taz_wt)),0)
            
#        
#    for zone in taz_wt.index:
#        b=gen_rand_wt() ## generates a df with with random waiting times in s for the 288 5 min intervals
#        b.columns=index_column(5).columns ## sets the columns names as as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
#        b['zone_id']=zone ## adds a new column with the zone id
#        b=b.set_index('zone_id') # sets the zone id as the index of b
#        taz_wt.loc[zone,:]=b.loc[zone,:] ## assigns the randon waiting times to the taz_wt
#     
#    y=np.arange(1,289)    
#    plt.scatter(gen_rand_wt(), y, s=np.pi*3, c=(0,0,0), alpha=0.5)

    return(taz_wt)

def gen_shar_ehail_tt_dict():
    
    a=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
    a.zone_id=a.zone_id.astype(str)
    a['incoming_node']=a.zone_id
    b=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
    b.zone_id=b.zone_id.astype(str)
    b['outgoing_node']=b.zone_id
    
   ## Adding the label 'i' to the incoming nodes
    for index in a.index:
        a.incoming_node[index]=a.incoming_node[index]+'i'

     ## Adding the label 'o' to the outgoing nodes    
    for index in b.index:
        b.outgoing_node[index]=b.outgoing_node[index]+'o'
    
    taz_pairs=pd.DataFrame(columns=['from_node','to_node','from_zone','to_zone'])
    
    
    for i in b.index:
        for j in a.index:
#            if b.zone_id[i]!=a.zone_id[j]:
            taz_pairs=taz_pairs.append({'from_node':a.incoming_node[j], 'to_node': b.outgoing_node[i], 'from_zone':a.zone_id[j], 'to_zone':b.zone_id[i]}, ignore_index=True)
#            else:
#                taz_pairs=taz_pairs.append({'from_node':a.incoming_node[j], 'to_node': b.outgoing_node[i], 'from_zone':a.zone_id[j], 'to_zone':b.zone_id[i]}, ignore_index=True)
#    
#           
#    a=a.append(b)
#    taz=pd.read_csv('taz_2012.csv', delimiter=',',index_col=False)
#    taz_pairs=pd.DataFrame([p for p in itertools.product(a.zone_id, repeat=2)])
#    taz_pairs[0]=taz_pairs[0].astype(str)
#    taz_pairs[1]=taz_pairs[1].astype(str)
#    taz_tt=pd.DataFrame(columns=index_column(5).columns)
#    taz_tt=pd.DataFrame()
#    taz_tt['origin_taz']=taz_pairs[0]
#    taz_tt['dest_taz']=taz_pairs[1]
    
    taz_tt=pd.DataFrame(columns=index_column(5).columns)
    taz_tt['from_node']=taz_pairs['from_node']
    taz_tt['to_node']=taz_pairs['to_node']
    taz_tt=taz_tt.set_index(['from_node','to_node'])
    
 
    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
    trips.columns = ['person_id','trip_origin_node','trip_dest_node','from_zone', 'to_zone','subtrip_origin_type','subtrip_dest_type','travel_mode','arrival_time','travel_time','pt_line']
    
    y=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)
#    y.node_id=y.node_id.astype(str)
#    y.taz=y.taz.astype(str)
    
    
    x=trips.loc[(trips.travel_mode=='ON_SMS_Pool_Veh')|(trips.travel_mode=='ON_RAIL_SMS_Pool_Veh')]
    x=x.reset_index(drop=True)
    x.from_zone=x.from_zone.astype(int)
    x.to_zone=x.to_zone.astype(int)
    
    x.from_zone=x.from_zone.replace(list(y.node_id),list(y.taz))
    x.to_zone=x.to_zone.replace(list(y.node_id),list(y.taz))
    
    x.from_zone=x.from_zone.astype(str)
    x.to_zone=x.to_zone.astype(str)
    
    x['from_taz']=x.from_zone
    x['to_taz']=x.to_zone
    
    x.from_zone=x.from_zone+'i'
    x.to_zone=x.to_zone+'o'
    
#    x.from_zone[x.from_taz==x.to_taz]=x.from_zone[x.from_taz==x.to_taz]+'i'
#    x.to_zone[x.from_taz==x.to_taz]=x.to_zone[x.from_taz==x.to_taz]+'o'
    
    x=x.drop(['from_taz','to_taz'], axis=1)

#    x['from_zone']=0
#    x['to_zone']=0
#    x.trip_origin_id=x.trip_origin_id.astype(str)
#    x.trip_dest_id=x.trip_dest_id.astype(str)
    

#    for i in range(len(y)):
#        x.origin_taz.loc[x.trip_origin_id==y.node_id[i]]=y.taz[i]
#        x.dest_taz.loc[x.trip_dest_id==y.node_id[i]]=y.taz[i]    
    
    x[['hh_s','mm_s','ss_s']] = x.arrival_time.str.split(":",expand=True,) ## Splitting the start_time into h, m and s
#    x[['hh_e','mm_e','ss_e']] = x.end_time.str.split(".",expand=True,) ## Splitting the end_time into h, m and s
    
#    tt['d']=tt.index
#    tt.d=tt.d.astype(str)
#    tt.iloc[(1,161), 'd']
    
    ## Converting the h, m and s into integers
    x.hh_s=x.hh_s.astype(int)
    x.mm_s=x.mm_s.astype(int)
    x.ss_s=x.ss_s.astype(int)
#    x.hh_e=x.hh_e.astype(int)
#    x.mm_e=x.mm_e.astype(int)
#    x.ss_e=x.ss_e.astype(int)
#    

    x['arrival_time_s']=(x.hh_s*60+x.mm_s)*60+x.ss_s ## Adding a new column to store the start_time in seconds
#    x['end_time_s']=(x.hh_e*60+x.mm_e)*60+x.ss_e ## Adding a new column to store the end_time in seconds
#    x=x.drop(['hh_s','mm_s','ss_s','hh_e','mm_e','ss_e'], axis=1)
    x=x.drop(['hh_s','mm_s','ss_s'], axis=1)
    
    
    x=x.sort_values(['arrival_time_s'])## Removing the h, m and s columns
    x=x.reset_index(drop=True)
#    y=y.set_index([('origin_taz','destination_taz')])
#    start=time.time() 
    for interval in index_column(5).columns:
        c=pd.DataFrame(index=taz_tt.index)
        c[interval]=0
        
        d=x[x.arrival_time_s>=interval[0]]
        d=d[d.arrival_time_s<= interval[1]]
        
       
        if len(d)!=0:
            
            d=d.set_index(['from_zone','to_zone'])
            
            for index in d.index:
                 c.loc[index,:]=round(d.travel_time[index].mean(),0) 
                 
#            else: 
#              continue               
#                 taz_tt.loc[(index[0],index[1]),(interval[0],interval[1])]
#                 taz_tt.loc[:,(0,299)]
        taz_tt[interval]=c[interval]


    for index in taz_tt.index:
         taz_tt.loc[index,:]=taz_tt.loc[index,:].where(taz_tt.loc[index,:]!=0,np.sum(np.array(taz_tt.loc[index,:]))/np.count_nonzero(np.array(taz_tt.loc[index,:])))
    taz_tt=taz_tt.round(0)
    taz_tt=taz_tt.fillna(0)
#    taz_tt=taz_tt.T.to_dict()
   
    return(taz_tt)   
         
def gen_shar_ehail_wt_dict(): ##a:tt_dual
    
    ## importing the taz 
    taz=pd.read_csv('taz_2012.csv', delimiter=',',index_col=False)
    
    ##creates a df with the same columns as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
    taz_wt=pd.DataFrame(columns=index_column(5).columns)##creates a df with the same columns as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
    taz_wt['zone_id']=taz.zone_id ##adding a new column with the zone id
    taz_wt.zone_id= taz_wt.zone_id.astype(str) ## converting the zone id to str
    taz_wt=taz_wt.set_index('zone_id') ## sets the zone id as the index of taz_wt
    
#    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
    trips.columns = ['person_id','trip_origin_node','trip_dest_node','from_zone', 'to_zone','subtrip_origin_type','subtrip_dest_type','travel_mode','arrival_time','travel_time','pt_line']
    
    y=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)
#    y.node_id=y.node_id.astype(str)
#    y.taz=y.taz.astype(str)
    
    
    x=trips.loc[(trips.travel_mode=='WAIT_SMS_Pool')|(trips.travel_mode=='WAIT_RAIL_SMS_Pool')]
    x=x.reset_index(drop=True)
    x.from_zone=x.from_zone.astype(int)
    x=x.drop(['to_zone'], axis=1)
   
    
    
    x.from_zone=x.from_zone.replace(list(y.node_id),list(y.taz))
    x.from_zone=x.from_zone.astype(str)  
    x=x.rename(columns={'from_zone':'zone', 'travel_time':'waiting_time'})
    


#    x['from_zone']=0
#    x['to_zone']=0
#    x.trip_origin_id=x.trip_origin_id.astype(str)
#    x.trip_dest_id=x.trip_dest_id.astype(str)
    

#    for i in range(len(y)):
#        x.origin_taz.loc[x.trip_origin_id==y.node_id[i]]=y.taz[i]
#        x.dest_taz.loc[x.trip_dest_id==y.node_id[i]]=y.taz[i]    
    
    x[['hh_s','mm_s','ss_s']] = x.arrival_time.str.split(":",expand=True,) ## Splitting the start_time into h, m and s
#    x[['hh_e','mm_e','ss_e']] = x.end_time.str.split(".",expand=True,) ## Splitting the end_time into h, m and s
    
#    tt['d']=tt.index
#    tt.d=tt.d.astype(str)
#    tt.iloc[(1,161), 'd']
    
    ## Converting the h, m and s into integers
    x.hh_s=x.hh_s.astype(int)
    x.mm_s=x.mm_s.astype(int)
    x.ss_s=x.ss_s.astype(int)
#    x.hh_e=x.hh_e.astype(int)
#    x.mm_e=x.mm_e.astype(int)
#    x.ss_e=x.ss_e.astype(int)
#    

    x['arrival_time_s']=(x.hh_s*60+x.mm_s)*60+x.ss_s ## Adding a new column to store the start_time in seconds
#    x['end_time_s']=(x.hh_e*60+x.mm_e)*60+x.ss_e ## Adding a new column to store the end_time in seconds
#    x=x.drop(['hh_s','mm_s','ss_s','hh_e','mm_e','ss_e'], axis=1)
    x=x.drop(['hh_s','mm_s','ss_s'], axis=1)
    
    
    x=x.sort_values(['arrival_time_s'])## Removing the h, m and s columns
    x=x.reset_index(drop=True) 
    
    for interval in index_column(5).columns:
        c=pd.DataFrame(index=taz_wt.index)
        c[interval]=0
        
        d=x[x.arrival_time_s>=interval[0]]
        d=d[d.arrival_time_s<= interval[1]]
        
       
        if len(d)!=0:
            
            d=d.set_index(['zone'])
            
            for index in d.index:
                 c.loc[index,:]=round(d.waiting_time[index].mean(),0) 
                 
#            else: 
#              continue               
#                 taz_tt.loc[(index[0],index[1]),(interval[0],interval[1])]
#                 taz_tt.loc[:,(0,299)]
        taz_wt[interval]=c[interval]


    for index in taz_wt.index:
         taz_wt.loc[index,:]=taz_wt.loc[index,:].where(taz_wt.loc[index,:]!=0,np.sum(np.array(taz_wt.loc[index,:]))/np.count_nonzero(np.array(taz_wt.loc[index,:])))
    taz_wt=taz_wt.round(0)
#    taz_wt=taz_wt.T.to_dict()
 
#    for column in taz_wt.columns:
#        if column[0]>=27000 and column[1]<=34200:## peak hours 7:30-09:30 am (between 4-8 min)
#            mu, sigma = 360, 60 # mean and standard deviation 
#            taz_wt[column] = np.round(np.random.normal(mu, sigma, len(taz_wt)),0)
#        elif column[0]>= 61200  and column[1]<=72000: ##05:00-08:00 pm (between 3-7 min)
#            mu, sigma = 300, 60 # mean and standard deviation 
#            taz_wt[column] = np.round(np.random.normal(mu, sigma, len(taz_wt)),0)
#        else: ## off peak hours: the rest of intervals
#            mu, sigma = 240, 60 ## between 1-5 min
#            taz_wt[column] = np.round(np.random.normal(mu, sigma, len(taz_wt)),0)
            
#        
#    for zone in taz_wt.index:
#        b=gen_rand_wt() ## generates a df with with random waiting times in s for the 288 5 min intervals
#        b.columns=index_column(5).columns ## sets the columns names as as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
#        b['zone_id']=zone ## adds a new column with the zone id
#        b=b.set_index('zone_id') # sets the zone id as the index of b
#        taz_wt.loc[zone,:]=b.loc[zone,:] ## assigns the randon waiting times to the taz_wt
#     
#    y=np.arange(1,289)    
#    plt.scatter(gen_rand_wt(), y, s=np.pi*3, c=(0,0,0), alpha=0.5)

    return(taz_wt)


def gen_on_demand_dist_dict(mode):
    dist=pd.read_csv('amcosts.csv', delimiter=',',index_col=False, usecols=[0,1,2])
   
    dist_iz=pd.DataFrame(dist.origin_zone.unique(), columns=['origin_zone'])
    dist_iz=dist_iz.sort_values('origin_zone')
    dist_iz=dist_iz.reset_index(drop=True)
    dist_iz['destination_zone']=dist_iz.origin_zone
    dist_iz['distance']=0
    
    dist=dist.append(dist_iz,ignore_index=True)
    dist=dist.sort_values(['origin_zone','destination_zone'])
    dist=dist.reset_index(drop=True)
    dist=dist.set_index(['origin_zone','destination_zone'])  
    
    subtrip= pd.read_csv('subtrip_metrics.csv', delimiter=',', usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13],index_col=False)
    subtrip.columns = ['person_id','trip_id','subtrip_id','origin_type', 'origin_node','origin_zone','destination_type','destination_node','destination_zone','travel_mode','start_time','end_time','travel_time','total_distance']
    y=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)
    if 0 in dist.distance.unique():## Taxi
        
        x=subtrip[(subtrip.travel_mode=='TaxiTravel')|(subtrip.travel_mode=='SMS_Taxi')|(subtrip.travel_mode=='Rail_SMS_Taxi')|(subtrip.travel_mode=='SMS_Pool_Taxi')|(subtrip.travel_mode=='Rail_SMS_Pool_Taxi')]
        x=x.reset_index(drop=True)
        
        x.origin_zone=x.origin_zone.astype(int)
        x.destination_zone=x.destination_zone.astype(int)
        x.origin_node=x.origin_node.astype(int)
        x.destination_node=x.destination_node.astype(int)

        x.origin_zone=x.origin_node.replace(list(y.node_id),list(y.taz))
        x.destination_zone=x.destination_node.replace(list(y.node_id),list(y.taz))
 
      
        for pair in dist[dist.distance==0].index:
            if len(x[(x.origin_zone==pair[0])&(x.destination_zone==pair[1])])!=0:
                dist.distance[pair]=(x[(x.origin_zone==pair[0])&(x.destination_zone==pair[1])].total_distance.mean())/1000
    
    if 0 in dist.distance.unique():## SMS_taxi 
      x=subtrip[(subtrip.travel_mode=='SMS_Taxi')|(subtrip.travel_mode=='Rail_SMS_Taxi')]
      x=x.reset_index(drop=True)
        
      x.origin_zone=x.origin_zone.astype(int)
      x.destination_zone=x.destination_zone.astype(int)
      x.origin_node=x.origin_node.astype(int)
      x.destination_node=x.destination_node.astype(int)
      x.origin_zone=x.origin_node.replace(list(y.node_id),list(y.taz))
      x.destination_zone=x.destination_node.replace(list(y.node_id),list(y.taz))
      
      for pair in dist[dist.distance==0].index:
           if len(x[(x.origin_zone==pair[0])&(x.destination_zone==pair[1])])!=0:
               dist.distance[pair]=(x[(x.origin_zone==pair[0])&(x.destination_zone==pair[1])].total_distance.mean())/1000
#    
#    if 0 in dist.distance.unique():
#     x=subtrip[(subtrip.travel_mode=='Car')]
#        
#     x.origin_zone=x.origin_zone.astype(int)
#     x.destination_zone=x.destination_zone.astype(int)
#     x.origin_node=x.origin_node.astype(int)
#     x.destination_node=x.destination_node.astype(int)
#     x.origin_zone=x.origin_node.replace(list(y.node_id),list(y.taz))
#     x.destination_zone=x.destination_node.replace(list(y.node_id),list(y.taz))
#      
#     for pair in dist[dist.distance==0].index:
#         if len(x[(x.origin_zone==pair[0])&(x.destination_zone==pair[1])])!=0:
#             dist.distance[pair]=(x[(x.origin_zone==pair[0])&(x.destination_zone==pair[1])].total_distance.mean())/1000
#    
#    
#    if 0 in dist.distance.unique():
#        x=subtrip[(subtrip.travel_mode=='SMS_Pool_Taxi')|(subtrip.travel_mode=='Rail_SMS_Pool_Taxi')]
#        
#        x.origin_zone=x.origin_zone.astype(int)
#        x.destination_zone=x.destination_zone.astype(int)
#        x.origin_node=x.origin_node.astype(int)
#        x.destination_node=x.destination_node.astype(int)
#        x.origin_zone=x.origin_node.replace(list(y.node_id),list(y.taz))
#        x.destination_zone=x.destination_node.replace(list(y.node_id),list(y.taz))
#        
#        for pair in dist[dist.distance==0].index:
#            if len(x[(x.origin_zone==pair[0])&(x.destination_zone==pair[1])])!=0:
#                dist.distance[pair]=dist.distance[pair]=(x[(x.origin_zone==pair[0])&(x.destination_zone==pair[1])].total_distance.mean())/1000
#    
#        
    dist.distance[(18,18)]=(dist.distance[(18,19)]+dist.distance[(18,16)]+dist.distance[(18,17)]+dist.distance[(19,18)]+dist.distance[(16,18)]+dist.distance[(17,18)])/6
    dist.distance[(11,11)]=(dist.distance[(11,10)]+dist.distance[(11,15)]+dist.distance[(11,12)]+dist.distance[(10,11)]+dist.distance[(15,11)]+dist.distance[(12,11)])/6
    dist.distance[(22,22)]=(dist.distance[(22,21)]+dist.distance[(22,1)]+dist.distance[(22,14)]+dist.distance[(21,22)]+dist.distance[(1,22)]+dist.distance[(14,22)])/6
    
    if mode=='taxi':
        
        dist=dist.reset_index()
    
        dist.origin_zone='t'+dist.origin_zone.astype(str)+'i'
        dist.destination_zone='t'+dist.destination_zone.astype(str)+'o' 
                      
        dist=dist.set_index(['origin_zone','destination_zone'])  
     
    elif mode=='single_ehail':
         
        dist=dist.reset_index()
    
        dist.origin_zone='sin'+dist.origin_zone.astype(str)+'i'
        dist.destination_zone='sin'+dist.destination_zone.astype(str)+'o' 
                      
        dist=dist.set_index(['origin_zone','destination_zone'])  
     
    elif mode=='shared_ehail':
        dist=dist.reset_index()
    
        dist.origin_zone='shar'+dist.origin_zone.astype(str)+'i'
        dist.destination_zone='shar'+dist.destination_zone.astype(str)+'o' 
                      
        dist=dist.set_index(['origin_zone','destination_zone'])  
    
    
    dist=dist.T.to_dict()
      
                    
    return(dist)
      

def gen_ehail_cost_dict(dict_tt,tt_u, mode, service): ## mode: taxi, service: normal/minivan
    ## tt_u: dist_dual

    a=pd.DataFrame.from_dict(dict_tt, orient='index')

    dist=pd.DataFrame.from_dict(tt_u, orient='index')

    
    
    
    if mode=='taxi' and service=='normal':
        cost=pd.DataFrame(39+8.5*dist.to_numpy()+5.75*a.to_numpy()/60, columns=a.columns)
        cost=cost.set_index(a.index)
        cost=cost.round(2)
    
        
    elif mode=='taxi' and service=='minivan':
        cost=pd.DataFrame(69+12*dist.to_numpy()+6.67*a.to_numpy()/60, columns=a.columns)
        cost=cost.set_index(a.index)
        cost=cost.round(2)
    
    
        
    cost=cost.T.to_dict()

    
    return(cost)     


def add_ehail_nodes(G,a):## a: taz_wt
   
#    a=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
#    a.zone_id=a.zone_id.astype(str)
#    a['incoming_node']=a.zone_id
#    b=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
#    b.zone_id=b.zone_id.astype(str)
#    b['outgoing_node']=b.zone_id
    

   ## Adding the label 'i' to the incoming nodes
    for node in a.keys():
#        a.incoming_node[index]=a.incoming_node[index]+'i'
#        G.add_node(a.incoming_node[index],taz=a.zone_id[index])
        G.add_node(node+'i', zone=node, node_type='taxi_node', node_graph_type='taxi_graph')
        G.add_node(node+'o', zone=node, node_type='taxi_node', node_graph_type='taxi_graph')
     ## Adding the label 'o' to the outgoing nodes    
#    for index in b.index:
#        b.outgoing_node[index]=b.outgoing_node[index]+'o'
#        G.add_node(b.outgoing_node[index],taz=b.zone_id[index])  
    
    
    ## Add the incoming nodes
#    for index in a.index:
#        G.add_node(a.incoming_node[index],taz=a.zone_id[index])
#    ## Add the outging nodes
#    for index in b.index:
#        G.add_node(b.outgoing_node[index],taz=b.zone_id[index])    
#        
        
       
       
#    b=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)
#    b.node_id=b.node_id.astype(str)
#    b.taz=b.taz.astype(str)
#    
#    for i in range(len(a['id'])):
#        G.add_node(a['id'][i], pos=(a['x'][i],a['y'][i]))
#    
#    for node_id, taz in zip(b.node_id, b.taz):
#        G.add_node(node_id, taz=taz)
#        
    return(G)  
    
    
    
def add_ehail_edges(G,a,b,c,d): ## a: taz_tt b: taz_wt, c:taz_dist, d=taz_cost
    
    
    for edge in a.keys():
        G.add_edge(*edge, zone=(edge[0][0:len(edge[0])-1],edge[1][0:len(edge[1])-1]), in_vehicle_tt=a[edge], taxi_wait_time=b[edge[0][0:len(edge[0])-1]], distance=c[edge]['distance'], taxi_cost=d[edge], walk_tt=0, edge_type='taxi_edge') 
#    a=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
#    a.zone_id=a.zone_id.astype(str)
#    a['incoming_node']=a.zone_id
#    b=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
#    b.zone_id=b.zone_id.astype(str)
#    b['outgoing_node']=b.zone_id
    
   ## Adding the label 'i' to the incoming nodes
#    for index in a.index:
#        a.incoming_node[index]=a.incoming_node[index]+'i'
#
#     ## Adding the label 'o' to the outgoing nodes    
#    for index in b.index:
#        b.outgoing_node[index]=b.outgoing_node[index]+'o'
#     
#    for i in b.index:
#        for j in a.index:
#            if b.zone_id[i]!=a.zone_id[j]:
#                G.add_edge(b.outgoing_node[i],a.incoming_node[j], taz=(b.zone_id[i],a.zone_id[j])) 
#            else:
#                G.add_edge(a.incoming_node[j],b.outgoing_node[i], taz=(b.zone_id[i],a.zone_id[j]))
    
    

    
#    
#    c=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)
#    c.node_id=c.node_id.astype(str)
#    c.taz=c.taz.astype(str)
#    
##    for origin_id in c.node_id:
##        for dest_id in c[c.node_id!=origin_id].node_id:
##            print(c.taz[c.node_id==origin_id])
##          G.add_edge(origin_id,dest_id, taz=())
#    for i in range(len(c)):
#        for j in range(len(c)):
#            if i!=j:   
#              G.add_edge(c.node_id[i],c.node_id[j], taz=(c.taz[i],c.taz[j]))   
                
            
    return(G)
    
 
    
def add_ehail_nodes_att(G,a): ## dict of waiting times , taz__tt
    for node in G.nodes.data():
        G.add_node(node[0], wt=a[node[1]['taz']])
    
def add_ehail_edges_att(G,a):
    for edge in G.edges.data():
        print(edge)
        G.add_edge(edge[0],edge[1], tt=a[edge[2]['taz']])
        
        
    
        G.add_node(node[0], wt=a[node[1]['taz']])
    
    
def gen_rand_wt(): ## function that generates random waiting times per 288 5 min interval during a day
                    ## with peaks points at the peak hours
    ## creating random waiting times
    
   
    ## between 00:00 and 03:00
    a=np.random.randint(60,180, size=36)
    a=-np.sort(-a)
    ## between 03:00-06:00
    b=np.random.randint(60,240, size=36)
    b=np.sort(b)
    

    ## between 06:00-08:30
    c=np.random.randint(240,900, size=30)
    c=np.sort(c)
    
    ##• between 08:30-13:30
    d=np.random.randint(180,900, size=60)
    d=-np.sort(-d)
    
    ## between 13:30-19:00
    e=np.random.randint(180,900, size=66)
    e=np.sort(e)
    
    ## between 19:00-23:59 
    f=np.random.randint(180,900, size=60)
    f=-np.sort(-f)
    ## creating a list that contains all the intervals
    l=[]
    l.append(a)
    l.append(b)
    l.append(c)
    l.append(d)
    l.append(e)
    l.append(f)
    
    ## creating an empty array where to concatenate all 288observations 
    y=np.empty(0)
    for array in l:
        y=np.concatenate((y,array))
    y=pd.DataFrame(y.reshape(-1,len(y))) ## convertinf the array to df 
    return(y) 
    
 # 
#    ## Creates two columns for the start and end times in seconds. 
#    tt['start_time_s']=0
#    tt['end_time_s']=0
    
#    ##Storing the unique time intervals
#    a=pd.DataFrame(tt.start_time.drop_duplicates(keep='first')) ## Storing the unique 288 5-min intervals
#    a[['hh_s','mm_s','ss_s']] = a.start_time.str.split(":",expand=True,)
#    a['end_time']=pd.DataFrame(tt.end_time.drop_duplicates(keep='first'))
#    a['start_time_s']=np.nan
#    a['end_time_s']=np.nan
#    a=a.reset_index(drop=True)   
     #Converting the start and end times interval to seconds
    
         
#    for j in range(len(a)):
#        h=float(a.start_time[j][0:2])
#        m=float(a.start_time[j][3:5])
#        s=float(a.start_time[j][6:8])
#        ts=(h*60+m)*60+s
#            
#        hb=float(a.end_time[j][0:2])
#        mb=float(a.end_time[j][3:5])
#        sb=float(a.end_time[j][6:8])
#        tsb=(hb*60+mb)*60+sb   
#        
#        a.iloc[j,2]=ts
#        a.iloc[j,3]=tsb
   
     
    ## tt:  Converting the start and end times to seconds
#    start=time.time() 
#    for i in range (len(a)):
#        ## for all the different pairs of time intervals , in case the time interval is the same, assigns 
#        ## to tt the time intervals in seconds
#        tt.loc[:,'start_time_s'][tt.loc[:,'start_time']==a.loc[i,'start_time']]=a.loc[i,'start_time_s']
#        tt.loc[:,'end_time_s'][tt.loc[:,'end_time']==a.loc[i,'end_time']]=a.loc[i,'end_time_s']  
#        
#    end=time.time()
#    print('Running time: %f min' %((end-start)/60))    
        
     
#    start=time.time()    
#    for j in range(len(tt)):
#         for i in range(len(a)):
#            if tt.start_time[j]==a.start_time[i]:
#                tt.start_time_s[j]=a.start_time_s[i]
#            if tt.end_time[j]==a.end_time[i]:
#                tt.end_time_s[j]=a.end_time_s[i]    
#    end=time.time()
#    print('Running time: %f min' %((end-start)/60))    
     


  
     
#    ## Importing the turnings groups
#    tt_u=pd.read_csv('Road_turning_groups.csv', delimiter=',', usecols=[2,3], index_col=('from_link','to_link'))  ## Importing turning groups data (from link to link)
#    ## Adding a new column for the end time interval
#    tt_u['travel_time']=np.nan ## Adding a new column for the default travel time
#    tt_u['distance']=np.nan  ## Adding a new column for the length
#    tt_u=tt_u.sort_index()
##    tt_u= tt_u.sort_values(['from_link','to_link','start_time','end_time']) ## sorting the values
##    tt_u=tt_u.reset_index(drop=True) #Reseting the index
#    
#    ## Assigning the default travel time and the length to the different turnings
#     
#    for i in range(len(tt_d)):
#        for link in tt_u.index:  
#            if link[0]==tt_d.loc[i,'link_id']:
#                tt_u.loc[link,'travel_time']=tt_d.loc[i,'travel_time']
#                tt_u.loc[link,'distance']=tt_d.loc[i,'distance']       
   
#     ##Storing the unique time intervals
#    
#    l=l_dual
#    
#    a=pd.DataFrame(tt.start_time_s.drop_duplicates(keep='first'))
#    a['end_time_s']=tt.end_time_s.drop_duplicates(keep='first')
#    a=a.reset_index(drop=True)
#    
#    
#    tt_dum_dict=pd.DataFrame(l)
#    tt_dum_dict=tt_dum_dict.set_index(['id','to_node'])
#    tt_dum_dict=tt_dum_dict.drop(['from_node','weight','length'], axis=1)
#  
#    for i in range(len(a)):
#        tt_dum_dict[(a.start_time_s[i],a.end_time_s[i])]=0
#    
#    tt_dum_dict=tt_dum_dict.to_dict()
#    tt_dum_dict=pd.DataFrame(tt_dum_dict)  
#    
#    for i in tt_dum_dict.index:
#        for j in tt.index:
#            if i[0]==j[0]:
#                tt_dum_dict.loc[i,:]=tt.travel_time[j]
#
#       
#           
#    return(tt_dum_dict)    




#def update_dicts_tt(dict_tt, dum_dict_tt,tt,t,H,y): #INPUT: dict_tt, dum_dict_tt=dict of dummy destinationes edges tt, tt:df with all the i min interval per link, 
#                                 # t: time at the update is done, H: time horizon to update in min
#     
#    
#    
#    t='08:07:00'                # i: interval of the travel time per links in minutes
#    H=15
#    y=5
#    H=H*60                             
#    h=float(t[0:2])
#    m=float(t[3:5])
#    s=float(t[6:8])
#    ts=(h*60+m)*60+s
#    
#    
#    
#    
#    ##Storing the pairs of links (521 turnings)
#    links=list(dict_tt.keys())
#    dummy_links=list(dum_dict_tt.keys())
#    dl=pd.DataFrame(dummy_links,columns=['from_link','to_link'] )
#    dl['travel_time']=np.nan
#    ##Extracting the travel times of the intervals of interest
#    #p: time interval used to predict (to replicate)
#    #x: time intervals whitin the time horizon 
#    # tt of p time interval is copied in the x times intervals
#   
#    if ts<y*60:   #Taking the (23:55,23:59:59) interval
#        p=tt[(tt.end_time_s>=86400-ts)]
##        p=p.reset_index(drop=True)
#        x=tt[(tt.start_time_s>=ts-y*60)]
#        x=x[(tt.start_time_s<ts+H)]
#        x=x.reset_index(drop=True)
#          
#    else:
#        p=tt[(tt.end_time_s>=ts-y*60)]
#        p=p[(tt.start_time_s<=ts-y*60)]
#        x=tt[(tt.end_time_s>=ts)]
#        x=x[(tt.start_time_s<ts+H)]
#        x=x.reset_index(drop=True)
#    
#    p=p.reset_index(drop=True)
#    links_p=list(zip(list(p.from_link),list(p.to_link)))
#    ## list with the links contained in p
#    
##    # Removing the p links that are different from the 521 turning groups              
#    for tup in links_p:
#        if tup  not in links:
#            print(tup)
#            links_p.remove(tup) 
#    
#            
#    # Checking if the 521 turning groups are in the p interval       
#    for tup in links:
#        if tup  not in links_p:
#            print(tup)       
#   
#    # Removing the p links that are different from the 521 turning groups          
#    for i in range(len(p)):
#        if (p.from_link[i],p.to_link[i]) not in links:
#            p=p.drop(i,axis=0)
#    p=p.reset_index(drop=True)
#    
#    
#    # Removing the x links that are different from the p links
#    for i in range(len(x)):
#        if (x.from_link[i],x.to_link[i]) not in links_p:
#            x=x.drop(i,axis=0)
#    x=x.reset_index(drop=True)
#    
#    
#    for j in range(len(p)):
#        r=x[x.from_link==p.from_link[j]]
#        r=r[x.to_link==p.to_link[j]]
#        r=r.reset_index(drop=True)  
#        for i in  range(len(r)):
#            dict_tt[(r.from_link[i],r.to_link[i])][(r.start_time_s[i],r.end_time_s[i])]=p.travel_time[j]
#   
#    
#    
#    unique_d=np.unique(list(p['from_link']))
#    for unique in unique_d:
#            w=p[p.from_link==unique]
#            for i in range(len(dl)):
#                if unique==dl.from_link[i]:
#                    dl.travel_time[i]=float(w['travel_time'].min())
#        
#
#    for j in range(len(dl)):
#        r=x[x.from_link==dl.from_link[j]]
#        r.loc[:,'from_link']=dl.from_link[j]
#        r.loc[:,'to_link']=dl.to_link[j]
#        r=r.reset_index(drop=True)  
#        for i in  range(len(r)):
#           dum_dict_tt[(r.from_link[i],r.to_link[i])][(r.start_time_s[i],r.end_time_s[i])]=dl.travel_time[j]
#   
#    return(dict_tt,dum_dict_tt)  

##    list=[]        
##    for ind in a.index:
##        list.append(ind[0])
#    
#    unique_d=np.unique(list)
#    
#    for ind in a.index:
#        if ind:
#    a[(1,161)]        
#    for unique in unique_d:
#            for ind in dum_dict_tt.index:
#                if unique==ind[0]:
#                    dl.travel_time[i]=float(w['travel_time'].min())        
#            
#    
#    for col in dict_tt.columns: 
#        if col[1]>=ts-y*60 and col[1]<ts+H+y*60:
#            print(col)
#            dict_tt[(col)]=a[(a.start_time_s[0],a.end_time_s[0])]
#    
     
    
#   
    
#    
#    
#    a=a.set_index(("from_link","to_link"), inplace = True) 
#        else:
#        p=tt[(tt.end_time_s>=ts-y*60)]
#        p=p[(tt.start_time_s<=ts-y*60)]
#        x=tt[(tt.end_time_s>=ts)]
#        x=x[(tt.start_time_s<ts+H)]
#        x=x.reset_index(drop=True)
#    
#        for col in dict_tt.columns
#    ##Storing the pairs of links (521 turnings)
#    links=list(dict_tt.keys())
#    dummy_links=list(dum_dict_tt.keys())
#    dl=pd.DataFrame(dummy_links,columns=['from_link','to_link'] )
#    dl['travel_time']=np.nan
#    ##Extracting the travel times of the intervals of interest
#    #p: time interval used to predict (to replicate)
#    #x: time intervals whitin the time horizon 
#    # tt of p time interval is copied in the x times intervals
#   
#    if ts<y*60:   #Taking the (23:55,23:59:59) interval
#        p=tt[(tt.end_time_s>=86400-ts)]
##        p=p.reset_index(drop=True)
#        x=tt[(tt.start_time_s>=ts-y*60)]
#        x=x[(tt.start_time_s<ts+H)]
#        x=x.reset_index(drop=True)
#          
#    else:
#        p=tt[(tt.end_time_s>=ts-y*60)]
#        p=p[(tt.start_time_s<=ts-y*60)]
#        x=tt[(tt.end_time_s>=ts)]
#        x=x[(tt.start_time_s<ts+H)]
#        x=x.reset_index(drop=True)
#    
#    p=p.reset_index(drop=True)
#    links_p=list(zip(list(p.from_link),list(p.to_link)))
#    ## list with the links contained in p
#    
##    # Removing the p links that are different from the 521 turning groups              
#    for tup in links_p:
#        if tup  not in links:
#            print(tup)
#            links_p.remove(tup) 
#    
#            
#    # Checking if the 521 turning groups are in the p interval       
#    for tup in links:
#        if tup  not in links_p:
#            print(tup)       
#   
#    # Removing the p links that are different from the 521 turning groups          
#    for i in range(len(p)):
#        if (p.from_link[i],p.to_link[i]) not in links:
#            p=p.drop(i,axis=0)
#    p=p.reset_index(drop=True)
#    
#    
#    # Removing the x links that are different from the p links
#    for i in range(len(x)):
#        if (x.from_link[i],x.to_link[i]) not in links_p:
#            x=x.drop(i,axis=0)
#    x=x.reset_index(drop=True)
#    
#    
#    for j in range(len(p)):
#        r=x[x.from_link==p.from_link[j]]
#        r=r[x.to_link==p.to_link[j]]
#        r=r.reset_index(drop=True)  
#        for i in  range(len(r)):
#            dict_tt[(r.from_link[i],r.to_link[i])][(r.start_time_s[i],r.end_time_s[i])]=p.travel_time[j]
#   
#    
#    
#    unique_d=np.unique(list(p['from_link']))
#    for unique in unique_d:
#            w=p[p.from_link==unique]
#            for i in range(len(dl)):
#                if unique==dl.from_link[i]:
#                    dl.travel_time[i]=float(w['travel_time'].min())
#        
#
#    for j in range(len(dl)):
#        r=x[x.from_link==dl.from_link[j]]
#        r.loc[:,'from_link']=dl.from_link[j]
#        r.loc[:,'to_link']=dl.to_link[j]
#        r=r.reset_index(drop=True)  
#        for i in  range(len(r)):
#           dum_dict_tt[(r.from_link[i],r.to_link[i])][(r.start_time_s[i],r.end_time_s[i])]=dl.travel_time[j]              
    ###        
#def update_tt(dict_tt,tt,t,H,y): #INPUT: dict_tt, tt:df with all the i min interval per link, 
#                                 # t: time at the update is done, H: time horizon to update in min
##    t='07:02:00'                # i: interval of the travel time per links in minutes
##    H=120
##    y=5
#    H=H*60                             
#    h=float(t[0:2])
#    m=float(t[3:5])
#    s=float(t[6:8])
#    ts=(h*60+m)*60+s
#    
#    
#    ##Storing the pairs of links (521 turnings)
#    links=list(dict_tt.keys())
#    
#    ##Extracting the travel times of the intervals of interest
#    #p: time interval used to predict (to replicate)
#    #x: time intervals whitin the time horizon 
#    # tt of p time interval is copied in the x times intervals
#   
#    if ts<y*60:   #Taking the (23:55,23:59:59) interval
#        p=tt[(tt.end_time_s>=86400-ts)]
#        p=p.reset_index(drop=True)
#        x=tt[(tt.start_time_s>=ts-y*60)]
#        x=x[(tt.start_time_s<ts+H)]
#        x=x.reset_index(drop=True)
#          
#    else:
#        p=tt[(tt.end_time_s>=ts-y*60)]
#        p=p[(tt.start_time_s<=ts-y*60)]
#        x=tt[(tt.end_time_s>=ts)]
#        x=x[(tt.start_time_s<ts+H)]
#        x=x.reset_index(drop=True)
#    
#    p=p.reset_index(drop=True)
#    links_p=list(zip(list(p.from_link),list(p.to_link))) ## list with the links contained in p
#    
##    # Removing the p links that are different from the 521 turning groups 
##    for tup in links_p:
##        if tup  not in links:
##            print(tup)
##            links_p.remove(tup) 
##            
##    # Checking if the 521 turning groups are in the p interval       
##    for tup in links:
##        if tup  not in links_p:
##            print(tup)       
#   # Removing the p links that are different from the 521 turning groups          
#    for i in range(len(p)):
#        if (p.from_link[i],p.to_link[i]) not in links:
#            p=p.drop(i,axis=0)
#    p=p.reset_index(drop=True)
#    
#    # Removing the x links that are different from the p links
#    for i in range(len(x)):
#        if (x.from_link[i],x.to_link[i]) not in links_p:
#            x=x.drop(i,axis=0)
#    x=x.reset_index(drop=True)
#    
#
#    for j in range(len(p)):
#        r=x[x.from_link==p.from_link[j]]
#        r=r[x.to_link==p.to_link[j]]
#        r=r.reset_index(drop=True)  
#        for i in  range(len(r)):
#            dict_tt[(r.from_link[i],r.to_link[i])]['weight'][(r.start_time_s[i],r.end_time_s[i])]=p.travel_time[j]
#   
#    return(dict_tt)    
##    
#            if p.from_link[i]==x.from_link[j] and p.to_link[i]==x.to_link[j]:
#                x.travel_time[j]=p.travel_time[i]
#                q=q+1
#            if q==H/y+1:
#                break
#    
#    for i in range(len(x)):
#            dict_tt[(x.from_link[i],x.to_link[i])]['weight'][(x.start_time_s[i],x.end_time_s[i])]=x.travel_time[i]
# 
#    
#    start=time.time()
#    m=pd.DataFrame(columns=['from_link', 'to_link', 'start_time','end_time','travel_time','start_time_s','end_time_s'])
#    for pflink, ptlink, ptt in zip(p.from_link, p.to_link, p.travel_time):
##        print(pflink,ptlink,ptt)
#        r=x[x.from_link==pflink]
#        r=r[x.to_link==ptlink]
#        r.travel_time=ptt
#        r=r.reset_index(drop=True)  
#        m=m.append(r)
#    end=time.time()    
#    print('Running time: %f s' %(end-start))  
##    
#    
#    for rflink,rtlink,rstimes,retimes,rtt in zip(r.from_link,r.to_link,r.start_time_s,r.end_time_s,r.travel_time):
#            print(rflink,rtlink,rstimes,retimes,rtt)
#            dict_tt[(rflink,rtlink)]['weight'][(rstimes,retimes)]=rtt
#    end=time.time()    
#    print('Running time: %f s' %(end-start))    
#        
#        
#        
#    for i in range(len(r)):
#            dict_tt[(r.from_link[i],r.to_link[i])]['weight'][(r.start_time_s[i],r.end_time_s[i])]=r.travel_time[i]
#        
#        
#        
#    
#    for xflink,xtlink,xtt in zip(x.from_link,x.to_link,x.travel_time):
#            if pflink==xflink and ptlink==xtlink:
#                x.loc[x['from_link'==xflink]and x['to_link'==xtlink]]
#                xtt=ptt
#    
#    x.travel_time[[x.from_link==1 and x.to_link==161]==True]=0
#    for i in range(len(x)):
#            dict_tt[(x.from_link[i],x.to_link[i])]['weight'][(x.start_time_s[i],x.end_time_s[i])]=x.travel_time[i]
# 
#def gen_ehail_tt_dict():
#    
#    a=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
#    a.zone_id=a.zone_id.astype(str)
#    a['incoming_node']=a.zone_id
#    b=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
#    b.zone_id=b.zone_id.astype(str)
#    b['outgoing_node']=b.zone_id
#    
#   ## Adding the label 'i' to the incoming nodes
#    for index in a.index:
#        a.incoming_node[index]=a.incoming_node[index]+'i'
#
#     ## Adding the label 'o' to the outgoing nodes    
#    for index in b.index:
#        b.outgoing_node[index]=b.outgoing_node[index]+'o'
#    
#    taz_pairs=pd.DataFrame(columns=['from_node','to_node','from_zone','to_zone'])
#    
#    
#    for i in b.index:
#        for j in a.index:
##            if b.zone_id[i]!=a.zone_id[j]:
#            taz_pairs=taz_pairs.append({'from_node':a.incoming_node[j], 'to_node': b.outgoing_node[i], 'from_zone':a.zone_id[j], 'to_zone':b.zone_id[i]}, ignore_index=True)
##            else:
##                taz_pairs=taz_pairs.append({'from_node':a.incoming_node[j], 'to_node': b.outgoing_node[i], 'from_zone':a.zone_id[j], 'to_zone':b.zone_id[i]}, ignore_index=True)
##    
##           
##    a=a.append(b)
##    taz=pd.read_csv('taz_2012.csv', delimiter=',',index_col=False)
##    taz_pairs=pd.DataFrame([p for p in itertools.product(a.zone_id, repeat=2)])
##    taz_pairs[0]=taz_pairs[0].astype(str)
##    taz_pairs[1]=taz_pairs[1].astype(str)
##    taz_tt=pd.DataFrame(columns=index_column(5).columns)
##    taz_tt=pd.DataFrame()
##    taz_tt['origin_taz']=taz_pairs[0]
##    taz_tt['dest_taz']=taz_pairs[1]
#    
##    taz_tt=pd.DataFrame(columns=index_column(5).columns)
#    taz_tt=pd.DataFrame()        
#    taz_tt['from_node']=taz_pairs['from_node']
#    taz_tt['to_node']=taz_pairs['to_node']
#    taz_tt=taz_tt.set_index(['from_node','to_node'])
#    
# 
#    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
#    trips.columns = ['person_id','trip_origin_node','trip_dest_node','from_zone', 'to_zone','subtrip_origin_type','subtrip_dest_type','travel_mode','arrival_time','travel_time','pt_line']
#    
#    y=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)
##    y.node_id=y.node_id.astype(str)
##    y.taz=y.taz.astype(str)
#    
#    
#    x=trips.loc[(trips.travel_mode=='ON_SMS_Veh')|(trips.travel_mode=='ON_RAIL_SMS_Veh')]
#    x=x.reset_index(drop=True)
#    x.from_zone=x.from_zone.astype(int)
#    x.to_zone=x.to_zone.astype(int)
#    
#    x.from_zone=x.from_zone.replace(list(y.node_id),list(y.taz))
#    x.to_zone=x.to_zone.replace(list(y.node_id),list(y.taz))
#    
#    x.from_zone=x.from_zone.astype(str)
#    x.to_zone=x.to_zone.astype(str)
#    
#    x['from_taz']=x.from_zone
#    x['to_taz']=x.to_zone
#    
#    x.from_zone=x.from_zone+'i'
#    x.to_zone=x.to_zone+'o'
#    
##    x.from_zone[x.from_taz==x.to_taz]=x.from_zone[x.from_taz==x.to_taz]+'i'
##    x.to_zone[x.from_taz==x.to_taz]=x.to_zone[x.from_taz==x.to_taz]+'o'
#    
#    x=x.drop(['from_taz','to_taz'], axis=1)
#
##    x['from_zone']=0
##    x['to_zone']=0
##    x.trip_origin_id=x.trip_origin_id.astype(str)
##    x.trip_dest_id=x.trip_dest_id.astype(str)
#    
#
##    for i in range(len(y)):
##        x.origin_taz.loc[x.trip_origin_id==y.node_id[i]]=y.taz[i]
##        x.dest_taz.loc[x.trip_dest_id==y.node_id[i]]=y.taz[i]    
#    
#    x[['hh_s','mm_s','ss_s']] = x.arrival_time.str.split(":",expand=True,) ## Splitting the start_time into h, m and s
##    x[['hh_e','mm_e','ss_e']] = x.end_time.str.split(".",expand=True,) ## Splitting the end_time into h, m and s
#    
##    tt['d']=tt.index
##    tt.d=tt.d.astype(str)
##    tt.iloc[(1,161), 'd']
#    
#    ## Converting the h, m and s into integers
#    x.hh_s=x.hh_s.astype(int)
#    x.mm_s=x.mm_s.astype(int)
#    x.ss_s=x.ss_s.astype(int)
##    x.hh_e=x.hh_e.astype(int)
##    x.mm_e=x.mm_e.astype(int)
##    x.ss_e=x.ss_e.astype(int)
##    
#
#    x['arrival_time_s']=(x.hh_s*60+x.mm_s)*60+x.ss_s ## Adding a new column to store the start_time in seconds
##    x['end_time_s']=(x.hh_e*60+x.mm_e)*60+x.ss_e ## Adding a new column to store the end_time in seconds
##    x=x.drop(['hh_s','mm_s','ss_s','hh_e','mm_e','ss_e'], axis=1)
#    x=x.drop(['hh_s','mm_s','ss_s'], axis=1)
#    
#    
#    x=x.sort_values(['arrival_time_s'])## Removing the h, m and s columns
#    x=x.reset_index(drop=True)
##    y=y.set_index([('origin_taz','destination_taz')])
##    start=time.time() 
#    for interval in index_column(5).columns:
#    
#        c=pd.DataFrame(index=taz_tt.index)
##        taz_tt[interval]=0
#        c[interval]=0
#
#        d=x[x.arrival_time_s>=interval[0]]
#        d=d[d.arrival_time_s<= interval[1]]
#        
#       
#        if len(d)!=0:
#            
#            d=d.set_index(['from_zone','to_zone'])
#            
#            for index in d.index:
#                 c.loc[index,:]=round(d.travel_time[index].mean(),0) 
#                 
##            else: 
##              continue               
##                 taz_tt.loc[(index[0],index[1]),(interval[0],interval[1])]
##                 taz_tt.loc[:,(0,299)]
#        taz_tt[interval]=c[interval]
#
#
#    for index in taz_tt.index:
#         taz_tt.loc[index,:]=taz_tt.loc[index,:].where(taz_tt.loc[index,:]!=0,np.sum(np.array(taz_tt.loc[index,:]))/np.count_nonzero(np.array(taz_tt.loc[index,:])))
#    taz_tt=taz_tt.fillna(0)
#    
#    taz_tt=taz_tt.round(0)
##    taz_tt=taz_tt.T.to_dict()
#
#
#
#    return(taz_tt)   
#
#
## taz_list=pd.DataFrame()
##    taz_list['origin_taz']=0
##    taz_list['destination_taz']=0
##taz_tt['taz_pairs']=0
##    for tazid in taz.zone_id:
##        for tazid2 in taz.zone_id:
###            taz_list.extend([(str(tazid),str(tazid2))])
##            taz_list=taz_list.append({'origin_taz':str(tazid),'destination_taz':str(tazid2)},ignore_index=True)
#
#
##    a=[p for p in itertools.product(taz.zone_id, repeat=2)] #https://stackoverflow.com/questions/3099987/generating-permutations-with-repetitions-in-python
#   
# 
#    
## Print the obtained permutations 
##for i in list(perm): 
##    print(i) 
#    
#    
##    
##    for tazid in list(perm):
###            taz_list.extend([(str(tazid),str(tazid2))])
##        taz_tt=taz_tt.append({'origin_taz':str(tazid[0]),'dest_taz':str(tazid[1])},ignore_index=True)
#
# 
#    
##    
##    subtrip= pd.read_csv('subtrip_metrics.csv', delimiter=',', usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13],index_col=False)
#
##    subtrip.columns = ['person_id','trip_id','subtrip_id','origin_type', 'origin_node','origin_taz','destination_type','destination_node','destination_taz','travel_mode','start_time','end_time','travel_time','total_distance']
##    
##    x=subtrip[subtrip.travel_mode=='TaxiTravel']                             
##end=time.time()
##print('Running time: %f min' %((end-start)/60))
#            
##      dict_tt[(col)]=a[(a.start_time_s[0],a.end_time_s[0])]           
#        
#            
##        for index in y.index.unique():
##            print(index, interval)
##            a=x[x.origin_taz==index[0]]
##            a=a[a.destination_taz==index[1]]
##            a=a[a.end_time_s>=interval[0]]
##            a=a[a.end_time_s<= interval[1]]
##            
##        
##        for index in x.index.unique():
##            if x.end_time_s[index]>=interval[0] and x.end_time_s[index]<= interval[1]:
##                a=a.append(x.loc[index,:])
##                a=a.append(a)        
##        a.origin_taz=a.origin_taz.astype(str)
##        a.destination_taz=a.destination_taz.astype(str)
##        a=a.set_index(['origin_taz','destination_taz'])
##        
##        if len(a)!=0:
##                b=pd.DataFrame(index=taz_tt.index)
##                b[interval]=0
##      
##                for zone in a.index:
##                    b.loc[zone,:]=a.travel_time[zone].mean()
##                for col in b.columns:
##                     taz_tt[(col)]=b
#                     
##                    x.travel_time[x.travel_time==0]
#    
#                    
#            
##          dum_dict_tt[(col)]=b[(b.start_time_s[0],b.end_time_s[0])]
#        
##        if x.e
##        print(interval[1])
##    x=tt[['start_time','end_time','start_time_s','end_time_s','travel_time']] 
#    
#    
#
##a=pd.DataFrame.from_dict(a, orient='index')
#def gen_ehail_wt_dict(): ##a:tt_dual
#    
#    ## importing the taz 
#    taz=pd.read_csv('taz_2012.csv', delimiter=',',index_col=False)
#    
#    ##creates a df with the same columns as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
#    taz_wt=pd.DataFrame(columns=index_column(5).columns)##creates a df with the same columns as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
#    taz_wt['zone_id']=taz.zone_id ##adding a new column with the zone id
#    taz_wt.zone_id= taz_wt.zone_id.astype(str) ## converting the zone id to str
#    taz_wt=taz_wt.set_index('zone_id') ## sets the zone id as the index of taz_wt
#    
##    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
#    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
#    trips.columns = ['person_id','trip_origin_node','trip_dest_node','from_zone', 'to_zone','subtrip_origin_type','subtrip_dest_type','travel_mode','arrival_time','travel_time','pt_line']
#    
#    y=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)
##    y.node_id=y.node_id.astype(str)
##    y.taz=y.taz.astype(str)
#    
#    
#    x=trips.loc[(trips.travel_mode=='WAIT_SMS')|(trips.travel_mode=='WAIT_RAIL_SMS')]
#    x=x.reset_index(drop=True)
#    x.from_zone=x.from_zone.astype(int)
#    x=x.drop(['to_zone'], axis=1)
#   
#    
#    
#    x.from_zone=x.from_zone.replace(list(y.node_id),list(y.taz))
#    x.from_zone=x.from_zone.astype(str)  
#    x=x.rename(columns={'from_zone':'zone', 'travel_time':'waiting_time'})
#    
#
#
##    x['from_zone']=0
##    x['to_zone']=0
##    x.trip_origin_id=x.trip_origin_id.astype(str)
##    x.trip_dest_id=x.trip_dest_id.astype(str)
#    
#
##    for i in range(len(y)):
##        x.origin_taz.loc[x.trip_origin_id==y.node_id[i]]=y.taz[i]
##        x.dest_taz.loc[x.trip_dest_id==y.node_id[i]]=y.taz[i]    
#    
#    x[['hh_s','mm_s','ss_s']] = x.arrival_time.str.split(":",expand=True,) ## Splitting the start_time into h, m and s
##    x[['hh_e','mm_e','ss_e']] = x.end_time.str.split(".",expand=True,) ## Splitting the end_time into h, m and s
#    
##    tt['d']=tt.index
##    tt.d=tt.d.astype(str)
##    tt.iloc[(1,161), 'd']
#    
#    ## Converting the h, m and s into integers
#    x.hh_s=x.hh_s.astype(int)
#    x.mm_s=x.mm_s.astype(int)
#    x.ss_s=x.ss_s.astype(int)
##    x.hh_e=x.hh_e.astype(int)
##    x.mm_e=x.mm_e.astype(int)
##    x.ss_e=x.ss_e.astype(int)
##    
#
#    x['arrival_time_s']=(x.hh_s*60+x.mm_s)*60+x.ss_s ## Adding a new column to store the start_time in seconds
##    x['end_time_s']=(x.hh_e*60+x.mm_e)*60+x.ss_e ## Adding a new column to store the end_time in seconds
##    x=x.drop(['hh_s','mm_s','ss_s','hh_e','mm_e','ss_e'], axis=1)
#    x=x.drop(['hh_s','mm_s','ss_s'], axis=1)
#    
#    
#    x=x.sort_values(['arrival_time_s'])## Removing the h, m and s columns
#    x=x.reset_index(drop=True) 
#    
#    for interval in index_column(5).columns:
#        c=pd.DataFrame(index=taz_wt.index)
#        c[interval]=0
#        
#        d=x[x.arrival_time_s>=interval[0]]
#        d=d[d.arrival_time_s<= interval[1]]
#        
#       
#        if len(d)!=0:
#            
#            d=d.set_index(['zone'])
#            
#            for index in d.index:
#                 c.loc[index,:]=round(d.waiting_time[index].mean(),0) 
#                 
##            else: 
##              continue               
##                 taz_tt.loc[(index[0],index[1]),(interval[0],interval[1])]
##                 taz_tt.loc[:,(0,299)]
#        taz_wt[interval]=c[interval]
#
#
#    for index in taz_wt.index:
#         taz_wt.loc[index,:]=taz_wt.loc[index,:].where(taz_wt.loc[index,:]!=0,np.sum(np.array(taz_wt.loc[index,:]))/np.count_nonzero(np.array(taz_wt.loc[index,:])))
#    taz_wt=taz_wt.round(0)
##    taz_wt=taz_wt.T.to_dict()
# 
##    for column in taz_wt.columns:
##        if column[0]>=27000 and column[1]<=34200:## peak hours 7:30-09:30 am (between 4-8 min)
##            mu, sigma = 360, 60 # mean and standard deviation 
##            taz_wt[column] = np.round(np.random.normal(mu, sigma, len(taz_wt)),0)
##        elif column[0]>= 61200  and column[1]<=72000: ##05:00-08:00 pm (between 3-7 min)
##            mu, sigma = 300, 60 # mean and standard deviation 
##            taz_wt[column] = np.round(np.random.normal(mu, sigma, len(taz_wt)),0)
##        else: ## off peak hours: the rest of intervals
##            mu, sigma = 240, 60 ## between 1-5 min
##            taz_wt[column] = np.round(np.random.normal(mu, sigma, len(taz_wt)),0)
#            
##        
##    for zone in taz_wt.index:
##        b=gen_rand_wt() ## generates a df with with random waiting times in s for the 288 5 min intervals
##        b.columns=index_column(5).columns ## sets the columns names as as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
##        b['zone_id']=zone ## adds a new column with the zone id
##        b=b.set_index('zone_id') # sets the zone id as the index of b
##        taz_wt.loc[zone,:]=b.loc[zone,:] ## assigns the randon waiting times to the taz_wt
##     
##    y=np.arange(1,289)    
##    plt.scatter(gen_rand_wt(), y, s=np.pi*3, c=(0,0,0), alpha=0.5)
#
#    return(taz_wt)
#
#def gen_shar_ehail_tt_dict():
#    
#    a=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
#    a.zone_id=a.zone_id.astype(str)
#    a['incoming_node']=a.zone_id
#    b=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
#    b.zone_id=b.zone_id.astype(str)
#    b['outgoing_node']=b.zone_id
#    
#   ## Adding the label 'i' to the incoming nodes
#    for index in a.index:
#        a.incoming_node[index]=a.incoming_node[index]+'i'
#
#     ## Adding the label 'o' to the outgoing nodes    
#    for index in b.index:
#        b.outgoing_node[index]=b.outgoing_node[index]+'o'
#    
#    taz_pairs=pd.DataFrame(columns=['from_node','to_node','from_zone','to_zone'])
#    
#    
#    for i in b.index:
#        for j in a.index:
##            if b.zone_id[i]!=a.zone_id[j]:
#            taz_pairs=taz_pairs.append({'from_node':a.incoming_node[j], 'to_node': b.outgoing_node[i], 'from_zone':a.zone_id[j], 'to_zone':b.zone_id[i]}, ignore_index=True)
##            else:
##                taz_pairs=taz_pairs.append({'from_node':a.incoming_node[j], 'to_node': b.outgoing_node[i], 'from_zone':a.zone_id[j], 'to_zone':b.zone_id[i]}, ignore_index=True)
##    
##           
##    a=a.append(b)
##    taz=pd.read_csv('taz_2012.csv', delimiter=',',index_col=False)
##    taz_pairs=pd.DataFrame([p for p in itertools.product(a.zone_id, repeat=2)])
##    taz_pairs[0]=taz_pairs[0].astype(str)
##    taz_pairs[1]=taz_pairs[1].astype(str)
##    taz_tt=pd.DataFrame(columns=index_column(5).columns)
##    taz_tt=pd.DataFrame()
##    taz_tt['origin_taz']=taz_pairs[0]
##    taz_tt['dest_taz']=taz_pairs[1]
#    
#    taz_tt=pd.DataFrame(columns=index_column(5).columns)
#    taz_tt['from_node']=taz_pairs['from_node']
#    taz_tt['to_node']=taz_pairs['to_node']
#    taz_tt=taz_tt.set_index(['from_node','to_node'])
#    
# 
#    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
#    trips.columns = ['person_id','trip_origin_node','trip_dest_node','from_zone', 'to_zone','subtrip_origin_type','subtrip_dest_type','travel_mode','arrival_time','travel_time','pt_line']
#    
#    y=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)
##    y.node_id=y.node_id.astype(str)
##    y.taz=y.taz.astype(str)
#    
#    
#    x=trips.loc[(trips.travel_mode=='ON_SMS_Pool_Veh')|(trips.travel_mode=='ON_RAIL_SMS_Pool_Veh')]
#    x=x.reset_index(drop=True)
#    x.from_zone=x.from_zone.astype(int)
#    x.to_zone=x.to_zone.astype(int)
#    
#    x.from_zone=x.from_zone.replace(list(y.node_id),list(y.taz))
#    x.to_zone=x.to_zone.replace(list(y.node_id),list(y.taz))
#    
#    x.from_zone=x.from_zone.astype(str)
#    x.to_zone=x.to_zone.astype(str)
#    
#    x['from_taz']=x.from_zone
#    x['to_taz']=x.to_zone
#    
#    x.from_zone=x.from_zone+'i'
#    x.to_zone=x.to_zone+'o'
#    
##    x.from_zone[x.from_taz==x.to_taz]=x.from_zone[x.from_taz==x.to_taz]+'i'
##    x.to_zone[x.from_taz==x.to_taz]=x.to_zone[x.from_taz==x.to_taz]+'o'
#    
#    x=x.drop(['from_taz','to_taz'], axis=1)
#
##    x['from_zone']=0
##    x['to_zone']=0
##    x.trip_origin_id=x.trip_origin_id.astype(str)
##    x.trip_dest_id=x.trip_dest_id.astype(str)
#    
#
##    for i in range(len(y)):
##        x.origin_taz.loc[x.trip_origin_id==y.node_id[i]]=y.taz[i]
##        x.dest_taz.loc[x.trip_dest_id==y.node_id[i]]=y.taz[i]    
#    
#    x[['hh_s','mm_s','ss_s']] = x.arrival_time.str.split(":",expand=True,) ## Splitting the start_time into h, m and s
##    x[['hh_e','mm_e','ss_e']] = x.end_time.str.split(".",expand=True,) ## Splitting the end_time into h, m and s
#    
##    tt['d']=tt.index
##    tt.d=tt.d.astype(str)
##    tt.iloc[(1,161), 'd']
#    
#    ## Converting the h, m and s into integers
#    x.hh_s=x.hh_s.astype(int)
#    x.mm_s=x.mm_s.astype(int)
#    x.ss_s=x.ss_s.astype(int)
##    x.hh_e=x.hh_e.astype(int)
##    x.mm_e=x.mm_e.astype(int)
##    x.ss_e=x.ss_e.astype(int)
##    
#
#    x['arrival_time_s']=(x.hh_s*60+x.mm_s)*60+x.ss_s ## Adding a new column to store the start_time in seconds
##    x['end_time_s']=(x.hh_e*60+x.mm_e)*60+x.ss_e ## Adding a new column to store the end_time in seconds
##    x=x.drop(['hh_s','mm_s','ss_s','hh_e','mm_e','ss_e'], axis=1)
#    x=x.drop(['hh_s','mm_s','ss_s'], axis=1)
#    
#    
#    x=x.sort_values(['arrival_time_s'])## Removing the h, m and s columns
#    x=x.reset_index(drop=True)
##    y=y.set_index([('origin_taz','destination_taz')])
##    start=time.time() 
#    for interval in index_column(5).columns:
#        c=pd.DataFrame(index=taz_tt.index)
#        c[interval]=0
#        
#        d=x[x.arrival_time_s>=interval[0]]
#        d=d[d.arrival_time_s<= interval[1]]
#        
#       
#        if len(d)!=0:
#            
#            d=d.set_index(['from_zone','to_zone'])
#            
#            for index in d.index:
#                 c.loc[index,:]=round(d.travel_time[index].mean(),0) 
#                 
##            else: 
##              continue               
##                 taz_tt.loc[(index[0],index[1]),(interval[0],interval[1])]
##                 taz_tt.loc[:,(0,299)]
#        taz_tt[interval]=c[interval]
#
#
#    for index in taz_tt.index:
#         taz_tt.loc[index,:]=taz_tt.loc[index,:].where(taz_tt.loc[index,:]!=0,np.sum(np.array(taz_tt.loc[index,:]))/np.count_nonzero(np.array(taz_tt.loc[index,:])))
#    taz_tt=taz_tt.round(0)
##    taz_tt=taz_tt.T.to_dict()
#
#    return(taz_tt)   
#         
#def gen_shar_ehail_wt_dict(): ##a:tt_dual
#    
#    ## importing the taz 
#    taz=pd.read_csv('taz_2012.csv', delimiter=',',index_col=False)
#    
#    ##creates a df with the same columns as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
#    taz_wt=pd.DataFrame(columns=index_column(5).columns)##creates a df with the same columns as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
#    taz_wt['zone_id']=taz.zone_id ##adding a new column with the zone id
#    taz_wt.zone_id= taz_wt.zone_id.astype(str) ## converting the zone id to str
#    taz_wt=taz_wt.set_index('zone_id') ## sets the zone id as the index of taz_wt
#    
##    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
#    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
#    trips.columns = ['person_id','trip_origin_node','trip_dest_node','from_zone', 'to_zone','subtrip_origin_type','subtrip_dest_type','travel_mode','arrival_time','travel_time','pt_line']
#    
#    y=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)
##    y.node_id=y.node_id.astype(str)
##    y.taz=y.taz.astype(str)
#    
#    
#    x=trips.loc[(trips.travel_mode=='WAIT_SMS_Pool')|(trips.travel_mode=='WAIT_RAIL_SMS_Pool')]
#    x=x.reset_index(drop=True)
#    x.from_zone=x.from_zone.astype(int)
#    x=x.drop(['to_zone'], axis=1)
#   
#    
#    
#    x.from_zone=x.from_zone.replace(list(y.node_id),list(y.taz))
#    x.from_zone=x.from_zone.astype(str)  
#    x=x.rename(columns={'from_zone':'zone', 'travel_time':'waiting_time'})
#    
#
#
##    x['from_zone']=0
##    x['to_zone']=0
##    x.trip_origin_id=x.trip_origin_id.astype(str)
##    x.trip_dest_id=x.trip_dest_id.astype(str)
#    
#
##    for i in range(len(y)):
##        x.origin_taz.loc[x.trip_origin_id==y.node_id[i]]=y.taz[i]
##        x.dest_taz.loc[x.trip_dest_id==y.node_id[i]]=y.taz[i]    
#    
#    x[['hh_s','mm_s','ss_s']] = x.arrival_time.str.split(":",expand=True,) ## Splitting the start_time into h, m and s
##    x[['hh_e','mm_e','ss_e']] = x.end_time.str.split(".",expand=True,) ## Splitting the end_time into h, m and s
#    
##    tt['d']=tt.index
##    tt.d=tt.d.astype(str)
##    tt.iloc[(1,161), 'd']
#    
#    ## Converting the h, m and s into integers
#    x.hh_s=x.hh_s.astype(int)
#    x.mm_s=x.mm_s.astype(int)
#    x.ss_s=x.ss_s.astype(int)
##    x.hh_e=x.hh_e.astype(int)
##    x.mm_e=x.mm_e.astype(int)
##    x.ss_e=x.ss_e.astype(int)
##    
#
#    x['arrival_time_s']=(x.hh_s*60+x.mm_s)*60+x.ss_s ## Adding a new column to store the start_time in seconds
##    x['end_time_s']=(x.hh_e*60+x.mm_e)*60+x.ss_e ## Adding a new column to store the end_time in seconds
##    x=x.drop(['hh_s','mm_s','ss_s','hh_e','mm_e','ss_e'], axis=1)
#    x=x.drop(['hh_s','mm_s','ss_s'], axis=1)
#    
#    
#    x=x.sort_values(['arrival_time_s'])## Removing the h, m and s columns
#    x=x.reset_index(drop=True) 
#    
#    for interval in index_column(5).columns:
#        c=pd.DataFrame(index=taz_wt.index)
#        c[interval]=0
#        
#        d=x[x.arrival_time_s>=interval[0]]
#        d=d[d.arrival_time_s<= interval[1]]
#        
#       
#        if len(d)!=0:
#            
#            d=d.set_index(['zone'])
#            
#            for index in d.index:
#                 c.loc[index,:]=round(d.waiting_time[index].mean(),0) 
#                 
##            else: 
##              continue               
##                 taz_tt.loc[(index[0],index[1]),(interval[0],interval[1])]
##                 taz_tt.loc[:,(0,299)]
#        taz_wt[interval]=c[interval]
#
#
#    for index in taz_wt.index:
#         taz_wt.loc[index,:]=taz_wt.loc[index,:].where(taz_wt.loc[index,:]!=0,np.sum(np.array(taz_wt.loc[index,:]))/np.count_nonzero(np.array(taz_wt.loc[index,:])))
#    taz_wt=taz_wt.round(0)
##    taz_wt=taz_wt.T.to_dict()
# 
##    for column in taz_wt.columns:
##        if column[0]>=27000 and column[1]<=34200:## peak hours 7:30-09:30 am (between 4-8 min)
##            mu, sigma = 360, 60 # mean and standard deviation 
##            taz_wt[column] = np.round(np.random.normal(mu, sigma, len(taz_wt)),0)
##        elif column[0]>= 61200  and column[1]<=72000: ##05:00-08:00 pm (between 3-7 min)
##            mu, sigma = 300, 60 # mean and standard deviation 
##            taz_wt[column] = np.round(np.random.normal(mu, sigma, len(taz_wt)),0)
##        else: ## off peak hours: the rest of intervals
##            mu, sigma = 240, 60 ## between 1-5 min
##            taz_wt[column] = np.round(np.random.normal(mu, sigma, len(taz_wt)),0)
#            
##        
##    for zone in taz_wt.index:
##        b=gen_rand_wt() ## generates a df with with random waiting times in s for the 288 5 min intervals
##        b.columns=index_column(5).columns ## sets the columns names as as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
##        b['zone_id']=zone ## adds a new column with the zone id
##        b=b.set_index('zone_id') # sets the zone id as the index of b
##        taz_wt.loc[zone,:]=b.loc[zone,:] ## assigns the randon waiting times to the taz_wt
##     
##    y=np.arange(1,289)    
##    plt.scatter(gen_rand_wt(), y, s=np.pi*3, c=(0,0,0), alpha=0.5)
#
#    return(taz_wt)
#    