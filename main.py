# Good modules to have
import numpy as np, pandas as pd
import random, json, time, os

# Required Modules
import plotly.graph_objects as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

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
        "     Number of points, N=: ",
        dcc.Input(id='my-input', value=10, type='number', debounce=True)
    ]),

    html.Br(),

    dcc.Graph(id='figure-output'),

])


#####################
#  Make Basic Plot  #
#####################

@app.callback(
    Output('figure-output', 'figure'),
    Input('my-input', 'value'))
def make_plot(N):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.arange(N), y=np.random.rand(N),
                             mode='lines',
                             name='Random Data'))

    fig.update_layout(title="Model Output")

    return fig

def make_timePlot():
    fig = go.Figure
    fig.add_trace(go.Histogram())


# -------------------------- MAIN ---------------------------- #


# This is the code that gets run when we call this file from the terminal
# The port number can be changed to fit your particular needs
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True, use_reloader=False)