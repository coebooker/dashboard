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

    dcc.Graph(id='figure-output'),

])


#####################
#  Make Basic Plot  #
#####################
data = pd.read_csv('uber-trip-data/uber-raw-data-apr14.csv')
data["Date/Time"] = pd.to_datetime(data["Date/Time"])


@app.callback(
     Output('figure-output', 'figure'),
     Input('my-input', 'value'))
def make_plot(N):
    return make_timePlot(data, datetime.datetime(year=2014, month=4, day=N))


def make_timePlot(data, date):
    dtplot = go.Figure()

    day = pd.Grouper(key="Date/Time", freq="D")
    hour = pd.Grouper(key="Date/Time", freq="60min")

    grouped = data.groupby(day).get_group(date).groupby(hour)
    y = [group[1]["Date/Time"].count() for group in grouped]
    x = [group[0].hour for group in grouped]

    dtplot.add_trace(go.Bar(x=x,y=y))
    dtplot.update_layout(title="Select any of the bars on the histogram to section data by time.")
    dtplot.update_layout(bargap=0)
    dtplot.update_layout(colorway=px.colors.sequential.Viridis)
    dtplot.update_coloraxes(colorscale=px.colors.sequential.Viridis, showscale=True)
    return dtplot

# -------------------------- MAIN ---------------------------- #


# This is the code that gets run when we call this file from the terminal
# The port number can be changed to fit your particular needs
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
