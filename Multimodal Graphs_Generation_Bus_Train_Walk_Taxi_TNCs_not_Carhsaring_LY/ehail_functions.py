

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import itertools
import math
from functions import index_column


##DICTIONARY OF DISTANCES
def gen_taxi_dist_dict(mode):
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

    dist.distance[(18,18)]=(dist.distance[(18,19)]+dist.distance[(18,16)]+dist.distance[(18,17)]+dist.distance[(19,18)]+dist.distance[(16,18)]+dist.distance[(17,18)])/6
    dist.distance[(11,11)]=(dist.distance[(11,10)]+dist.distance[(11,15)]+dist.distance[(11,12)]+dist.distance[(10,11)]+dist.distance[(15,11)]+dist.distance[(12,11)])/6
    dist.distance[(22,22)]=(dist.distance[(22,21)]+dist.distance[(22,1)]+dist.distance[(22,14)]+dist.distance[(21,22)]+dist.distance[(1,22)]+dist.distance[(14,22)])/6

    if mode=='taxi':

        dist=dist.reset_index()

        dist.origin_zone='t'+dist.origin_zone.astype(str)+'i'
        dist.destination_zone='t'+dist.destination_zone.astype(str)+'o'

        dist=dist.set_index(['origin_zone','destination_zone'])

    elif mode=='single_taxi':

        dist=dist.reset_index()

        dist.origin_zone='sin'+dist.origin_zone.astype(str)+'i'
        dist.destination_zone='sin'+dist.destination_zone.astype(str)+'o'

        dist=dist.set_index(['origin_zone','destination_zone'])

    elif mode=='shared_taxi':
        dist=dist.reset_index()

        dist.origin_zone='shar'+dist.origin_zone.astype(str)+'i'
        dist.destination_zone='shar'+dist.destination_zone.astype(str)+'o'

        dist=dist.set_index(['origin_zone','destination_zone'])

    dist=round(1000*dist,3)    
    dist=dist.T.to_dict()


    return(dist)


##DICTIONARY OF WAITING TIMES

def gen_taxi_wt_dict(): ##a:tt_dual

    ## importing the taz
    taz=pd.read_csv('taz_2012.csv', delimiter=',',index_col=False)

    ##creates a df with the same columns as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
    taz_wt=pd.DataFrame(columns=index_column(5).columns)##creates a df with the same columns as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
    taz_wt['zone']=taz.zone_id ##adding a new column with the zone id
    taz_wt.zone= taz_wt.zone.astype(str) ## converting the zone id to str
    taz_wt=taz_wt.set_index('zone') ## sets the zone id as the index of taz_wt


    for column in taz_wt.columns:
        if column[0]>=27000 and column[1]<=34200:## peak hours 7:30-09:30 am (between 4-8 min)
            mu, sigma = 360, 60 # mean and standard deviation
            taz_wt[column] = np.round(np.random.normal(mu, sigma, len(taz_wt)),0)
        elif column[0]>= 61200  and column[1]<=72000: ##05:00-08:00 pm (between 3-7 min)
            mu, sigma = 300, 60 # mean and standard deviation
            taz_wt[column] = np.round(np.random.normal(mu, sigma, len(taz_wt)),0)
        else: ## off peak hours: the rest of intervals
            mu, sigma = 240, 60 ## between 1-5 min
            taz_wt[column] = np.round(np.random.normal(mu, sigma, len(taz_wt)),0)

    taz_wt=taz_wt.reset_index(level='zone')

    taz_wt.zone='t'+taz_wt.zone.astype(str)

    taz_wt=taz_wt.set_index(['zone'])


    taz_wt=taz_wt.T.to_dict()
    return(taz_wt)
#


def gen_on_demand_taxi_single_wt_dict(): ##a:tt_dual

    ## importing the taz
    taz=pd.read_csv('taz_2012.csv', delimiter=',',index_col=False)

    ##creates a df with the same columns as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
    taz_wt=pd.DataFrame(columns=index_column(5).columns)##creates a df with the same columns as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
    taz_wt['zone']=taz.zone_id ##adding a new column with the zone id
    taz_wt.zone= taz_wt.zone.astype(str) ## converting the zone id to str
    taz_wt=taz_wt.set_index('zone') ## sets the zone id as the index of taz_wt

#    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
    trips.columns = ['person_id','trip_origin_node','trip_dest_node','from_zone', 'to_zone','subtrip_origin_type','subtrip_dest_type','travel_mode','arrival_time','travel_time','pt_line']

    y=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)


    x=trips.loc[(trips.travel_mode=='WAIT_SMS')|(trips.travel_mode=='WAIT_RAIL_SMS')]
    x=x.reset_index(drop=True)
    x.from_zone=x.from_zone.astype(int)
    x=x.drop(['to_zone'], axis=1)



    x.from_zone=x.from_zone.replace(list(y.node_id),list(y.taz))
    x.from_zone=x.from_zone.astype(str)
    x=x.rename(columns={'from_zone':'zone', 'travel_time':'waiting_time'})



    x[['hh_s','mm_s','ss_s']] = x.arrival_time.str.split(":",expand=True,) ## Splitting the start_time into h, m and s


    ## Converting the h, m and s into integers
    x.hh_s=x.hh_s.astype(int)
    x.mm_s=x.mm_s.astype(int)
    x.ss_s=x.ss_s.astype(int)


    x['arrival_time_s']=(x.hh_s*60+x.mm_s)*60+x.ss_s ## Adding a new column to store the start_time in seconds
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

    taz_wt=taz_wt.reset_index(level='zone')

    taz_wt.zone='sin'+taz_wt.zone.astype(str)

    taz_wt=taz_wt.set_index(['zone'])
    taz_wt=taz_wt.T.to_dict()


    return(taz_wt)



def gen_on_demand_taxi_shared_wt_dict(): ##a:tt_dual

    ## importing the taz
    taz=pd.read_csv('taz_2012.csv', delimiter=',',index_col=False)

    ##creates a df with the same columns as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
    taz_wt=pd.DataFrame(columns=index_column(5).columns)##creates a df with the same columns as the tt_dual, that are the 288 5 min interval in seconds eg (0,299),...
    taz_wt['zone']=taz.zone_id ##adding a new column with the zone id
    taz_wt.zone= taz_wt.zone.astype(str) ## converting the zone id to str
    taz_wt=taz_wt.set_index('zone') ## sets the zone id as the index of taz_wt

#    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
    trips.columns = ['person_id','trip_origin_node','trip_dest_node','from_zone', 'to_zone','subtrip_origin_type','subtrip_dest_type','travel_mode','arrival_time','travel_time','pt_line']

    y=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)


    x=trips.loc[(trips.travel_mode=='WAIT_SMS_Pool')|(trips.travel_mode=='WAIT_RAIL_SMS_Pool')]
    x=x.reset_index(drop=True)
    x.from_zone=x.from_zone.astype(int)
    x=x.drop(['to_zone'], axis=1)



    x.from_zone=x.from_zone.replace(list(y.node_id),list(y.taz))
    x.from_zone=x.from_zone.astype(str)
    x=x.rename(columns={'from_zone':'zone', 'travel_time':'waiting_time'})



    x[['hh_s','mm_s','ss_s']] = x.arrival_time.str.split(":",expand=True,) ## Splitting the start_time into h, m and s


    ## Converting the h, m and s into integers
    x.hh_s=x.hh_s.astype(int)
    x.mm_s=x.mm_s.astype(int)
    x.ss_s=x.ss_s.astype(int)


    x['arrival_time_s']=(x.hh_s*60+x.mm_s)*60+x.ss_s ## Adding a new column to store the start_time in seconds
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

    taz_wt=taz_wt.reset_index(level='zone')

    taz_wt.zone='shar'+taz_wt.zone.astype(str)

    taz_wt=taz_wt.set_index(['zone'])
    taz_wt=taz_wt.T.to_dict()


    return(taz_wt)



## DICTIONARY OF TRAVEL TIMES

def gen_taxi_tt_dict():

    a=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
    a['incoming_node']=a.zone_id
    b=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
    b['outgoing_node']=b.zone_id


    taz_pairs=pd.DataFrame(columns=['from_node','to_node','from_zone','to_zone'])


    for i in b.index:
        for j in a.index:
            taz_pairs=taz_pairs.append({'from_node':a.incoming_node[j], 'to_node': b.outgoing_node[i], 'from_zone':a.zone_id[j], 'to_zone':b.zone_id[i]}, ignore_index=True)

    taz_tt=pd.DataFrame(columns=index_column(5).columns)
    taz_tt['from_node']=taz_pairs['from_node']
    taz_tt['to_node']=taz_pairs['to_node']
    taz_tt=taz_tt.set_index(['from_node','to_node'])


    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
    trips.columns = ['person_id','trip_origin_node','trip_dest_node','from_zone', 'to_zone','subtrip_origin_type','subtrip_dest_type','travel_mode','arrival_time','travel_time','pt_line']
    allcartrips=trips.loc[(trips.travel_mode=='ON_TAXI')|(trips.travel_mode=='ON_SMS_Veh')|(trips.travel_mode=='ON_RAIL_SMS_Veh')|(trips.travel_mode=='ON_SMS_Pool_Veh')|(trips.travel_mode=='ON_RAIL_SMS_Pool_Veh')|(trips.travel_mode=='ON_CAR')]
    allcartrips.from_zone = allcartrips.from_zone.astype(int)
    allcartrips.to_zone = allcartrips.to_zone.astype(int)
    allcartrips=allcartrips.reset_index(drop=True)

    y=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)

    allcartrips.from_zone= allcartrips.from_zone.replace(list(y.node_id),list(y.taz))
    allcartrips.to_zone= allcartrips.to_zone.replace(list(y.node_id),list(y.taz))


    allcartrips[['hh_s','mm_s','ss_s']] = allcartrips.arrival_time.str.split(":",expand=True,) ## Splitting the start_time into h, m and s
#
    ## Converting the h, m and s into integers
    allcartrips.hh_s=allcartrips.hh_s.astype(int)
    allcartrips.mm_s=allcartrips.mm_s.astype(int)
    allcartrips.ss_s=allcartrips.ss_s.astype(int)
#

    allcartrips['arrival_time_s']=(allcartrips.hh_s*60+allcartrips.mm_s)*60+allcartrips.ss_s ## Adding a new column to store the start_time in seconds

    allcartrips=allcartrips.drop(['hh_s','mm_s','ss_s'], axis=1)


    allcartrips=allcartrips.sort_values(['arrival_time_s'])## Removing the h, m and s columns
    allcartrips=allcartrips.reset_index(drop=True)


    x=allcartrips.loc[(allcartrips.travel_mode=='ON_TAXI')]
    x=x.reset_index(drop=True)


    for interval in index_column(5).columns:

        c=pd.DataFrame(index=taz_tt.index)
#        taz_tt[interval]=0
        c[interval]=0

        d=x[x.arrival_time_s>=interval[0]]
        d=d[d.arrival_time_s<= interval[1]]


        if len(d)!=0:

            d=d.set_index(['from_zone','to_zone'])

            for index in d.index.unique():
                 c.loc[index]=round(d.travel_time[index].mean(),0)

#            else:
#              continue
#                 taz_tt.loc[(index[0],index[1]),(interval[0],interval[1])]
#                 taz_tt.loc[:,(0,299)]
        taz_tt[interval]=c[interval]


    for index in taz_tt.index:
         taz_tt.loc[index]=taz_tt.loc[index].where(taz_tt.loc[index]!=0,np.sum(np.array(taz_tt.loc[index]))/np.count_nonzero(np.array(taz_tt.loc[index])))

    taz_tt=taz_tt.fillna(0)




    x=allcartrips.loc[(allcartrips.travel_mode=='ON_SMS_Veh')|(allcartrips.travel_mode=='ON_RAIL_SMS_Veh')|(allcartrips.travel_mode=='ON_SMS_Pool_Veh')|(allcartrips.travel_mode=='ON_RAIL_SMS_Pool_Veh')]
    x=x.reset_index(drop=True)


    taz_tt_aux=pd.DataFrame(columns=index_column(5).columns)
    taz_tt_aux['from_node']=taz_pairs['from_node']
    taz_tt_aux['to_node']=taz_pairs['to_node']
    taz_tt_aux=taz_tt_aux.set_index(['from_node','to_node'])

    for index in taz_tt.index:
        if np.count_nonzero(np.array(taz_tt.loc[index]))!=0:
            taz_tt_aux=taz_tt_aux.drop([index])


    r=pd.DataFrame()

    for index in taz_tt_aux.index:
        s=x[(x.from_zone==index[0])&(x.to_zone==index[1])]
        r=r.append(s)

    for interval in index_column(5).columns:
        c=pd.DataFrame(index=taz_tt_aux.index)
#        taz_tt[interval]=0
        c[interval]=0

        d=r[r.arrival_time_s>=interval[0]]
        d=d[d.arrival_time_s<= interval[1]]


        if len(d)!=0:

            d=d.set_index(['from_zone','to_zone'])

            for index in d.index.unique():
                 c.loc[index]=round(d.travel_time[index].mean(),0)

        taz_tt_aux[interval]=c[interval]

    for index in taz_tt_aux.index:
         taz_tt_aux.loc[index]=taz_tt_aux.loc[index].where(taz_tt_aux.loc[index]!=0,np.sum(np.array(taz_tt_aux.loc[index]))/np.count_nonzero(np.array(taz_tt_aux.loc[index])))
    taz_tt_aux=taz_tt_aux.fillna(0)


    for index in taz_tt_aux.index:
        taz_tt.loc[index]=taz_tt_aux.loc[index]




    x=allcartrips.loc[(allcartrips.travel_mode=='ON_CAR')]

    x=x.reset_index(drop=True)



#    x.from_zone=x.from_zone.astype(str)
#    x.to_zone=x.to_zone.astype(str)
#
    taz_tt_aux=pd.DataFrame(pd.DataFrame(columns=index_column(5).columns))
    taz_tt_aux['from_node']=taz_pairs['from_node']
    taz_tt_aux['to_node']=taz_pairs['to_node']
    taz_tt_aux=taz_tt_aux.set_index(['from_node','to_node'])


    for index in taz_tt.index:
        if np.count_nonzero(np.array(taz_tt.loc[index]))!=0:
            taz_tt_aux=taz_tt_aux.drop([index])

    r=pd.DataFrame()

    for index in taz_tt_aux.index:
        s=x[(x.from_zone==index[0])&(x.to_zone==index[1])]
        r=r.append(s)

    for interval in index_column(5).columns:
        c=pd.DataFrame(index=taz_tt_aux.index)
#        taz_tt[interval]=0
        c[interval]=0

        d=r[r.arrival_time_s>=interval[0]]
        d=d[d.arrival_time_s<= interval[1]]


        if len(d)!=0:

            d=d.set_index(['from_zone','to_zone'])

            for index in d.index.unique():
                c.loc[index]=round(d.travel_time[index].mean(),0)

        taz_tt_aux[interval]=c[interval]

    for index in taz_tt_aux.index:
         taz_tt_aux.loc[index]=taz_tt_aux.loc[index].where(taz_tt_aux.loc[index]!=0,np.sum(np.array(taz_tt_aux.loc[index]))/np.count_nonzero(np.array(taz_tt_aux.loc[index])))

    taz_tt_aux=taz_tt_aux.fillna(0)


    for index in taz_tt_aux.index:
        taz_tt.loc[index]=taz_tt_aux.loc[index]




    for index in taz_tt.index:
        if np.count_nonzero(np.array(taz_tt.loc[index]))==0:
            taz_tt.loc[index]=taz_tt.loc[index[1],index[0]]

    ## Travel time for the missing zone to zone
    taz_tt.loc[(2,2)]=(taz_tt.loc[(2,21)]+taz_tt.loc[(21,2)]+taz_tt.loc[(2,6)]+taz_tt.loc[(6,2)]+taz_tt.loc[(2,7)]+taz_tt.loc[(7,2)]+taz_tt.loc[(2,1)]+taz_tt.loc[(1,2)])/8
    taz_tt.loc[(6,6)]=(taz_tt.loc[(6,21)]+taz_tt.loc[(21,6)]+taz_tt.loc[(2,6)]+taz_tt.loc[(6,2)]+taz_tt.loc[(6,7)]+taz_tt.loc[(7,6)]+taz_tt.loc[(6,3)]+taz_tt.loc[(3,6)]+taz_tt.loc[(6,12)]+taz_tt.loc[(12,6)]+taz_tt.loc[(6,13)]+taz_tt.loc[(13,6)])/12
    taz_tt.loc[(8,8)]=(taz_tt.loc[(8,5)]+taz_tt.loc[(5,8)]+taz_tt.loc[(8,3)]+taz_tt.loc[(3,8)]+taz_tt.loc[(8,4)]+taz_tt.loc[(4,8)]+taz_tt.loc[(8,1)]+taz_tt.loc[(1,8)]+taz_tt.loc[(8,14)]+taz_tt.loc[(14,8)])/10
    taz_tt.loc[(9,9)]=(taz_tt.loc[(9,23)]+taz_tt.loc[(23,9)]+taz_tt.loc[(9,10)]+taz_tt.loc[(10,9)]+taz_tt.loc[(9,3)]+taz_tt.loc[(3,9)]+taz_tt.loc[(9,4)]+taz_tt.loc[(4,9)])/8
    taz_tt.loc[(11,11)]=(taz_tt.loc[(11,12)]+taz_tt.loc[(12,11)]+taz_tt.loc[(11,13)]+taz_tt.loc[(13,11)]+taz_tt.loc[(11,15)]+taz_tt.loc[(15,13)])/6
    taz_tt.loc[(18,18)]=(taz_tt.loc[(18,19)]+taz_tt.loc[(19,18)]+taz_tt.loc[(18,16)]+taz_tt.loc[(16,18)]+taz_tt.loc[(18,17)]+taz_tt.loc[(17,18)])/6
    taz_tt.loc[(22,22)]=(taz_tt.loc[(22,21)]+taz_tt.loc[(21,22)]+taz_tt.loc[(22,1)]+taz_tt.loc[(1,22)]+taz_tt.loc[(22,14)]+taz_tt.loc[(14,22)])/6



    taz_tt=taz_tt.reset_index()

    taz_tt.from_node='t'+ taz_tt.from_node.astype(str)+'i'
    taz_tt.to_node='t'+taz_tt.to_node.astype(str)+'o'

    taz_tt=taz_tt.set_index(['from_node','to_node'])
    taz_tt=taz_tt.round(0)
    taz_tt=taz_tt.T.to_dict()



    return(taz_tt)



def gen_on_demand_taxi_single_tt_dict():

    a=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
    a['incoming_node']=a.zone_id
    b=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
    b['outgoing_node']=b.zone_id


    taz_pairs=pd.DataFrame(columns=['from_node','to_node','from_zone','to_zone'])


    for i in b.index:
        for j in a.index:
            taz_pairs=taz_pairs.append({'from_node':a.incoming_node[j], 'to_node': b.outgoing_node[i], 'from_zone':a.zone_id[j], 'to_zone':b.zone_id[i]}, ignore_index=True)

    taz_tt=pd.DataFrame(columns=index_column(5).columns)
    taz_tt['from_node']=taz_pairs['from_node']
    taz_tt['to_node']=taz_pairs['to_node']
    taz_tt=taz_tt.set_index(['from_node','to_node'])


    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
    trips.columns = ['person_id','trip_origin_node','trip_dest_node','from_zone', 'to_zone','subtrip_origin_type','subtrip_dest_type','travel_mode','arrival_time','travel_time','pt_line']
    allcartrips=trips.loc[(trips.travel_mode=='ON_TAXI')|(trips.travel_mode=='ON_SMS_Veh')|(trips.travel_mode=='ON_RAIL_SMS_Veh')|(trips.travel_mode=='ON_SMS_Pool_Veh')|(trips.travel_mode=='ON_RAIL_SMS_Pool_Veh')|(trips.travel_mode=='ON_CAR')]
    allcartrips.from_zone = allcartrips.from_zone.astype(int)
    allcartrips.to_zone = allcartrips.to_zone.astype(int)
    allcartrips=allcartrips.reset_index(drop=True)

    y=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)

    allcartrips.from_zone= allcartrips.from_zone.replace(list(y.node_id),list(y.taz))
    allcartrips.to_zone= allcartrips.to_zone.replace(list(y.node_id),list(y.taz))


    allcartrips[['hh_s','mm_s','ss_s']] = allcartrips.arrival_time.str.split(":",expand=True,) ## Splitting the start_time into h, m and s
#
    ## Converting the h, m and s into integers
    allcartrips.hh_s=allcartrips.hh_s.astype(int)
    allcartrips.mm_s=allcartrips.mm_s.astype(int)
    allcartrips.ss_s=allcartrips.ss_s.astype(int)
#

    allcartrips['arrival_time_s']=(allcartrips.hh_s*60+allcartrips.mm_s)*60+allcartrips.ss_s ## Adding a new column to store the start_time in seconds

    allcartrips=allcartrips.drop(['hh_s','mm_s','ss_s'], axis=1)


    allcartrips=allcartrips.sort_values(['arrival_time_s'])## Removing the h, m and s columns
    allcartrips=allcartrips.reset_index(drop=True)


    x=allcartrips.loc[(allcartrips.travel_mode=='ON_SMS_Veh')|(allcartrips.travel_mode=='ON_RAIL_SMS_Veh')]
    x=x.reset_index(drop=True)


    for interval in index_column(5).columns:

        c=pd.DataFrame(index=taz_tt.index)
#        taz_tt[interval]=0
        c[interval]=0

        d=x[x.arrival_time_s>=interval[0]]
        d=d[d.arrival_time_s<= interval[1]]


        if len(d)!=0:

            d=d.set_index(['from_zone','to_zone'])

            for index in d.index.unique():
                 c.loc[index]=round(d.travel_time[index].mean(),0)

        taz_tt[interval]=c[interval]


    for index in taz_tt.index:
         taz_tt.loc[index]=taz_tt.loc[index].where(taz_tt.loc[index]!=0,np.sum(np.array(taz_tt.loc[index]))/np.count_nonzero(np.array(taz_tt.loc[index])))

    taz_tt=taz_tt.fillna(0)




    x=allcartrips.loc[(allcartrips.travel_mode=='ON_TAXI')|(allcartrips.travel_mode=='ON_SMS_Pool_Veh')|(allcartrips.travel_mode=='ON_RAIL_SMS_Pool_Veh')]
    x=x.reset_index(drop=True)


    taz_tt_aux=pd.DataFrame(columns=index_column(5).columns)
    taz_tt_aux['from_node']=taz_pairs['from_node']
    taz_tt_aux['to_node']=taz_pairs['to_node']
    taz_tt_aux=taz_tt_aux.set_index(['from_node','to_node'])

    for index in taz_tt.index:
        if np.count_nonzero(np.array(taz_tt.loc[index]))!=0:
            taz_tt_aux=taz_tt_aux.drop([index])


    r=pd.DataFrame()

    for index in taz_tt_aux.index:
        s=x[(x.from_zone==index[0])&(x.to_zone==index[1])]
        r=r.append(s)

    for interval in index_column(5).columns:
        c=pd.DataFrame(index=taz_tt_aux.index)
#        taz_tt[interval]=0
        c[interval]=0

        d=r[r.arrival_time_s>=interval[0]]
        d=d[d.arrival_time_s<= interval[1]]


        if len(d)!=0:

            d=d.set_index(['from_zone','to_zone'])

            for index in d.index.unique():
                 c.loc[index]=round(d.travel_time[index].mean(),0)

        taz_tt_aux[interval]=c[interval]

    for index in taz_tt_aux.index:
         taz_tt_aux.loc[index]=taz_tt_aux.loc[index].where(taz_tt_aux.loc[index]!=0,np.sum(np.array(taz_tt_aux.loc[index]))/np.count_nonzero(np.array(taz_tt_aux.loc[index])))
    taz_tt_aux=taz_tt_aux.fillna(0)


    for index in taz_tt_aux.index:
        taz_tt.loc[index]=taz_tt_aux.loc[index]



    x=allcartrips.loc[(allcartrips.travel_mode=='ON_CAR')]

    x=x.reset_index(drop=True)



    taz_tt_aux=pd.DataFrame(pd.DataFrame(columns=index_column(5).columns))
    taz_tt_aux['from_node']=taz_pairs['from_node']
    taz_tt_aux['to_node']=taz_pairs['to_node']
    taz_tt_aux=taz_tt_aux.set_index(['from_node','to_node'])


    for index in taz_tt.index:
        if np.count_nonzero(np.array(taz_tt.loc[index]))!=0:
            taz_tt_aux=taz_tt_aux.drop([index])

    r=pd.DataFrame()

    for index in taz_tt_aux.index:
        s=x[(x.from_zone==index[0])&(x.to_zone==index[1])]
        r=r.append(s)

    for interval in index_column(5).columns:
        c=pd.DataFrame(index=taz_tt_aux.index)
#        taz_tt[interval]=0
        c[interval]=0

        d=r[r.arrival_time_s>=interval[0]]
        d=d[d.arrival_time_s<= interval[1]]


        if len(d)!=0:

            d=d.set_index(['from_zone','to_zone'])

            for index in d.index.unique():
                c.loc[index]=round(d.travel_time[index].mean(),0)

        taz_tt_aux[interval]=c[interval]

    for index in taz_tt_aux.index:
         taz_tt_aux.loc[index]=taz_tt_aux.loc[index].where(taz_tt_aux.loc[index]!=0,np.sum(np.array(taz_tt_aux.loc[index]))/np.count_nonzero(np.array(taz_tt_aux.loc[index])))

    taz_tt_aux=taz_tt_aux.fillna(0)


    for index in taz_tt_aux.index:
        taz_tt.loc[index]=taz_tt_aux.loc[index]




    for index in taz_tt.index:
        if np.count_nonzero(np.array(taz_tt.loc[index]))==0:
            taz_tt.loc[index]=taz_tt.loc[index[1],index[0]]

    ## Travel time for the missing zone to zone
    taz_tt.loc[(2,2)]=(taz_tt.loc[(2,21)]+taz_tt.loc[(21,2)]+taz_tt.loc[(2,6)]+taz_tt.loc[(6,2)]+taz_tt.loc[(2,7)]+taz_tt.loc[(7,2)]+taz_tt.loc[(2,1)]+taz_tt.loc[(1,2)])/8
    taz_tt.loc[(6,6)]=(taz_tt.loc[(6,21)]+taz_tt.loc[(21,6)]+taz_tt.loc[(2,6)]+taz_tt.loc[(6,2)]+taz_tt.loc[(6,7)]+taz_tt.loc[(7,6)]+taz_tt.loc[(6,3)]+taz_tt.loc[(3,6)]+taz_tt.loc[(6,12)]+taz_tt.loc[(12,6)]+taz_tt.loc[(6,13)]+taz_tt.loc[(13,6)])/12
    taz_tt.loc[(8,8)]=(taz_tt.loc[(8,5)]+taz_tt.loc[(5,8)]+taz_tt.loc[(8,3)]+taz_tt.loc[(3,8)]+taz_tt.loc[(8,4)]+taz_tt.loc[(4,8)]+taz_tt.loc[(8,1)]+taz_tt.loc[(1,8)]+taz_tt.loc[(8,14)]+taz_tt.loc[(14,8)])/10
    taz_tt.loc[(9,9)]=(taz_tt.loc[(9,23)]+taz_tt.loc[(23,9)]+taz_tt.loc[(9,10)]+taz_tt.loc[(10,9)]+taz_tt.loc[(9,3)]+taz_tt.loc[(3,9)]+taz_tt.loc[(9,4)]+taz_tt.loc[(4,9)])/8
    taz_tt.loc[(11,11)]=(taz_tt.loc[(11,12)]+taz_tt.loc[(12,11)]+taz_tt.loc[(11,13)]+taz_tt.loc[(13,11)]+taz_tt.loc[(11,15)]+taz_tt.loc[(15,13)])/6
    taz_tt.loc[(18,18)]=(taz_tt.loc[(18,19)]+taz_tt.loc[(19,18)]+taz_tt.loc[(18,16)]+taz_tt.loc[(16,18)]+taz_tt.loc[(18,17)]+taz_tt.loc[(17,18)])/6
    taz_tt.loc[(22,22)]=(taz_tt.loc[(22,21)]+taz_tt.loc[(21,22)]+taz_tt.loc[(22,1)]+taz_tt.loc[(1,22)]+taz_tt.loc[(22,14)]+taz_tt.loc[(14,22)])/6



    taz_tt=taz_tt.reset_index()

    taz_tt.from_node='sin'+ taz_tt.from_node.astype(str)+'i'
    taz_tt.to_node='sin'+taz_tt.to_node.astype(str)+'o'

    taz_tt=taz_tt.set_index(['from_node','to_node'])
    taz_tt=taz_tt.round(0)
    taz_tt=taz_tt.T.to_dict()



    return(taz_tt)


def gen_on_demand_taxi_shared_tt_dict():

    a=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
    a['incoming_node']=a.zone_id
    b=pd.read_csv('taz_2012.csv', delimiter=',', usecols=[0], index_col=False)
    b['outgoing_node']=b.zone_id


    taz_pairs=pd.DataFrame(columns=['from_node','to_node','from_zone','to_zone'])


    for i in b.index:
        for j in a.index:
            taz_pairs=taz_pairs.append({'from_node':a.incoming_node[j], 'to_node': b.outgoing_node[i], 'from_zone':a.zone_id[j], 'to_zone':b.zone_id[i]}, ignore_index=True)

    taz_tt=pd.DataFrame(columns=index_column(5).columns)
    taz_tt['from_node']=taz_pairs['from_node']
    taz_tt['to_node']=taz_pairs['to_node']
    taz_tt=taz_tt.set_index(['from_node','to_node'])


    trips=pd.read_csv('traveltime.csv', delimiter=',',index_col=False)
    trips.columns = ['person_id','trip_origin_node','trip_dest_node','from_zone', 'to_zone','subtrip_origin_type','subtrip_dest_type','travel_mode','arrival_time','travel_time','pt_line']
    allcartrips=trips.loc[(trips.travel_mode=='ON_TAXI')|(trips.travel_mode=='ON_SMS_Veh')|(trips.travel_mode=='ON_RAIL_SMS_Veh')|(trips.travel_mode=='ON_SMS_Pool_Veh')|(trips.travel_mode=='ON_RAIL_SMS_Pool_Veh')|(trips.travel_mode=='ON_CAR')]
    allcartrips.from_zone = allcartrips.from_zone.astype(int)
    allcartrips.to_zone = allcartrips.to_zone.astype(int)
    allcartrips=allcartrips.reset_index(drop=True)

    y=pd.read_csv('node_taz_mapping.csv', delimiter=',', usecols=[0,8], index_col=False)

    allcartrips.from_zone= allcartrips.from_zone.replace(list(y.node_id),list(y.taz))
    allcartrips.to_zone= allcartrips.to_zone.replace(list(y.node_id),list(y.taz))


    allcartrips[['hh_s','mm_s','ss_s']] = allcartrips.arrival_time.str.split(":",expand=True,) ## Splitting the start_time into h, m and s
#
    ## Converting the h, m and s into integers
    allcartrips.hh_s=allcartrips.hh_s.astype(int)
    allcartrips.mm_s=allcartrips.mm_s.astype(int)
    allcartrips.ss_s=allcartrips.ss_s.astype(int)
#

    allcartrips['arrival_time_s']=(allcartrips.hh_s*60+allcartrips.mm_s)*60+allcartrips.ss_s ## Adding a new column to store the start_time in seconds

    allcartrips=allcartrips.drop(['hh_s','mm_s','ss_s'], axis=1)


    allcartrips=allcartrips.sort_values(['arrival_time_s'])## Removing the h, m and s columns
    allcartrips=allcartrips.reset_index(drop=True)


    x=allcartrips.loc[(allcartrips.travel_mode=='ON_SMS_Pool_Veh')|(allcartrips.travel_mode=='ON_RAIL_SMS_Pool_Veh')]
    x=x.reset_index(drop=True)


    for interval in index_column(5).columns:

        c=pd.DataFrame(index=taz_tt.index)
#        taz_tt[interval]=0
        c[interval]=0

        d=x[x.arrival_time_s>=interval[0]]
        d=d[d.arrival_time_s<= interval[1]]


        if len(d)!=0:

            d=d.set_index(['from_zone','to_zone'])

            for index in d.index.unique():
                 c.loc[index]=round(d.travel_time[index].mean(),0)

        taz_tt[interval]=c[interval]


    for index in taz_tt.index:
         taz_tt.loc[index]=taz_tt.loc[index].where(taz_tt.loc[index]!=0,np.sum(np.array(taz_tt.loc[index]))/np.count_nonzero(np.array(taz_tt.loc[index])))

    taz_tt=taz_tt.fillna(0)


    x=allcartrips.loc[(allcartrips.travel_mode=='ON_TAXI')|(allcartrips.travel_mode=='ON_SMS_Veh')|(allcartrips.travel_mode=='ON_RAIL_SMS_Veh')]
    x=x.reset_index(drop=True)


    taz_tt_aux=pd.DataFrame(columns=index_column(5).columns)
    taz_tt_aux['from_node']=taz_pairs['from_node']
    taz_tt_aux['to_node']=taz_pairs['to_node']
    taz_tt_aux=taz_tt_aux.set_index(['from_node','to_node'])

    for index in taz_tt.index:
        if np.count_nonzero(np.array(taz_tt.loc[index]))!=0:
            taz_tt_aux=taz_tt_aux.drop([index])


    r=pd.DataFrame()

    for index in taz_tt_aux.index:
        s=x[(x.from_zone==index[0])&(x.to_zone==index[1])]
        r=r.append(s)

    for interval in index_column(5).columns:
        c=pd.DataFrame(index=taz_tt_aux.index)
#        taz_tt[interval]=0
        c[interval]=0

        d=r[r.arrival_time_s>=interval[0]]
        d=d[d.arrival_time_s<= interval[1]]


        if len(d)!=0:

            d=d.set_index(['from_zone','to_zone'])

            for index in d.index.unique():
                 c.loc[index]=round(d.travel_time[index].mean(),0)

        taz_tt_aux[interval]=c[interval]

    for index in taz_tt_aux.index:
         taz_tt_aux.loc[index]=taz_tt_aux.loc[index].where(taz_tt_aux.loc[index]!=0,np.sum(np.array(taz_tt_aux.loc[index]))/np.count_nonzero(np.array(taz_tt_aux.loc[index])))
    taz_tt_aux=taz_tt_aux.fillna(0)


    for index in taz_tt_aux.index:
        taz_tt.loc[index]=taz_tt_aux.loc[index]



    x=allcartrips.loc[(allcartrips.travel_mode=='ON_CAR')]

    x=x.reset_index(drop=True)



    taz_tt_aux=pd.DataFrame(pd.DataFrame(columns=index_column(5).columns))
    taz_tt_aux['from_node']=taz_pairs['from_node']
    taz_tt_aux['to_node']=taz_pairs['to_node']
    taz_tt_aux=taz_tt_aux.set_index(['from_node','to_node'])


    for index in taz_tt.index:
        if np.count_nonzero(np.array(taz_tt.loc[index]))!=0:
            taz_tt_aux=taz_tt_aux.drop([index])

    r=pd.DataFrame()

    for index in taz_tt_aux.index:
        s=x[(x.from_zone==index[0])&(x.to_zone==index[1])]
        r=r.append(s)

    for interval in index_column(5).columns:
        c=pd.DataFrame(index=taz_tt_aux.index)
#        taz_tt[interval]=0
        c[interval]=0

        d=r[r.arrival_time_s>=interval[0]]
        d=d[d.arrival_time_s<= interval[1]]


        if len(d)!=0:

            d=d.set_index(['from_zone','to_zone'])

            for index in d.index.unique():
                c.loc[index]=round(d.travel_time[index].mean(),0)

        taz_tt_aux[interval]=c[interval]

    for index in taz_tt_aux.index:
         taz_tt_aux.loc[index]=taz_tt_aux.loc[index].where(taz_tt_aux.loc[index]!=0,np.sum(np.array(taz_tt_aux.loc[index]))/np.count_nonzero(np.array(taz_tt_aux.loc[index])))

    taz_tt_aux=taz_tt_aux.fillna(0)


    for index in taz_tt_aux.index:
        taz_tt.loc[index]=taz_tt_aux.loc[index]




    for index in taz_tt.index:
        if np.count_nonzero(np.array(taz_tt.loc[index]))==0:
            taz_tt.loc[index]=taz_tt.loc[index[1],index[0]]

    ## Travel time for the missing zone to zone
    taz_tt.loc[(2,2)]=(taz_tt.loc[(2,21)]+taz_tt.loc[(21,2)]+taz_tt.loc[(2,6)]+taz_tt.loc[(6,2)]+taz_tt.loc[(2,7)]+taz_tt.loc[(7,2)]+taz_tt.loc[(2,1)]+taz_tt.loc[(1,2)])/8
    taz_tt.loc[(6,6)]=(taz_tt.loc[(6,21)]+taz_tt.loc[(21,6)]+taz_tt.loc[(2,6)]+taz_tt.loc[(6,2)]+taz_tt.loc[(6,7)]+taz_tt.loc[(7,6)]+taz_tt.loc[(6,3)]+taz_tt.loc[(3,6)]+taz_tt.loc[(6,12)]+taz_tt.loc[(12,6)]+taz_tt.loc[(6,13)]+taz_tt.loc[(13,6)])/12
    taz_tt.loc[(8,8)]=(taz_tt.loc[(8,5)]+taz_tt.loc[(5,8)]+taz_tt.loc[(8,3)]+taz_tt.loc[(3,8)]+taz_tt.loc[(8,4)]+taz_tt.loc[(4,8)]+taz_tt.loc[(8,1)]+taz_tt.loc[(1,8)]+taz_tt.loc[(8,14)]+taz_tt.loc[(14,8)])/10
    taz_tt.loc[(9,9)]=(taz_tt.loc[(9,23)]+taz_tt.loc[(23,9)]+taz_tt.loc[(9,10)]+taz_tt.loc[(10,9)]+taz_tt.loc[(9,3)]+taz_tt.loc[(3,9)]+taz_tt.loc[(9,4)]+taz_tt.loc[(4,9)])/8
    taz_tt.loc[(11,11)]=(taz_tt.loc[(11,12)]+taz_tt.loc[(12,11)]+taz_tt.loc[(11,13)]+taz_tt.loc[(13,11)]+taz_tt.loc[(11,15)]+taz_tt.loc[(15,13)])/6
    taz_tt.loc[(18,18)]=(taz_tt.loc[(18,19)]+taz_tt.loc[(19,18)]+taz_tt.loc[(18,16)]+taz_tt.loc[(16,18)]+taz_tt.loc[(18,17)]+taz_tt.loc[(17,18)])/6
    taz_tt.loc[(22,22)]=(taz_tt.loc[(22,21)]+taz_tt.loc[(21,22)]+taz_tt.loc[(22,1)]+taz_tt.loc[(1,22)]+taz_tt.loc[(22,14)]+taz_tt.loc[(14,22)])/6


    taz_tt=taz_tt.reset_index()

    taz_tt.from_node='shar'+ taz_tt.from_node.astype(str)+'i'
    taz_tt.to_node='shar'+taz_tt.to_node.astype(str)+'o'

    taz_tt=taz_tt.set_index(['from_node','to_node'])
    taz_tt=taz_tt.round(0)
    taz_tt=taz_tt.T.to_dict()



    return(taz_tt)



    ##Dictionary of costs

def gen_taxi_cost_dict(dict_tt,tt_u, mode): ## mode: taxi, service: normal/minivan
    ## tt_u: dist_dual

    a=pd.DataFrame.from_dict(dict_tt, orient='index')

    dist=pd.DataFrame.from_dict(tt_u, orient='index')


    if mode=='taxi':
        cost=pd.DataFrame(39+8.5*dist.to_numpy()/1000+5.75*a.to_numpy()/60, columns=a.columns)
        cost=cost.set_index(a.index)
        cost=cost.round(2)


    elif mode=='single_taxi':
        cost=pd.DataFrame(15+6.6*dist.to_numpy()/1000+2.8*a.to_numpy()/60, columns=a.columns)
        cost=cost.set_index(a.index)
        cost=cost.round(2)

    elif mode=='shared_taxi':
        cost=pd.DataFrame(15+5.35*dist.to_numpy()/1000+2*a.to_numpy()/60, columns=a.columns)
        cost=cost.set_index(a.index)
        cost=cost.round(2)


    cost=cost.T.to_dict()


    return(cost)


## Add nodes


def add_taxi_nodes(G,a):## a: taz_wt

    for node in a.keys():
#
        G.add_node('taxi'+node+'i', zone=node, node_type='in_taxi_node', node_graph_type='taxi_graph')#'taxi'+
        G.add_node('taxi'+node+'o', zone=node, node_type='out_taxi_node', node_graph_type='taxi_graph')


def add_on_demand_taxi_single_nodes(G,a):## a: taz_wt

    for node in a.keys():
#
        G.add_node('SMS'+node+'i', zone=node, node_type='in_on_demand_taxi_single_node', node_graph_type='on_demand_single_taxi_graph')
        G.add_node('SMS'+node+'o', zone=node, node_type='out_on_demand_taxi_single_node', node_graph_type='on_demand_single_taxi_graph')

def add_on_demand_taxi_shared_nodes(G,a):## a: taz_wt

    for node in a.keys():
#
        G.add_node('SMS_Pool'+node+'i', zone=node, node_type='in_on_demand_taxi_shared_node', node_graph_type='on_demand_shared_taxi_graph')
        G.add_node('SMS_Pool'+node+'o', zone=node, node_type='out_on_demand_taxi_shared_node', node_graph_type='on_demand_shared_taxi_graph')

 ## Add the edges
def add_taxi_edges(G,a,b,c,d): ## a: taz_tt b: taz_wt, c:taz_dist, d=taz_cost
    # print(a)


    for edge in a.keys():
        G.add_edge('taxi'+edge[0], 'taxi'+edge[1], travel_time=a[edge], taxi_wait_time=b[edge[0][0:len(edge[0])-1]], distance=c[edge]['distance'], taxi_fares=d[edge], edge_type='taxi_edge')





def add_on_demand_taxi_single_edges(G,a,b,c,d): ## a: taz_tt b: taz_wt, c:taz_dist, d=taz_cost


    for edge in a.keys():


        G.add_edge('SMS'+edge[0], 'SMS'+edge[1], travel_time=a[edge], taxi_wait_time=b[edge[0][0:len(edge[0])-1]], distance=c[edge]['distance'], taxi_fares=d[edge], edge_type='on_demand_single_taxi_edge')


    return(G)

def add_on_demand_taxi_shared_edges(G,a,b,c,d): ## a: taz_tt b: taz_wt, c:taz_dist, d=taz_cost


    for edge in a.keys():
        G.add_edge('SMS_Pool'+edge[0], 'SMS_Pool'+edge[1], travel_time=a[edge], taxi_wait_time=b[edge[0][0:len(edge[0])-1]], distance=c[edge]['distance'], taxi_fares=d[edge], edge_type='on_demand_shared_taxi_edge')


    return(G)

