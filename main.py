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

# Getting Data
UberData = pd.read_csv('uber-trip-data/uber-raw-data-apr14.csv')
UberData["Date/Time"] = pd.to_datetime(UberData["Date/Time"])

# Dictionary of base lookups provided in the data
base_lookup = dict(
    [('B02512', 'Unter'), ('B02598', 'Hinter'), ('B02617', 'Weiter'), ('B02682', 'Schmecken'), ('B02764', 'Danach-NY'),
     ('B02835', 'Dreist'), ('B02836', 'Drinnen')])

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
            'the histogram.'),

        html.Div([
            dcc.DatePickerSingle(date=datetime.date.fromisoformat("2014-04-01"), id='date-pick')
        ], style=dict([('padding', '15px')])),

        html.Div([
            dcc.Dropdown(id='time-pick', options=[dict(label=str(i) + ":00", value=i) for i in range(0, 24)],
                         placeholder="Select Certain Hours",
                         multi=True,
                         style=dict([('color', 'black')]))
        ], style=dict([('padding', '15px')])),

        html.Tbody('', id='test-out',
                   style=dict([('padding-left', '30px')])),

    ], style=dict([('padding', '30px')])),

    html.Div([
        html.Div([
            dcc.Graph(id='map-fig'),
            dcc.Graph(id='base-plot')
        ], style=dict([('display', 'flex'), ('flex-direction', 'row')])),

        html.Tbody(children="Select any of the bars on the histogram to section data by time.",
                   style=dict([('background-color', '#2F2F2E')])),

        dcc.Graph(id='time-plot')
    ], style=dict(
        [('responsive', True), ("background-color", "dimgray"), ('display', 'flex'), ('flex-direction', 'column')])),

],
    style=dict([('responsive', True), ('display', 'flex'), ('flex-direction', 'row'), ("background-color", "#2F2F2E"),
                ("color", 'white'), ('padding', '0px')]))


#####################
#  Make Plot  #
#####################

def map_func(date, selected_times):
    dt_lst = []

    # Fixes the base case for when time is passed in as NoneType
    if selected_times is None:
        selected_times = [0]

    # Creates the Date/Time String for each hour on a particular day
    for timeVal in selected_times:
        if timeVal < 10:
            dtStr = date + " 00:0" + str(timeVal) + ":00"
        else:
            dtStr = date + " 00:" + str(timeVal) + ":00"
        dt_lst.append(dtStr)  # Limits Dataframe to those particular hours on that particular day

    df = UberData[UberData['Date/Time'].isin(dt_lst)]

    # Accessing Mapbox Library/Creating Figure
    px.set_mapbox_access_token(open("mapbox_token.txt").read())

    fig = px.scatter_mapbox(df,
                            lat="Lat",
                            lon="Lon",
                            color="Date/Time",
                            color_continuous_scale=px.colors.cyclical.IceFire,
                            size_max=15,
                            zoom=10)

    fig.update_layout(title="Map Output",
                      margin=dict(t=27, l=2, r=2, b=27),
                      font=dict(color='white'),
                      width=600,
                      height=400,
                      autosize=True,
                      paper_bgcolor='#2F2F2E',
                      plot_bgcolor='#2F2F2E'
                      )
    return fig


def make_timeplot(data, date, selected_times):
    day = pd.Grouper(key="Date/Time", freq="D")  # groupers to get data for days/hours
    hour = pd.Grouper(key="Date/Time", freq="60min")

    grouped = data.groupby(day).get_group(date).groupby(hour)

    y = [group[1]["Date/Time"].count() for group in grouped]  # count num of rides in each hour
    x = [group[0].hour for group in grouped]  # index hours

    ######## Make Figure #################
    dtplot = go.Figure()

    bar_marker = go.bar.Marker(color=x,
                               colorscale='viridis_r')

    bar_plot = go.Bar(x=[str(i) + ":00" for i in x],  # create bar graph
                      y=y,
                      marker=bar_marker)

    dtplot.add_trace(bar_plot)  # add to trace

    # layout/appearance
    dtplot.update_layout(bargap=0,
                         margin=dict(t=27, l=2, r=2, b=27),
                         font=dict(color='white'),
                         paper_bgcolor='dimgray',
                         plot_bgcolor='dimgray',
                         width=1200,
                         height=400,
                         autosize=True)

    dtplot.update_traces(text=[str(i) for i in y],
                         textposition='outside',
                         hoverinfo='x',
                         selectedpoints=selected_times,
                         selector=dict(type='bar'),
                         selected=dict(marker=dict(color='white')))

    dtplot.update_yaxes(showticklabels=False,
                        showgrid=False,
                        fixedrange=True)

    dtplot.update_xaxes(showgrid=False,
                        fixedrange=True)

    return dtplot


def make_baseplot(temp_day):
    day = pd.Grouper(key="Date/Time", freq="D")  # group by day/base
    base = pd.Grouper(key="Base")

    grouped = UberData.groupby(day).get_group(temp_day).groupby(base)

    y = [group[1].count()[1] for group in grouped]  # count number in each group
    x = [base_lookup[i] for i in UberData["Base"].unique()]  # find name of unique bases using dictionary

    ######## Make Figure #################
    bplot = go.Figure()

    bplot.add_trace(go.Bar(x=x, y=y, marker=go.bar.Marker(color=[i for i in range(0, len(x))],
                                                          colorscale='viridis_r')))  # make bar chart/add trace

    # layout/appearance
    bplot.update_layout(bargap=0,
                        margin=dict(t=27, l=2, r=2, b=27),
                        font=dict(color='white'),
                        paper_bgcolor='dimgray',
                        plot_bgcolor='dimgray',
                        width=600,
                        height=400,
                        autosize=True)

    bplot.update_traces(text=[str(i) for i in y],
                        textposition='outside',
                        hoverinfo='x')

    bplot.update_yaxes(showticklabels=False,
                       showgrid=False,
                       fixedrange=True)
    bplot.update_xaxes(showgrid=False,
                       fixedrange=True)

    return bplot


@app.callback(Output('base-plot', 'figure'),
              [Input('date-pick', 'date')])
def make_bplot(date):
    temp_day = datetime.date.fromisoformat(date)
    return make_baseplot(temp_day)


@app.callback(
    Output('time-plot', 'figure'),
    [Input('date-pick', 'date'), Input('time-pick', 'value')])
def make_tplot(date, picked_time):
    temp_day = datetime.date.fromisoformat(date)
    return make_timeplot(UberData, temp_day, picked_time)


@app.callback(Output('map-fig', 'figure'),
              [Input('date-pick', 'date'), Input('time-pick', 'value')])
def make_map(date, picked_time):
    return map_func(date, picked_time)


# -------------------------- MAIN ---------------------------- #

# This is the code that gets run when we call this file from the terminal
# The port number can be changed to fit your particular needs
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
