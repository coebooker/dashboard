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
    html.Div([
        html.H3('DASH-UBER DATA APP',
                style=dict(
                    [('font-family', 'open sans'), ('font-weight', 700), ('letter-spacing', '2.1px'),
                     ('font-size', '21px'), ('padding-left', '12px')])),

        html.Tbody(
            'Select different days using the date picker or by selecting different time frames on '
            'the histogram.',
            style=dict([('padding-left', '30px')])),

        html.Div([
            dcc.DatePickerSingle(date=datetime.date.fromisoformat("2014-04-01"), id='date-pick')
        ], style=dict([('padding', '15px')])),

        html.Div([
            dcc.Input(id='map-in', type='number', debounce=True)
        ], style=dict([('padding', '15px')])),

        html.Div([
            dcc.Dropdown(id='time-pick', options=[dict(label=str(i) + ":00", value=i) for i in range(0, 24)],
                         placeholder="Select Certain Hours",
                         multi=True,
                         style=dict([('color', 'black')]))
        ], style=dict([('padding', '15px')]))
    ], style=dict([('padding', '30px'), ('max-width', '450px')]), ),

    html.Div([
        dcc.Graph(id='map-fig'),
        html.Tbody(children="Select any of the bars on the histogram to section data by time."),
        dcc.Graph(id='time-plot')
    ], style=dict(
        [('responsive', True), ("background-color", "dimgray"), ('display', 'flex'), ('flex-direction', 'column')]))
],
    style=dict([('responsive', True), ('display', 'flex'), ('flex-direction', 'row'), ("background-color", "#2F2F2E"),
                ("color", 'white'), ('padding', '0px')]))

#####################
#  Make Plot  #
#####################
UberData = pd.read_csv('uber-trip-data/uber-raw-data-apr14.csv')
UberData["Date/Time"] = pd.to_datetime(UberData["Date/Time"])


def map_func(df, date):
    df = df.head(50)
    px.set_mapbox_access_token(open("mapbox_token.txt").read())
    fig = px.scatter_mapbox(df,
                            lat="Lat",
                            lon="Lon",
                            color="Date/Time",
                            color_continuous_scale=px.colors.cyclical.IceFire,
                            size_max=15, zoom=10)
    fig.update_layout(title="Map Output", paper_bgcolor='dimgray',
                      plot_bgcolor='dimgray')
    fig.update_layout(bargap=0,
                      margin=dict(t=27, l=2, r=2, b=27),
                      font=dict(color='white'),
                      paper_bgcolor='dimgray',
                      plot_bgcolor='dimgray',
                      width=600,
                      height=400,
                      autosize=True)
    return fig


def make_timeplot(data, date, time):
    dtplot = go.Figure()

    day = pd.Grouper(key="Date/Time", freq="D")
    hour = pd.Grouper(key="Date/Time", freq="60min")

    grouped = data.groupby(day).get_group(date).groupby(hour)

    y = [group[1]["Date/Time"].count() for group in grouped]
    x = [group[0].hour for group in grouped]

    yString = [str(i) for i in y]
    xString = [str(i) + ":00" for i in range(0, 24)]

    mark = go.bar.Marker(color=x,
                         colorscale='viridis_r')

    temp = go.Bar(x=xString,
                  y=y,
                  marker=mark)

    dtplot.add_trace(temp)

    dtplot.update_layout(bargap=0,
                         margin=dict(t=27, l=2, r=2, b=27),
                         font=dict(color='white'),
                         paper_bgcolor='dimgray',
                         plot_bgcolor='dimgray',
                         width=600,
                         height=400,
                         autosize=True)

    dtplot.update_traces(text=yString,
                         textposition='outside',
                         hoverinfo='x',
                         selectedpoints=time, selector=dict(type='bar'),
                         selected=dict(marker=dict(color='white')))

    dtplot.update_yaxes(showticklabels=False,
                        showgrid=False,
                        fixedrange=True)
    dtplot.update_xaxes(showgrid=False,
                        fixedrange=True)

    return dtplot


def selectBar(dtplot, time):
    return dtplot.update_traces(selectedpoints=time, selector=dict(type='bar'),
                                selected=dict(marker=dict(color='white')))


@app.callback(
    Output('time-plot', 'figure'),
    [Input('date-pick', 'date'), Input('time-pick', 'value')])
def make_plot(date, time):
    temp_day = datetime.date.fromisoformat(date)
    return make_timeplot(UberData, temp_day, time)


@app.callback(Output('map-fig', 'figure'),
              [Input('date-pick', 'date')])
def make_map(date):
    return map_func(UberData, date)


# -------------------------- MAIN ---------------------------- #

# This is the code that gets run when we call this file from the terminal
# The port number can be changed to fit your particular needs
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
