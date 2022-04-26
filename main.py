# Good modules to have
from datetime import datetime

import numpy as np, pandas as pd
import random, json, time, os

# Required Modules
import plotly.graph_objects as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import datetime

# Add basic CSS
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# This is the main application
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Do not bother us with exceptions
app.config.suppress_callback_exceptions = True

#################################################
################# Layout ########################
#################################################

app.layout = html.Div([

    html.H3(children='Dash-Uber Data App'),
    html.H6(children='Select different days using the date picker or by selecting different time frames on the histogram.'),

    html.Div([
        dcc.DatePickerSingle(date=datetime.date.fromisoformat("2014-04-01"), id='date-pick')
    ]),

    html.Div([
        dcc.Input(id='map-in', value=0, type='number', debounce=True)
    ]),

    html.Br(),

    dcc.Graph(id='map-fig'),

    dcc.Graph(id='time-plot'),

])

#####################
#  Make Basic Plot  #
#####################
UberData = pd.read_csv('uber-trip-data/uber-raw-data-apr14.csv')
UberData["Date/Time"] = pd.to_datetime(UberData["Date/Time"])


def map_func(df):
    print(open("mapbox_token.txt").read())
    df = df.head(50)
    px.set_mapbox_access_token(open("mapbox_token.txt").read())
    fig = px.scatter_mapbox(df, lat="Lat", lon="Lon", color="Date/Time",
                            color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
    fig.update_layout(title="Map Output")
    return fig 

def make_timeplot(data, date):

    dtplot = go.Figure()

    day = pd.Grouper(key="Date/Time", freq="D")
    hour = pd.Grouper(key="Date/Time", freq="60min")

    grouped = data.groupby(day).get_group(date).groupby(hour)

    y = [group[1]["Date/Time"].count() for group in grouped]
    x = [group[0].hour for group in grouped]
    X_BINS = [str(i)+":00" for i in range(0,24)]

    mark = go.bar.Marker(color=x, colorscale='viridis_r')
    temp = go.Bar(x=X_BINS, y=y, marker=mark)
    #temp = go.Histogram(x=grouped["Date/Time"], nbinsx=24, histfunc='count', marker=go.histogram.Marker(cauto=True, colorscale="Viridis_r"))

    dtplot.add_trace(temp)
    dtplot.update_layout(title="Select any of the bars on the histogram to section data by time.")
    dtplot.update_layout(bargap=0)

    return dtplot


@app.callback(
    Output('time-plot', 'figure'),
    [Input('date-pick', 'date')]
)
def make_plot(date):
    temp_day = datetime.date.fromisoformat(date)
    return make_timeplot(UberData, datetime.datetime(year=2014, month=4, day=temp_day.day))


@app.callback(Output('map-fig', 'figure'), [Input('date-pick', 'useless')])
def make_map(useless):
    return map_func(UberData)



# -------------------------- MAIN ---------------------------- #

# This is the code that gets run when we call this file from the terminal
# The port number can be changed to fit your particular needs
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
