# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 09:26:47 2019

@author: Francisco
"""


import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from itertools import islice


def import_data():

    a = dict(pd.read_csv('Road_nodes_coord.csv', delimiter=',', index_col=False))## Importing nodes data
    l = pd.read_csv('Road_links.csv', delimiter=',', usecols=[0,3,4], index_col=False) ## Importing links data
    l_tt = pd.read_csv('Road_links_default_travel_times.csv', delimiter=',', usecols=[4,4], index_col=False) ## Importing default travel times per link
    l=l.assign(weight=l_tt) ## Adding the travel times to the links data
    l_length= pd.read_csv('links_length.csv', usecols=[2,2], delimiter=',', index_col=False)## Importing distances (length) per link
    l=l.assign(length=l_length) ## Adding the distances to the links data
    l=l.round({'weight':3, 'length':3}) ## Round to 3 decimals
    l=l.to_dict()# Converting into dict



    ## Getting the unique values of origin nodes
    unique_o=np.unique(list(dict.values(l['from_node'])))
    unique_d=np.unique(list(dict.values(l['to_node'])))
# Adding the label 'o' to the from_nodes
    for i in range (len(l['from_node'])):
        for j in range (len(unique_o)):
            if unique_o[j]==l['from_node'][i]:
                l['from_node'][i]=str(l['from_node'][i])+'o'

    ## Adding the label 'd' to the to_nodes
    for i in range (len(l['to_node'])):
        for j in range (len(unique_d)):
            if unique_d[j]==l['to_node'][i]:
                l['to_node'][i]=str(l['to_node'][i])+'d'



    return(a,l) ## a: dict of nodes data, l: dicts of links data


def import_tt_turnings():

    ##Importing the default travel times per link
    tt_d = pd.read_csv('Road_links_default_travel_times.csv', delimiter=',', usecols=[0,4], index_col=False) ## Importing default travel times per link

    ## Importing the travel times per 5 min per link and per turning
    tt= pd.read_csv('link_travel_time_per_5_min.csv', delimiter=';', index_col=False, header=None )
    tt.columns = ['from_link', 'to_link','start_time','end_time', 'travel_time']

    ## Creates two columns for the start and end time in seconds.
    tt['start_time_s']=0
    tt['end_time_s']=0

    ##Storing the unique time interval


#    a=pd.DataFrame(tt.start_time.drop_duplicates(keep='first'))
#    b=pd.DataFrame(tt.end_time.drop_duplicates(keep='first'))
#    a['start_time_s']=np.nan
#    b['end_time_s']=np.nan

   # Converting the start and end times to seconds


    a=pd.DataFrame(tt.start_time.drop_duplicates(keep='first'))
    a['end_time']=pd.DataFrame(tt.end_time.drop_duplicates(keep='first'))
    a['start_time_s']=np.nan
    a['end_time_s']=np.nan

#    a=pd.DataFrame(tt.start_time.drop_duplicates(keep='first'))
#    a['end_time']=pd.DataFrame(tt.end_time.drop_duplicates(keep='first'))
#    a=a.assign(start_time_s= lambda x: (a.start_time[0:2]*60*a.start_time[3:5])+60*a.start_time[6:8])
#    a['end_time_s']=np.nan


    for j in range(len(a)):
        h=float(a.start_time[j][0:2])
        m=float(a.start_time[j][3:5])
        s=float(a.start_time[j][6:8])
        ts=(h*60+m)*60+s

        hb=float(a.end_time[j][0:2])
        mb=float(a.end_time[j][3:5])
        sb=float(a.end_time[j][6:8])
        tsb=(hb*60+mb)*60+sb

        a.iloc[j,2]=ts
        a.iloc[j,3]=tsb


    ## tt:  Converting the start and end times to seconds
    for i in range(len(a)):
        tt.start_time_s[tt.start_time==a.iloc[i,0]]=a.iloc[i,2] ##start time
        tt.end_time_s[tt.end_time==a.iloc[i,1]]=a.iloc[i,3] ## end time



    ## Importing the turnings groups
    tt_u=pd.read_csv('Road_turning_groups.csv', delimiter=',', usecols=[2,3], index_col=False)  ## Importing turning groups data (from link to link)
    tt_u['start_time']=np.nan
    tt_u['end_time']=np.nan
    tt_u['travel_time']=np.nan
    tt_u= tt_u.sort_values(['from_link','to_link','start_time','end_time'])
    tt_u=tt_u.reset_index(drop=True)

    ## Assigning the default travel time to the different turnings

    for i in range(len(tt_d)):
        for j in range(len(tt_u)):
            if tt_u.loc[j,'from_link']==tt_d.loc[i,'link_id']:
                tt_u.loc[j,'travel_time']=tt_d.loc[i,'travel_time']



    return(tt,tt_u) ## tt: df with all the link travel times per 5 min for 24 h
                    ## tt_u: df with the default link travel times


def dict_tt(tt,tt_u):

    ##Storing the unique time intervals
    a=tt.start_time.drop_duplicates(keep='first')
    b=tt.end_time.drop_duplicates(keep='first')

    ## Creating a dictionary of travel time per link and per 5 min interval in seconds. tt=default travel time
    tt_dict={}
    for i in range(len(tt_u)):

        intervals={'weight':{}}
        for j in range(len(a)):
            h=float(a[j][0:2])
            m=float(a[j][3:5])
            s=float(a[j][6:8])
            ts=(h*60+m)*60+s

            hb=float(b[j][0:2])
            mb=float(b[j][3:5])
            sb=float(b[j][6:8])
            tsb=(hb*60+mb)*60+sb

            intervals['weight'][(ts,tsb)]=tt_u.travel_time[i]

            tt_dict[(tt_u.from_link[i],tt_u.to_link[i])]=intervals


    return(tt_dict)


def dummy_dict(tt,l):

     ##Storing the unique time intervals
    a=tt.start_time.drop_duplicates(keep='first')
    b=tt.end_time.drop_duplicates(keep='first')


    ## Creating a dictionary of travel time per link and per 5 min interval in seconds. tt=default travel time
    tt_dict={}
    for i in range(len(l['id'])):

        intervals={'weight':{}}
        for j in range(len(a)):
            h=float(a[j][0:2])
            m=float(a[j][3:5])
            s=float(a[j][6:8])
            ts=(h*60+m)*60+s

            hb=float(b[j][0:2])
            mb=float(b[j][3:5])
            sb=float(b[j][6:8])
            tsb=(hb*60+mb)*60+sb

            intervals['weight'][(ts,tsb)]=l['weight'][i]

            tt_dict[(l['id'][i],l['to_node'][i])]=intervals


    return(tt_dict)




def update_dicts_tt(dict_tt, dum_dict_tt,tt,t,H,y): #INPUT: dict_tt, dum_dict_tt=dict of dummy destinationes edges tt, tt:df with all the i min interval per link,
                                 # t: time at the update is done, H: time horizon to update in min


#    t='08:02:00'                # i: interval of the travel time per links in minutes
#    H=15
#    y=5
    H=H*60
    h=float(t[0:2])
    m=float(t[3:5])
    s=float(t[6:8])
    ts=(h*60+m)*60+s




    ##Storing the pairs of links (521 turnings)
    links=list(dict_tt.keys())
    dummy_links=list(dum_dict_tt.keys())
    dl=pd.DataFrame(dummy_links,columns=['from_link','to_link'] )
    dl['travel_time']=np.nan
    ##Extracting the travel times of the intervals of interest
    #p: time interval used to predict (to replicate)
    #x: time intervals whitin the time horizon
    # tt of p time interval is copied in the x times intervals

    if ts<y*60:   #Taking the (23:55,23:59:59) interval
        p=tt[(tt.end_time_s>=86400-ts)]
        p=p.reset_index(drop=True)
        x=tt[(tt.start_time_s>=ts-y*60)]
        x=x[(tt.start_time_s<ts+H)]
        x=x.reset_index(drop=True)

    else:
        p=tt[(tt.end_time_s>=ts-y*60)]
        p=p[(tt.start_time_s<=ts-y*60)]
        x=tt[(tt.end_time_s>=ts)]
        x=x[(tt.start_time_s<ts+H)]
        x=x.reset_index(drop=True)

    p=p.reset_index(drop=True)
    links_p=list(zip(list(p.from_link),list(p.to_link)))
    ## list with the links contained in p

#    # Removing the p links that are different from the 521 turning groups
    for tup in links_p:
        if tup  not in links:
            print(tup)
            links_p.remove(tup)


    # Checking if the 521 turning groups are in the p interval
    for tup in links:
        if tup  not in links_p:
            print(tup)

    # Removing the p links that are different from the 521 turning groups
    for i in range(len(p)):
        if (p.from_link[i],p.to_link[i]) not in links:
            p=p.drop(i,axis=0)
    p=p.reset_index(drop=True)


    # Removing the x links that are different from the p links
    for i in range(len(x)):
        if (x.from_link[i],x.to_link[i]) not in links_p:
            x=x.drop(i,axis=0)
    x=x.reset_index(drop=True)


    for j in range(len(p)):
        r=x[x.from_link==p.from_link[j]]
        r=r[x.to_link==p.to_link[j]]
        r=r.reset_index(drop=True)
        for i in  range(len(r)):
            dict_tt[(r.from_link[i],r.to_link[i])]['weight'][(r.start_time_s[i],r.end_time_s[i])]=p.travel_time[j]



    unique_d=np.unique(list(p['from_link']))
    for unique in unique_d:
            w=p[p.from_link==unique]
            for i in range(len(dl)):
                if unique==dl.from_link[i]:
                    dl.travel_time[i]=float(w['travel_time'].min())


    for j in range(len(dl)):
        r=x[x.from_link==dl.from_link[j]]
        r.loc[:,'from_link']=dl.from_link[j]
        r.loc[:,'to_link']=dl.to_link[j]
        r=r.reset_index(drop=True)
        for i in  range(len(r)):
           dum_dict_tt[(r.from_link[i],r.to_link[i])]['weight'][(r.start_time_s[i],r.end_time_s[i])]=dl.travel_time[j]

    return(dict_tt,dum_dict_tt)
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


def add_nodes(G,a): ## a: dict of nodes data
    for i in range(len(a['id'])):
        G.add_node(a['id'][i], pos=(a['x'][i],a['y'][i]))
    return(G)

def add_edges(G,a): ## a: dict of links data
    for i in range(len(a['id'])):
        G.add_edge(a['from_node'][i],a['to_node'][i], id= a['id'][i],dist=a['length'][i],weight=a['weight'][i])
    return(G)

def graph(G):
    pos=nx.get_node_attributes(G,'pos')  #Storing the nodes location
    nx.draw(G,pos, with_labels=True) # Graph with node attributes
#    nx.draw_networkx_edge_labels(G,pos) ## Graph with edge attributes
    plt.show()

def add_nodes_dual(G,a): ## a: dict of links data
    for i in range(len(a['id'])):
        G.add_node('cs'+str(a['id'][i]), id=str(a['id'][i]), node_type='dual_node', node_graph_type='Carsharing')
    return(G)

def add_dummy_nodes(G,a): ## a: dict of nodes
    ## Getting the unique values of origin node

## Adding the from_node and to_nodes as H nodes
    for i in range(len(a['id'])):
        G.add_node('cs'+str(a['id'][i])+'o',id =a['id'][i], pos=(a['x'][i],a['y'][i]), node_type='orig_dummy_node')
        G.add_node('cs'+str(a['id'][i])+'d', id =a['id'][i], pos=(a['x'][i],a['y'][i]), node_type='dest_dummy_node')

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

def add_dummy_edges(G,a,tt_u): ## a: dict of links data
    ## Adding the edges that links the dummy origins with the H  nodes (G edges)
    for i in range (len(a['from_node'])):
        G.add_edge('cs'+str(a['from_node'][i]), 'cs'+str(a['id'][i]), travel_time=0, wait_time=0, distance=0, edge_type='orig_dummy_edge')
 ## Adding the edges that links the the H  nodes (G edges) with the dummy destinations with the minimum travel time of the preceding G link (node in our case)
    for i in range (len(a['to_node'])):
        G.add_edge('cs'+str(a['id'][i]), 'cs'+str(a['to_node'][i]), travel_time=tt_u[tt_u.from_link==a['id'][i]]['travel_time'].min(), departure_time=None, edge_type='dest_dummy_edge')

    return(G)



 ## Adding the edges that link the nodes (G links) with the weight of the preceding G link (node in our case)
def add_dual_edges(G,tt_u):
    for i in range(len(tt_u)):
        G.add_edge(tt_u.from_link[i],tt_u.to_link[i],weight= tt_u.travel_time[i], departure_time=None, edge_type='dual_edge')
    return(G)

def add_edge_attributes(G,dict_tt,dum_dict_tt):
    for edge in dict_tt:
        G.add_edge(*edge, weight=dict_tt[edge]['weight'])

    for edge in dum_dict_tt:
        G.add_edge(*edge, weight=dum_dict_tt[edge]['weight'])
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








