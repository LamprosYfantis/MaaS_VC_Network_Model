# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 16:02:07 2019

@author: Francisco
"""

import datetime
def round_time(dt=None, round_to=60):
   if dt == None: 
       dt = datetime.datetime.now()
   seconds = (dt - dt.min).seconds
   rounding = (seconds+round_to/2) // round_to * round_to
   return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

