# -*- coding: utf-8 -*-
"""
Created on Wed May  1 15:51:17 2019

@author: Francisco
"""


from functions import import_tt_turnings
from datetime import datetime
import pandas as pd




tt,tt_u=import_tt_turnings()


def dict_tt(tt_u,tt):
    a=tt.start_time.drop_duplicates(keep='first')
    b=tt.end_time.drop_duplicates(keep='first')

    tt_dict={}
    for i in range(len(tt_u)):
        intervals={}
        for j in range(len(a)):
            h=float(a[j][0:2])
            m=float(a[j][3:5])
            s=float(a[j][6:8])
            ts=(h*60+m)*60+s
            
            hb=float(b[j][0:2])
            mb=float(b[j][3:5])
            sb=float(b[j][6:8])
            tsb=(hb*60+mb)*60+sb
            
            intervals[(ts,tsb)]=tt_u.travel_time[i]
        
            tt_dict[(tt_u.from_link[i],tt_u.to_link[i])]=intervals




#
#
#prueba={(1,2):{('a','b'):{},('c','d'):{} }, (3,4):{('a','b'):{},('c','d'):{} }}
#
#
#p_tt=pd.DataFrame({'from_link':[1,3],'to_link':[2,4],'travel_time':[15,45]})
#
#
#for i in range(len(p_tt)):
#    for links, interval in prueba.items():
#        for key in interval:
#            if links==(p_tt.from_link[i],p_tt.to_link[i]):
#                prueba[links][key]=p_tt.travel_time[i]
#    
#
#
#for i in range(len(tt_u)):
#    for links, interval in tt_dict.items():
#        for key in interval:
#            if links==(tt_u.from_link[i],tt_u.to_link[i]):
#                tt_dict[links][key]=tt_u.travel_time[i]
#  
#
#tt_dict[(1,161)][(0,299)]=45
#tt_dict[(2,47)][(0,299)]=10     
#
#prueba[(1,2)][('a','b')]=0
#prueba[(3,4)][('a','b')]=1000
#i=0
#key=(1,161)           
#interval=(0,299)            
#

#
#
#intervals={}
#
#for j in range(len(a)):
#        h=float(a[j][0:2])
#        m=float(a[j][3:5])
#        s=float(a[j][6:8])
#        ts=(h*60+m)*60+s
#    
#        hb=float(b[j][0:2])
#        mb=float(b[j][3:5])
#        sb=float(b[j][6:8])
#        tsb=(hb*60+mb)*60+sb
#
#        intervals[(ts,tsb)]={}
#
#tt_dict={'weight':{}}
#
#for i in range(0,9):
#    for key in intervals:
#        intervals[(key)]=tt_u.travel_time[i]       
#        tt_dict['weight'][(tt_u.from_link[i],tt_u.to_link[i])]=intervals[(key)]
#
#
#
#
#
#
#for i in range(len(tt_u)):
#   tt_dict['weight'][(tt_u.from_link[i],tt_u.to_link[i])]=intervals
#
#
#
#
#
#
#S=nx.DiGraph()
#S.add_node(1)
#S.add_node(2)
#
#S.add_edge(1,2, weight=my_dict) 
#S.edges.data()    
#
#S[1][2]['weight']['weight']
#
#for i in range(1,255):
#    del my_dict[('Aly','Siv')][i]
#
#tt_dict={'weight':True}
#tt_dict[{'weight':{(tt_u.from_link[i],tt_u.to_link[i]):0}}
#
#tt_dict['weight'][(1,161)]=40
#tt_dict['weight'][(1,161)]=40
#tt_dict={}
#tt_dict['weight']=True
#
#
#   
#
#
#
#
#
#
#
#
#intervals[(1,4)]={}
#intervals[(3,4)]={}
#time={}
#for i in range
#   
#a=tt.end_time[0]
#
#unique=np.unique(list(dict.values(a['from_node'])))
#
#h=float(a[0:2])
#m=float(a[3:5])
#s=float(a[6:8])
#s=(h*60+m)*60+s
#
#tt_dict['weight']={(3,2):0}   
# 
#
#    
#    
#tt_dict={'weight':{(tt_u.from_link[i],tt_u.to_link[i]):0}}
#
#
#
#my_dict={'weight':{(1,161):0}}
#my_dict['weight'][(1,161)]={(28880,29100):45}
#
#
#
#my_dict={'weight':{(1,161):{(28880,29100):0}}}
#
#my_dict['weight'][(1,161)][(28880,29100)]
#my_dict['weight']=my_dict['weight'][('start time','end_time')]
#
#[('start time','end_time')]
#
#
#
#
#
#
#v='start time'
#
#u='end_time'
#
#my_dict['weight'][(v,u)]
