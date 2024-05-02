# Import packages

import re
import pandas as pd
import sys
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


## Date function
# Checks if this line contains as date and returns it in pd date format if it does
def line_is_date(l):
    is_date = re.match(r'^# +(\d\d-\d\d-\d\d\d\d)', l)
    if is_date:
        #print("Found Date", is_date)
        this_day = is_date[1]
        #convert the string-formatted data to a Pandas date format so we can do computations on it
        return pd.to_datetime(this_day, dayfirst=True) #pd.to_datetime(is_date)
    else:
        return False

## Site Function
def line_is_place(l):
    is_place = re.match(r'## +Location:(.*)', l)
    if is_place:
        #print("Found Place:", is_place)
        this_place = is_place[1]
        return this_place
    else:
        return False

## Find Dive Start Function
def line_is_divestart(l):
    hours_line = re.match(r'^#+ +(.*?:) *(\d?\d:\d\d) *- *(\d?\d:\d\d)', l)
    if hours_line:
        activity = hours_line[2]
        return activity
    else:
        return False
    
## Find Dive End Function
def line_is_diveend(l):
    hours_line = re.match(r'^#+ +(.*?:) *(\d?\d:\d\d) *- *(\d?\d:\d\d)', l)
    if hours_line:
        activity = hours_line[3]
        return activity
    else:
        return False


## Find Observations
def line_is_observation(l):
    obs_line = re.match(r'^##+ Obs:(.*)', l)
    if obs_line:
        is_obs = obs_line[1]
        return is_obs
    else:
        return False


#FUNCTION TO PRODUCE DATFRAME WITH DIVE INFO
def extract_dives(input_file):
    log = open(input_file).read().split("\n")
    days_data = []
    start_data = []
    obs_data = []
    
    this_date = [] 
    brand_new_day = ""
    this_place  = []
    this_start = []
    this_end = []
    this_obs = []
    
    for line in log:
        #FIND DATE
        this_date = line_is_date(line) #Find date
        dates = []
        if this_date is not False: #this is to repeat date until new date is found
            brand_new_day = this_date
            dates.append(this_date)
        else:
            this_date = brand_new_day
            dates.append(brand_new_day)   

        #FIND PLACE    
        this_place = line_is_place(line) 
        if this_place:
            days_data.append({"Date": this_date, "Place": this_place})   
        
        #FIND DIVE START AND END
        this_start = line_is_divestart(line)
        this_end = line_is_diveend(line)
        if this_start and this_end:
            start_data.append({"Date": this_date, "Dive Start": this_start, "Dive End": this_end})
   
        #FIND OBSERVATIONS
        this_obs = line_is_observation(line)
        if this_obs:
            obs_data.append({"Date": this_date, "Observations": this_obs})
    

    # Put it together
    df = pd.DataFrame(days_data)
    start = pd.DataFrame(start_data)
    obs = pd.DataFrame(obs_data)
    print(obs)
    df = obs.merge(df, how = "outer", on = "Date") #obs no good, creating double ups - need to fix
    df =  df.merge(start, how = "outer", on = "Date")
    return df    

# Run the function
df = extract_dives("dive-log.md")
print(df)