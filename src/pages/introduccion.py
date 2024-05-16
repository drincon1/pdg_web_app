import sys
sys.path.append("..")
import dash
from dash import html, callback, Input, State, Output, dcc, ALL
from dash.exceptions import PreventUpdate
from connection import MongoDB
import json
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import os


dash.register_page(__name__)
""" ---------------- CALLBACKS ---------------- """
@callback(
    Output('url-cuestionario', 'pathname'),
    Input('btn-continuar', 'n_clicks'),
    prevent_initial_call=True
)
def iniciar_sesion(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    return '/cuestionario'

""" ------------------------------------------- """

""" ---------------- LAYOUT ---------------- """
layout = dbc.Container([
    # Título 
    dbc.Row([
        dbc.Col([
            html.H1("Autodiagnóstico empresarial sobre el uso del agua",style={'textAlign': 'center'}),
            html.Hr()
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H3("Explicación",className="text-center",),
                dcc.Markdown('''
                #### Dash and Markdown

                Dash supports [Markdown](http://commonmark.org/help).

                Markdown is a simple way to write and format text.
                It includes a syntax for things like **bold text** and *italics*,
                [links](http://commonmark.org/help), inline `code` snippets, lists,
                quotes, and more.
                ''', style={'padding-left': '10px'})
            ], style={'border':'1px solid black', 'height':'500px', 'border-style': 'dotted', 'border-radius': '5px'})
        ], width=12)
    ],align="center",),
    dbc.Row([
        dbc.Col([
            dbc.Button("Continuar",id='btn-continuar',className="primary",style={'margin-top':'10px'}),
            dcc.Location(id='url-cuestionario', refresh=True),
        ], className="d-flex justify-content-end")
    ])

])
""" ----------------------------------------- """