## Import Libraries

import datetime as dt
import pandas as pd
import numpy as np
from urllib.request import urlopen
import json

## plotly
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

## dash libraries
#from jupyter_dash import JupyterDash 
import dash
#import dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
#from dash.dependencies import Output, Input
from dash import dcc
from dash import html

from flask import Flask

# Set up application and server 

application = dash.Dash(__name__)
server = application.server


## read in csv as df
## read in csv as df
url_1 = 'https://github.com/stefan-faulkner/team156data/blob/master/all_zips_forecast_method1.csv?raw=true'

df = pd.read_csv(url_1,dtype = {'Zipcode': str}).rename(columns={"1Yr-ROI":"1 Year ROI","3Yr-ROI":"3 Year ROI","5Yr-ROI":"5 Year ROI"})


## zip code & county data, from https://simplemaps.com/data/us-zips
url_2 = 'https://github.com/stefan-faulkner/team156data/blob/master/uszips.csv?raw=true'

counties_df = pd.read_csv(url_2, dtype = {'zip': str})

## merge county df columns of interest with df
df = df.merge(counties_df[['zip','lat','lng','city','state_id','state_name','county_name','county_fips']], left_on = 'Zipcode', right_on='zip', how='inner')


## counties-fips json data
## used the same counties source as in this reference: https://plotly.com/python/choropleth-maps/
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

## any of the FIPS in the df that should have a leading 0 don't have it there 
## it was easier to truncate a leading zero from the FIPS json than add one to the df FIPS data

adj_features = []
for feature in counties['features']:
    if feature['id'][0] == '0':
        feature['id'] = feature['id'][1:]
    adj_features.append(feature)

adj_counties = {'type': 'FeatureCollection', 'features': adj_features}


####FIRST FIGURE

## choropleth reference: https://plotly.com/python/choropleth-maps/
## more choropleth help: https://plotly.com/python/reference/choropleth/
## slider reference: https://support.sisense.com/kb/en/article/plotly-choropleth-with-slider-map-charts-over-time

data_slider1 = []
steps1 = []
years1 = ['1 Year ROI','3 Year ROI','5 Year ROI']

## create data slider
for i,year in enumerate(years1):
    ##  create working df for each year
    df_segmented =  df[['county_fips',year]]
    
    ## aggregate data into county-level averages since i couldn't get zip codes to work
    df_segmented = df_segmented.groupby('county_fips').agg('mean').reset_index()

    ## df has to go into this dict format to work for the slider
    ## data range for color bar is manually set with zmin and zmax - I manually chose these to show color differences
    data_each_yr = dict(
                        type='choropleth',
                        name = year,
                        geojson=adj_counties,
                        locations = df_segmented['county_fips'],
                        z=df_segmented[year],
                        zmin = -1,
                        zmax = 1,
                        colorscale = "RdBu",
                        colorbar= {'title':'Forecasted ROI'})

    ## append each year's dict to slider list
    data_slider1.append(data_each_yr)
    
    ## create the slider steps
    step = dict(method='restyle',args=['visible', [False] * len(years1)], label='ROI: {}'.format(year))
    step['args'][1][i] = True
    steps1.append(step)

## create slider
sliders1 = [dict(active=0, pad={"t": 1}, steps=steps1)]

## graph layout details
layout1 = dict(title ='Projected ROI Over Time By County', geo=dict(scope='usa',
                       projection={'type': 'albers usa'}),
              sliders=sliders1, 
              height = 600,
              width = 1200)

## create figure
fig1 = dict(data=data_slider1, layout=layout1)



#RGB COLOURS --> https://htmlcolorcodes.com/

application.layout = html.Div([
html.Div([
        html.Div([    # Feel free to make any changes to the colour or title as the team sees fit 
                html.H1('Automated Real Estate Appraisal Visualization Tool', style = {'textAlign': 'center',
                                                                                 'color': 'black',
                                                                                 'fontSize': '34px',
                                                                                 'padding-top': '2px'},
                        ),
                html.P('By team156', style = {'textAlign': 'center',
                                                      'color': 'black',
                                                      'fontSize': '22px'},
                    )
                ],
            style = {'backgroundColor': '#85929E',
                     'height': '150px',
                     'display': 'flex',
                     'flexDirection': 'column',
                     'justifyContent': 'center'}
            ) ])
    , html.Div([dcc.Graph(figure=fig1,style={'justifyContent': 'center'})]) #wanted to be fully centered but not working 
])




if __name__ == '__main__':
    application.run_server(debug = True)
    
    
    