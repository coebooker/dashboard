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

    html.H1(children='Super Simple Dash App!'),
    html.H2(children='This is an example of a dash app with an interactive dashboard.'),

    html.H6("Change below to make a new figure:"),

    html.Div([
        "     Day in 4 N=: ",
        dcc.Input(id='my-input', value=1, type='number', debounce=True)
    ]),

    html.Br(),

    dcc.Graph(id='map-fig'),

    dcc.Graph(id='figure-output'),

])

#####################
#  Make Basic Plot  #
#####################
data = pd.read_csv('uber-trip-data/uber-raw-data-apr14.csv')
data["Date/Time"] = pd.to_datetime(data["Date/Time"])


def make_plotb(N):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.arange(N), y=np.random.rand(N),
                             mode='lines',
                             name='Random Data'))

    fig.update_layout(title="Model Output")

    return fig


def map_func():
    px.set_mapbox_access_token(open(".mapbox_token").read())
    df = data
    fig = px.scatter_mapbox(df, lat="centroid_lat", lon="centroid_lon", color="peak_hour", size="car_hours",
                            color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
    return fig


def make_timeplot(data, date):
    dtplot = go.Figure()

    day = pd.Grouper(key="Date/Time", freq="D")
    hour = pd.Grouper(key="Date/Time", freq="60min")

    grouped = data.groupby(day).get_group(date).groupby(hour)
    y = [group[1]["Date/Time"].count() for group in grouped]
    x = [group[0].time() for group in grouped]
    color = [group[0].hour for group in grouped]

    dtplot.add_trace(go.Bar(x=x, y=y))
    dtplot.update_layout(title="Select any of the bars on the histogram to section data by time.")
    dtplot.update_layout(bargap=0)
    temp = go.layout.Colorscale(sequential="viridis",diverging="viridis",sequentialminus="viridis")
    dtplot.update_coloraxes(colorscale='Viridis')
    return dtplot


@app.callback(
    Output('figure-output', 'figure'),
    [Input('my-input', 'value')])
def make_plot(N):
    return make_timeplot(data, datetime.datetime(year=2014, month=4, day=N))


Output('map-fig', 'figure')


def make_map():
    return map_func()


# -------------------------- MAIN ---------------------------- #


# This is the code that gets run when we call this file from the terminal
# The port number can be changed to fit your particular needs
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
