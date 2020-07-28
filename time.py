# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 13:52:13 2019

@author: Francisco
"""
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import datetime as datetime
import time


    




h=0
m=0
s=0
x=0
unique_st=list(tt.start_time.unique())
while x < 50:
    
    a= str('%02d:%02d:%02d'% (h, m ,s))
    print(a)
    if (a in unique_st): 
        print('table updated')
        tt_x=tt[tt.start_time==a]
        tt_x=tt_x.reset_index(drop=True)
##assigning the travel times at 8:30
        for i in range(len(tt_x)):
            for j in range(len(tt_u)):
                if tt_x.from_link[i]==tt_u.from_link[j] and tt_x.to_link[i]==tt_u.to_link[j]:
                    tt_u.loc[j,'travel_time']=tt_x.loc[i,'travel_time']
                    tt_u.loc[j,'start_time']=tt_x.loc[i,'start_time']
                    tt_u.loc[j,'end_time']=tt_x.loc[i,'end_time']
      
        k=pd.concat([tt_u,tt_x]) ## joining tt_x and tt_u
        k=k.drop_duplicates(keep=False) ## storing the non duplicates values
        tt_u=pd.concat([tt_u,k])   ## joining tt_u with the non duplicates values     
        tt_u=tt_u.drop_duplicates(keep='first') ## removing the duplicates
        tt_u= tt_u.sort_values(['from_link','to_link','start_time','end_time']) ## sorting
        tt_u=tt_u.reset_index(drop=True)       ## reindexing       
        
    s=s+1
    if s>=60:
        m=m+1
        s=0
        x=x+1 
    if m>=60:
        m=0
        h=h+1
        

       
#            
#a=str('17:30:00')
#
#
#
#
#a=datetime.datetime.now()
#a=datetime.datetime.strftime(a,'%H:%M:%S')
#
#turning=turning.sort_values(['from_link','to_link'])
#
#
#
#a=str('08:30:00')
#b=str('08:00:00')
#tt_prima=pd.DataFrame(columns=(['from_link', 'to_link','start_time','end_time', 'travel_time']))
#for i in range (len(tt)):
#    if b==tt.start_time[i]:
#          x=pd.DataFrame([[tt.from_link[i], tt.to_link[i],tt.start_time[i], tt.end_time[i], tt.travel_time[i]]], columns=['from_link', 'to_link','start_time','end_time', 'travel_time'])
#          tt_prima=tt_prima.append(x, ignore_index=True)
#
#tt_prima=tt_prima.drop(['start_time','end_time','travel_time'],axis=1)
#
#e=pd.concat([turning,tt_prima])
#k=e.drop_duplicates(keep=False)
#data=pd.DataFrame()

    






     

pd.DataFrame([[links_p.seq_id[j],links_p.x[j],links_p.y[j]]],columns=['seq_id','x', 'y'])
b=tt.start_time[61364]
c=tt.start_time[4454]
b==c

for i in range(len(tt)):
    tt.start_time[i]=datetime.datetime.strptime(tt.start_time[i], '%H:%M:%S')
    tt.end_time[i]=datetime.datetime.strptime(tt.end_time[i], '%H:%M:%S')
    
    
    



b=datetime.datetime.strftime(tt.start_time[6978], '%H:%M:%S')
round_down(a)

dt=round_time(a,round_to=60*5)
print (round_time(a,round_to=60*10))
a.hour





for i in range
b=tt.start_time[105905]
h=int(tt.end_time[11][0]+tt.end_time[11][1])
m=int(tt.end_time[11][3]+tt.end_time[11][4])
s=int(tt.end_time[11][6]+tt.end_time[11][7])




b=datetime.datetime.strptime(tt.start_time[6978], '%H:%M:%S')
print (round_time(x,round_to=60*5))



print (round_time(round_to=60*10))

x=datetime.datetime(2012,12,31,23,29,59)

datetime.strftime(b,'%H')

c=int(time.strptime(tt.end_time[11], '%H'))

c=int('%H')


#Input Date String
t = "12/20/2014 15:25:05 pm"

#Return a datetime corresponding to date string
c = datetime.strptime(b, '%H:%M:%S')
