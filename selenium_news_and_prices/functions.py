# script wit general functions that can be used in multiple occasions

from math import ceil
import datetime

# convert time index to 5 minutes 
def dateto5minutes(x):
    minutes=ceil(x.minute/5)*5
    hours=x.hour
    days=x.day
    if minutes==60:
        minutes=0
        hours=x.hour+1
        if hours==24:
            hours=0
            days=x.day+1
    return(datetime.datetime(x.year,x.month,days,hours,minutes))