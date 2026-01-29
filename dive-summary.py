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
        this_day = is_date[1]
        #convert the string-formatted data to a Pandas date format so we can do computations on it
        return pd.to_datetime(this_day, dayfirst=True) #pd.to_datetime(is_date)
    else:
        return False

## Site Function
def line_is_place(l):
    is_place = re.match(r'## +Location:(.*)', l)
    if is_place:
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

#Find depth
def line_is_depth(l):
                            
    depth_line = re.match(r'^#+ +(.*?:) *(\d?\d:\d\d) *- *(\d?\d:\d\d), (.*)m', l)
    if depth_line:
        depth = depth_line[4]
        return depth
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
    log = open(input_file).read().split("\n") #read input file line by line
    #Create empty arrays for data
    days_data = []
    start_data = []
    obs_data = []
    depth_data = []
    this_date = [] 
    brand_new_day = ""
    this_place  = []
    this_start = []
    this_end = []
    this_obs = []
    this_depth = []
    
    for line in log:
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
        #FIND DEPTH
        this_depth = line_is_depth(line)
        if this_depth:
            depth_data.append({"Date": this_depth,  "Depth": this_depth})
           

    # Put it together
    df = pd.DataFrame(days_data)

    start = pd.DataFrame(start_data)
    obs = pd.DataFrame(obs_data)
    depth = pd.DataFrame(depth_data)
    df =  df.merge(start, how = "outer", on = "Date")
    df['Dive End'] = pd.to_datetime(df['Dive End'], format ="%H:%M") #, format ="%H:%M"
    df['Dive Start'] = pd.to_datetime(df['Dive Start'], format ="%H:%M")
    df['Dive Time'] = (df['Dive End'] - df['Dive Start'])#.total_seconds()/3600
    df['Dive Time'] = df['Dive Time'].astype(int)/60000000000
    df["Observations"] = obs["Observations"]
    df['Depth'] = depth['Depth']
    return df 

    print(df)

# Run extract dives to create dataframe from dive log data.
dives = extract_dives("dive-log.md")

df3 = extract_dives("dive-log.md")


#FUNCTIONs TO LOOK AT OBSERVATIONS
#Categorise Obs
#  or row["Observations"] == ' '
def categoriseobs(row):
        if row["Observations"] == ' whitetip' or row["Observations"] == ' hammerhead' or row["Observations"] == ' leopard shark' or  row["Observations"] == ' blacktip' or row["Observations"] == ' tawny nurse shark' or row["Observations"] == ' wobbegong' or row["Observations"] == ' whale shark' or row["Observations"] == 'grey reef shark':
            return "Shark"
        elif row["Observations"]== ' octopus' or row["Observations"] == ' cuttlefish' or row["Observations"] == ' squid' or row["Observations"] == ' octopus':  
            return "Cephlapod"
        elif row["Observations"] == ' whitespot eagle ray' or row["Observations"] == ' bluespot lagoon ray' or row["Observations"] == ' manta'or row["Observations"] == ' eagle ray'  or row["Observations"] == ' mobula':
            return "Ray"
        elif row["Observations"] == ' green turtle' or row["Observations"] == ' hawksbill Turtle' or row["Observations"] == ' turtle':
            return "Turtle"
        elif row["Observations"] == ' Moray'or row["Observations"] == ' moray' or row["Observations"] == ' blue grouper' or row["Observations"] == ' bumphead': 
            return "Notable Fish"
        elif row["Observations"] == ' Maori Wrasse' or row["Observations"] == ' wally':
            return "Maori Wrasse"
        elif row["Observations"] == ' CoTS':
            return "CoTS"
        elif row["Observations"] == ' clown' or row["Observations"] == ' clarks aneomonefish' or row["Observations"] == ' tomato anemonefish'or row["Observations"] == ' nemo':
            return "Anemone Fish"
        elif row["Observations"] == ' nudi branch' or row["Observations"] == ' sea snake':
            return "Other"

#Summarise
#Summarise animals. 
def summarise_obs(input_file):
    df  = input_file
    df["Observations"] = df["Observations"].str.split(',')
    df = df.explode("Observations")
    df["ObCat"] = df.apply( lambda row: categoriseobs(row), axis = 1)
    df  =  df.dropna()
    
    

    return(df)

#FUNCTION TO MAKE A MAP
def map_dives(input_file):
    geolocator = Nominatim(user_agent="your_app_name", timeout = 100)
    df3 = input_file
    df3["Place_Loc"] = df3["Place"].apply(lambda x: geolocator.geocode(x)) #applies geolocator to Place names, finds their location
    print("Couldn't locate:",  df3["Place_Loc"] == "None")
    df3 = df3.dropna() # Drop rows with missing or invalid values in the 'mag' column
    # I would  like to print a list of places that get dropped from this list so I can fix them in the log
   

    df3["Place_Lat"] = df3["Place_Loc"].apply(lambda x: x.latitude)
    df3["Place_Lon"] = df3["Place_Loc"].apply(lambda x: x.longitude)
    print(df3)
    fig = px.scatter_geo(df3, lat="Place_Lat", lon='Place_Lon',
                     hover_name='Place', 
                     title='Dive Locations', width=1500, height=750, )

    fig.update_geos(
        showocean = True, oceancolor = 'rgb(131, 191, 212)',
        showland = True, landcolor = 'rgb(190, 229, 192)',
        showcoastlines=True, coastlinecolor= 'rgb(15, 114, 121)',
        center=dict(lon=3, lat=82),
        fitbounds = "locations"
    )
    
    fig.update_traces(marker=dict(size=11, color = 'rgb(237, 239, 93)',  line=dict(width=2,
                                        color='rgb(57, 171, 126)')))
    return(fig)


#['rgb(36, 86, 104)', 'rgb(15, 114, 121)', 'rgb(13, 143, 129)', 'rgb(57, 171, 126)', 'rgb(110, 197, 116)', 'rgb(169, 220, 103)', 'rgb(237, 239, 93)']

obs = summarise_obs(dives)
print(obs)
mapfigure = map_dives(df3) #runs on df3 rather than dives because map function doesn't like dives dataframe for some reason
#new = old.filter(['A','B','D'], axis=1)
dives_simple = dives.filter(["Date", "Place", "Dive Time", "Depth"])



# MAKE A DASHBOARD
import dash
from dash import dcc, html, Output, Input, dash_table
import plotly.express as px

app = dash.Dash(__name__)
#switch off (with comment) server to run in vs code, on to run for deployment
server = app.server

#markdown text
markdown_text = '''
This dashboard displays data from my recreational dive log. Dive log data is recorded in a markdown file. The script that reads dive data file, and creates the dashboard is on GitHub (https://github.com/florence-sefton/dive-log).
'''
app.layout = html.Div([
    #html, css (css style)
        html.H1("Flo's Dive Log", style = {'color': 'rgb(36, 86, 104)', 'textAlign': 'center', 'fontsize': 40}), #.H1 header 1, remember to spell colour wrong
    #markdown
        dcc.Markdown(markdown_text,  style = {'color': 'rgb(15, 114, 121)','textAlign': 'center'}),
            dcc.Tabs([
                dcc.Tab(label = "Dive Map",  style = {'color': 'rgb(36, 86, 104)'}, children = [
                dcc.Graph(figure = mapfigure),
            ]),
                dcc.Tab(label='Seen On Dives', style = {'color': 'rgb(36, 86, 104)'}, children=[
                     #make droopdown, to select which Obcat value to view a pie chart break down for
                    #dcc.Graph(figure = (px.pie(obs, names='ObCat', title= "Things I've seen", color_discrete_sequence=px.colors.sequential.Aggrnyl))), 
                    
                    dcc.Dropdown(options=obs.ObCat.unique(), value = 'Shark', id = 'dropdown'),
                     #create elemenent for the pie chart linked do dropdown
                     dcc.Graph( id='graph-with-dropdown'),  
                     ]),

                dcc.Tab(label = "Dive data",  style = {'color': 'rgb(36, 86, 104)'}, children = [
                #frequency histogram plotting dive times
                
                dcc.Graph(figure = px.histogram(dives, x = "Dive Time", nbins = 15, 
                labels = { "Dive Time":'Dive Time (minutes)', "count":  'Number of dives'}, 
                template = "simple_white", title = "Dive time distribution:", 
                color_discrete_sequence = px.colors.sequential.Aggrnyl, )),
                #bar plot showing number of dives per year
                dcc.Graph(figure = px.bar(dives.groupby(dives.Date.dt.year).size().reset_index(name='counts'), 
                x='Date', y = 'counts', 
                template = "simple_white", 
                labels = {"Date" : "Year", "counts": "Number of Dives"}, title = "Dives per year:", 
                color_discrete_sequence=px.colors.sequential.Aggrnyl)),
                
                #dcc.Graph(figure = px.scatter(dives, x = "Depth", y = "Dive Time"))
                
                
            ]),

                
              



       
            dcc.Tab(label = 'Dive Log', children = [
            #    dash_table.DataTable(data = dives.to_dict('records'), columns=[{'name': i, 'id': i} for i in dives.columns[3:4]]),
            dash_table.DataTable(data = dives_simple.to_dict('records'), columns=[{'name': str(i), 'id': str(i)} for i in dives_simple.columns]),
            
            ]),
        ]),
        
         ])

#callback
@app.callback(
    Output(component_id = 'graph-with-dropdown', component_property ='figure'),
    Input(component_id = 'dropdown',  component_property  = 'value'),
)


def update_figure(ObCat):
    filtered_df  =  obs[obs.ObCat==ObCat]
    figure = px.pie(filtered_df, names='Observations', title=f'Types of {filtered_df.ObCat.unique()[0]} seen:', color_discrete_sequence=px.colors.sequential.Aggrnyl)
    return figure

if __name__ == "__main__":
    app.run_server(debug=True) #debug true give useful debug message 

#ctr c to quit





