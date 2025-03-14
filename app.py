# Import packages
import re
import pandas as pd
import sys
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
#for maps
import plotly.express as px
from geopy.geocoders import Nominatim

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
        if this_date is not False: #this is to repeat date until new date is found, 
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
            obs_data.append({"Date": this_date,  "Observations": this_obs})
    


    # Put it together
    df = pd.DataFrame(days_data)
    
    start = pd.DataFrame(start_data)
    obs = pd.DataFrame(obs_data)
    df =  df.merge(start, how = "outer", on = "Date")
    df['Dive End'] = pd.to_datetime(df['Dive End'])
    df['Dive Start'] = pd.to_datetime(df['Dive Start'])
    df['Dive Time'] = (df['Dive End'] - df['Dive Start'])#.total_seconds()/3600
    df['Dive Time'] = df['Dive Time'].astype(int)/60000000000
    df["Observations"] = obs["Observations"]
    
    #dive_time = end_time-start_time
    #dive_time = dive_time.total_seconds()
    
    print(df)
    return df 

# Run the function
df = extract_dives("dive-log.md")
df3 = extract_dives("dive-log.md")
#print(df)

#FUNCTIONs TO LOOK AT OBSERVATIONS
#Categorise Obs
def categoriseobs(row):
        if row["Observations"] == ' Whitetip'  or row["Observations"] == ' Blacktip':
            return "Shark"
        elif row["Observations"]== ' Octopus' or row["Observations"] == ' Cuttlefish' or row["Observations"] == ' squid':  
            return "Cephlapod"
        elif row["Observations"] == ' Whitespot Eagle Ray' or row["Observations"] == ' Blue Spot Lagoon Ray':
            return "Ray"
        elif row["Observations"] == ' Green Turtle' or row["Observations"] == ' Hawksbill Turtle' :
            return "Turtle"
        elif row["Observations"] == ' Moray'or row["Observations"] == ' Moree': 
            return "Moray Eel"
        elif row["Observations"] == ' Maori Wrasse' or row["Observations"] == ' wally':
            return "Maori Wrasse"
        elif row["Observations"] == ' CoTS':
            return "CoTS"
    

#Summarise
#Summarise animals. 
def summarise_obs(input_file):
    df  = input_file
    df["ObCat"] = df.apply( lambda row: categoriseobs(row), axis = 1)
    df2 = df.groupby(["ObCat"]).size().reset_index(name='counts')
    fig = px.pie(df2, values='counts', names='ObCat', title='Things I have seen:')
    return(df)

#FUNCTION TO MAKE A MAP
def map_dives(input_file):
    geolocator = Nominatim(user_agent="your_app_name", timeout = 100)
    df3 = input_file
    df3["Place_Loc"] = df3["Place"].apply(lambda x: geolocator.geocode(x)) #applies geolocator to Place names, finds their location
    df3 = df3.dropna() # Drop rows with missing or invalid values in the 'mag' column
    print("no none", df3)
    # I would  like to print a list of places that get dropped from this list so I can fix them in the log
    df3["Place_Lat"] = df3["Place_Loc"].apply(lambda x: (x.latitude))
    df3["Place_Lon"] = df3["Place_Loc"].apply(lambda x: x.longitude)

    #print(df)
    
    fig = px.scatter_geo(df3, lat='Place_Lat', lon='Place_Lon',
                     hover_name='Place', 
                     title='Dive Locations')
    #fig.show()
    return(fig)



#The plots

#figure2 = summarise_obs(df)
dives = summarise_obs(df)

df = summarise_obs(df)
mapdata = map_dives(df3)
print("Dives:", dives)



# MAKE A DASHBOARD
import dash
from dash import dcc, html, Output, Input, dash_table
import plotly.express as px




app = dash.Dash(__name__)
#server = app.server

#markdown text
markdown_text = '''
This dashboard displays data from dive log.
'''
app.layout = html.Div([
    #html, css (css style)
        html.H1("Flo's Dive Log", style = {'color': 'blue', 'fontsize': 40}), #.H1 header 1, remember to spell colour wrong
    #markdown
        dcc.Markdown(markdown_text,),

        
            dcc.Tabs([
                dcc.Tab(label='Seen On Dives', children=[
                     #make droopdown, to select which Obcat value to view a pie chart break down for
                   dcc.Graph(figure = (px.pie(dives, names='ObCat', title= "Things I've seen", color_discrete_sequence=px.colors.sequential.Aggrnyl))), 
                     dcc.Dropdown(options=dives.ObCat.unique(), value = 'Shark', id = 'dropdown'),
                     #create elemenent for the pie chart linked do dropdown
                     dcc.Graph( id='graph-with-dropdown'),  
                     ]),

                dcc.Tab(label = "Dive Map", children = [
                dcc.Graph(figure = mapdata),
            ]),
            dcc.Tab(label = "Dive data", children = [
                dcc.Graph(figure = px.bar(dives.groupby(dives.Date.dt.year).size().reset_index(name='counts'), 
                x='Date', y = 'counts', 
                template = "simple_white", 
                labels = {"Date" : "Year", "counts": "Number of Dives"}, title = "Dives per year:", 
                color_discrete_sequence=px.colors.sequential.Aggrnyl)),

                dcc.Graph(figure = px.histogram(dives, x = "Dive Time", nbins = 10, labels = {'count':'Number of dives', "Dive Time":'Dive Time (minutes)'}, template = "simple_white", title = "Dive time distribution", color_discrete_sequence = px.colors.sequential.Aggrnyl, )),
            ]),
            dcc.Tab(label = 'Dive Log', children = [
                dash_table.DataTable(data = dives.to_dict('records'), columns=[{'name': i, 'id': i} for i in dives.columns[0:4]]),
            ]),
        ]),
        
         ])

#callback
@app.callback(
    Output(component_id = 'graph-with-dropdown', component_property ='figure'),
    Input(component_id = 'dropdown',  component_property  = 'value'),
)


def update_figure(ObCat):
    filtered_df  =  dives[dives.ObCat==ObCat]
    figure = px.pie(filtered_df, names='Observations', title=f'Types of {filtered_df.ObCat.unique()[0]} seen:', color_discrete_sequence=px.colors.sequential.Aggrnyl)
    return figure

if __name__ == "__main__":
    app.run_server(debug=True) #debug true give useful debug message 

#ctr c to quit




