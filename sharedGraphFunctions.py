# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 09:26:47 2019

@author: Francisco
"""

import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools
import math
import networkx as nx
#import geopandas as gpd

# specification of the time discrtization step (time interval)
dt = 30

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

def dicts_tt(tt):

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
    tt_dict=pd.DataFrame(index=tt_dual.index, columns=index_column(5).columns)
#
#    for column in index_column(5).columns: ## assigns the 288 5 intervals as columns od the df usinf index_column()
#        tt_dict[column]=0

    tt_dict=tt_dict.to_dict()
    tt_dict=pd.DataFrame(tt_dict)
    tt_dict=tt_dict.sort_index()

#    for i in tt_dict.index:
#        for j in tt_dual.index:
#            if i==j:
#                tt_dict.loc[i,:]=tt_dual.travel_time[j]


    for col in tt_dict.columns:

        c=pd.DataFrame(index=tt_dual.index)
        c[col]=0

        b=pd.DataFrame(index=tt_dict.index)
        b[col]=tt[(tt.start_time_s==col[0])&(tt.end_time_s==col[1])].travel_time
        b=b.dropna(axis=0)

        c[col]=b[col]
        for index in c[pd.isnull(c[col])].index:
            if index in tt_dual.index:
                c.loc[index]=tt_dual.travel_time[index]

        tt_dict[col]=c[col]



    ##dummy dict

    tt_dum_dict=pd.DataFrame(index=index_dum().index, columns=index_column(5).columns)
#    tt_dum_dict.id=tt_dum_dict.id.astype(str)
#    tt_dum_dict.to_node=tt_dum_dict.to_node.astype(str)
#    tt_dum_dict=tt_dum_dict.set_index(['id','to_node'])
#    tt_dum_dict=tt_dum_dict.drop(['from_node','weight','length'], axis=1)


#    for column in index_column(5).columns: ## assigns the 288 5 intervals as columns od the df usinf index_column()
#        tt_dum_dict[column]=0

#    for i in range(len(a)):
#        tt_dum_dict[(a.start_time_s[i],a.end_time_s[i])]=0

    tt_dum_dict=tt_dum_dict.to_dict()
    tt_dum_dict=pd.DataFrame(tt_dum_dict)

    for i in tt_dum_dict.index:
        for j in tt_dual.index:
            if i[0]==j[0]:
                tt_dum_dict.loc[i,:]=tt_dual.travel_time[j]

#    a=pd.DataFrame(index=tt_dum_dict.index)
#    a=a.reset_index()
#    a=a['level_0'].unique().tolist()
#
    b=tt_dict
    b=b.reset_index()
    b=b.set_index(b.level_0)
    uniques=b.level_0.to_list()


    for index in tt_dum_dict.index:
        if uniques.count(index[0])==1:
            s=pd.DataFrame(b.loc[index[0]])
            s=s.T
            s.level_0=s.level_0.astype(int)
            s.level_0=s.level_0.astype(str)
            s=s.set_index(('level_0',''))
            s=s.drop([('level_1','')], axis=1)
            tt_dum_dict.loc[index]=s.loc[index[0]]
        else:
            s=pd.DataFrame(b.loc[index[0]])
            r=pd.DataFrame(s.min())
            r=r.T
            r.level_0=r.level_0.astype(int)
            r.level_0=r.level_0.astype(str)
            r=r.set_index(('level_0',''))
            r=r.drop([('level_1','')], axis=1)
            tt_dum_dict.loc[index]=r.loc[index[0]]




    tt_dict=tt_dict.T.to_dict()
    tt_dum_dict=tt_dum_dict.T.to_dict()

    return(tt_dict,tt_dum_dict)


def gen_cs_cost_dicts(dict_tt,dum_dict_tt): ## mode: taxi, service: normal/minivan
    ## tt_u: dist_dual

    a=pd.DataFrame.from_dict(dict_tt, orient='index')
    b=pd.DataFrame.from_dict(dum_dict_tt, orient='index')


    cost_dual=pd.DataFrame(4*a.to_numpy()/60, columns=a.columns)
    cost_dual=cost_dual.set_index(a.index)

        ## dum cost

    cost_dum=pd.DataFrame(4*b.to_numpy()/60, columns=b.columns)
    cost_dum=cost_dum.set_index(b.index)


    cost_dual=cost_dual.round(2)
    cost_dum=cost_dum.round(2)
    cost_dual=cost_dual.T.to_dict()
    cost_dum=cost_dum.T.to_dict()

    return(cost_dual,cost_dum)


def gen_station_stock():
    stations=pd.read_csv('parking_mrtonly.csv', delimiter=',',index_col=False)

    ##creates a df with the same columns as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
    st_sl=pd.DataFrame(columns=index_column(5).columns)##creates a df with the same columns as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
    st_sl['station']=stations.id ##adding a new column with the zone id
    st_sl.station= st_sl.station.astype(str) ## converting the zone id to str
    st_sl=st_sl.set_index('station') ## sets the zone id as the index of taz_wt


    for column in  st_sl.columns:
        if column[0]>=27000 and column[1]<=34200:## AM peak hours 7:30-09:30 am (between 4-8 min)
            mu, sigma = 20, 5 # mean and standard deviation
            st_sl[column] = np.round(np.random.normal(mu, sigma, len( st_sl)),0)
        elif column[0]>= 61200  and column[1]<=72000: ## PM peak hour 05:00-08:00 pm (between 3-7 min)
            mu, sigma = 20, 5 # mean and standard deviation
            st_sl[column] = np.round(np.random.normal(mu, sigma, len( st_sl)),0)
        else: ## off peak hours: the rest of intervals
            mu, sigma = 35, 4 ## between 1-5 min
            st_sl[column] = np.round(np.random.normal(mu, sigma, len( st_sl)),0)

    st_sl= st_sl.T.to_dict()

    return(st_sl)



#def gen_sta_csv():
#    parking=gpd.read_file(r'C:\Users\cheko\Desktop\05_Virtual_city-20190715T161511Z-001\05_Virtual_city\others\parking\parking_mrtaccess.shp')
#    parking.to_csv('cs_stations.csv')
#    stations=pd.read_csv('cs_stations.csv', delimiter=',',index_col=False)
#
#    stations.geometry=stations.geometry.str.replace('(','')
#    stations.geometry=stations.geometry.str.replace(')','')
#    stations.geometry=stations.geometry.str.replace('POINT','')
#
#    stations[['wrong','x','y']] = stations.geometry.str.split(" ",expand=True,)
#
#    stations=stations.drop(['wrong', 'geometry'],axis=1)
#
#    stations.x=stations.x.astype(float)
#    stations.y=stations.y.astype(float)
#    stations.id= stations.id.astype(str) ## converting the zone id to str
#    stations=stations.set_index('id')
#    ## Changing the stations 2 and 6
#
#    stations.loc['2','x']=373736
#    stations.loc['2','y']=139913
#    stations.loc['2','node']=91
#
#    stations.loc['6','x']=367181
#    stations.loc['6','y']=147436
#    stations.loc['6','node']=74
#
#    stations=stations.drop(['Unnamed: 0'], axis=1)
#    stations.to_csv('cs_stations.csv')

def gen_sta_dict():

    stations=pd.read_csv('cs_stations.csv', delimiter=',',index_col=False)
    stations.x=stations.x.astype(float)
    stations.y=stations.y.astype(float)
    stations.node=stations.node.astype(str)
    stations.id= stations.id.astype(str) ## converting the zone id to str
    stations=stations.set_index('id')
    stations= stations.T.to_dict()

    return(stations)



def add_cs_dummy_nodes(G,a,b): ## a: dict of nodes b:station dict


## Adding the from_node and to_nodes as H nodes
    for i in range(len(a['id'])):
        for key in b.keys():
            if a['id'][i]==b[key]['node']:
                G.add_node('cs'+str(a['id'][i])+'o',id =a['id'][i], pos=(a['x'][i],a['y'][i]), node_type='car_sharing_dummy_node', node_graph_type='car_sharing_graph')
                G.add_node('cs'+str(a['id'][i])+'d', id =a['id'][i], pos=(a['x'][i],a['y'][i]), node_type='car_sharing_dummy_node', node_graph_type='car_sharing_graph')

    # return(G)


def add_cs_dual_nodes(G,a): ## a: dict of links data l_dum
    for i in range(len(a['id'])):
        G.add_node('cs'+str(a['id'][i]),  node_type='car_sharing_dual_node', node_graph_type='car_sharing_graph')
    # return(G)


def add_cs_station_nodes(G,a,b): ## a: dict of stations, b_: dict of station stock level
    for i in b:
        time_inteval_list = list(b[i].keys())
        break
    
    new_b = dict()
    for i in b:
        new_b.update({i: dict()})
        for t in range(0, 86400, dt):
            stock_level = b[i][time_inteval_list[int(t/300)]]
            new_b[i].update({t: stock_level})

    for key in a.keys():
        G.add_node('s'+key, id=key, pos=(a[key]['x'],a[key]['y']), capacity=50, stock_level=new_b[key], access_node=str(a[key]['node']), node_type='car_sharing_station_node', node_graph_type='car_sharing_graph')

    # return(G)


def add_cs_dummy_edges(G,a,b,c,d,e): ## a: dict of links data, b: dict of tt, c: dict of dist, d: dist of cost

    for i in range(len(a['from_node'])):
        for key in e.keys():
            if a['from_node'][i][0:len(a['from_node'][i])-1]==e[key]['node']:    ## Adding the edges that links the dummy origins with the H  nodes (G edges)
                 G.add_edge('cs'+str(a['from_node'][i]), 'cs'+str(a['id'][i]), travel_time=0, distance=0, car_sharing_fares=0, edge_type='car_sharing_orig_dummy_edge')
 ## Adding the edges that links the the H  nodes (G edges) with the dummy destinations with the minimum travel time of the preceding G link (node in our case)
    # b_copy = dict()
    # b_copy.update(b)
    # d_copy=dict()
    # d_copy.update(d)
    for i in b:
        time_inteval_list = list(b[i].keys())
        break
    
    new_b = dict()
    for i in b:
        new_b.update({i: dict()})
        for t in range(0, 86400, dt):
            in_vehicle_travel_time = b[i][time_inteval_list[int(t/300)]]
            discr_in_vehicle_travel_time = in_vehicle_travel_time - (in_vehicle_travel_time%dt)
            new_b[i].update({t: discr_in_vehicle_travel_time})
    
    new_d = dict()
    for i in d:
        new_d.update({i: dict()})
        for t in range(0, 86400, dt):
            mon_cost = math.ceil(d[i][time_inteval_list[int(t/300)]])
            new_d[i].update({t: mon_cost})
                 
    
    # for i, j in b_copy.items():########
    #     b_copy[i] = list(j.values()) ############
    # for i, j in d_copy.items():#########
    #     d_copy[i] = list(j.values())############
        
 
    for edge in index_dum().index:
        for key in e.keys():
            if edge[1][0:len(edge[1])-1]==e[key]['node']:
                G.add_edge('cs'+edge[0],'cs'+edge[1],travel_time=new_b[edge], distance=c[edge]['distance'], car_sharing_fares=new_d[edge], edge_type='car_sharing_dest_dummy_edge')
# #        G.add_edge(ind, weight=dum_dict_tt[edge], dist=round(tt_u['distance'][i],3), cost=round(tt_u['distance'][i]*5,3), departure_time=None, edge_type='dest_dummy_edge')

    # return(G)




 ## Adding the edges that link the nodes (G links) with the weight of the preceding G link (node in our case)
def add_cs_dual_edges(G,a,b,c): ##a: dict of tt, b_ dict of dist, c: dist of cost
    
    for i in a:
        time_inteval_list = list(a[i].keys())
        break
    
    new_a = dict()
    for i in a:
        new_a.update({i: dict()})
        for t in range(0, 86400, dt):
            in_vehicle_travel_time = a[i][time_inteval_list[int(t/300)]]
            discr_in_vehicle_travel_time = in_vehicle_travel_time - (in_vehicle_travel_time%dt)
            new_a[i].update({t: discr_in_vehicle_travel_time})
    
    new_c = dict()
    for i in c:
        new_c.update({i: dict()})
        for t in range(0, 86400, dt):
            mon_cost = math.ceil(c[i][time_inteval_list[int(t/300)]])
            new_c[i].update({t: mon_cost})
    
    # for i, j in a_copy.items():########
    #     a_copy[i] = list(j.values()) ############
    # for i, j in c_copy.items():#########
    #     c_copy[i] = list(j.values())############
    
        
    for edge in index_dual().index:
        G.add_edge('cs'+edge[0],'cs'+edge[1], travel_time=new_a[edge], distance=b[edge]['distance'], car_sharing_fares=new_c[edge], edge_type='car_sharing_dual_edge')

    # return(G)

def add_cs_station_access_edges(G,a,n,p,q): ##a: dict of stations, n: nodes, p: dum tt q:links

    segment=pd.read_csv('road_segments.csv',delimiter=',',index_col=False)


    for station in a.keys():
        b=pd.DataFrame.from_dict(n)
        d=pd.DataFrame.from_dict(p, orient='index')
        e=pd.DataFrame.from_dict(q)
        dist_st_to_node=math.sqrt(((float(b[b.id==a[station]['node']].x)-a[station]['x'])**2)+((float(b[b.id==a[station]['node']].y)-a[station]['y'])**2))
        dist_link=float(e[e.id==int(segment[segment.id==(a[station]['segment_id'])].link_id)].length)
        d=(dist_st_to_node/dist_link)*d
        d=round(d)
        d=d.reset_index()
        d=d.drop(columns=['level_1'])
        d['level_0']=d['level_0'].astype(str)
        d=d.set_index('level_0')
        cost=4/60*d
        cost=round(cost,2)
        cost=cost.T.to_dict()
        d=d.T.to_dict()
        
        for i in d:
            time_inteval_list = list(d[i].keys())
            break
    
        new_d = dict()
        for i in d:
            new_d.update({i: dict()})
            for t in range(0, 86400, dt):
                in_vehicle_travel_time = d[i][time_inteval_list[int(t/300)]]
                discr_in_vehicle_travel_time = in_vehicle_travel_time - (in_vehicle_travel_time%dt)
                new_d[i].update({t: discr_in_vehicle_travel_time})
        
        new_cost = dict()
        for i in cost:
            new_cost.update({i: dict()})
            for t in range(0, 86400, dt):
                mon_cost = math.ceil(cost[i][time_inteval_list[int(t/300)]])
                new_cost[i].update({t: mon_cost})
        # cost_copy = dict()
        # cost_copy.update(cost)
        # d_copy = dict()
        # d_copy.update(d)
        # for i, j in cost_copy.items():########
        #     cost_copy[i] = list(j.values()) ############
        # for i, j in d_copy.items():#########
        #     d_copy[i] = list(j.values())############
        
        G.add_edge('s'+station,'cs'+str(int(a[station]['node']))+'o', travel_time=new_d[str(int(segment[segment.id==(a[station]['segment_id'])].link_id))], wait_time=60, distance=dist_st_to_node, car_sharing_fares=new_cost[str(int(segment[segment.id==(a[station]['segment_id'])].link_id))], edge_type='car_sharing_station_egress_edge')

        G.add_edge('cs'+str(int(a[station]['node']))+'d','s'+station,travel_time=new_d[str(int(segment[segment.id==(a[station]['segment_id'])].link_id))], wait_time=60, distance=dist_st_to_node, car_sharing_fares=new_cost[str(int(segment[segment.id==(a[station]['segment_id'])].link_id))], edge_type='car_sharing_station_access_edge')

    # return(G)


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

