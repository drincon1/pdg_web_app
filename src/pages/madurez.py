import sys
sys.path.append("..")
import dash
from dash import html, callback, Input, State, Output, dcc, ALL
from dash.exceptions import PreventUpdate
from connection import MongoDB
import json
import dash_bootstrap_components as dbc

dash.register_page(__name__)


""" ---------- LAYOUT ---------- """
layout = html.Div(className="madurez-background", children=[
    dbc.Container(
        [
            dbc.Card(
            [
                html.H2("Nivel de madurez", className="card-title"),
                #html.P("Model Training Accuracy", className="card-text"),
            ],
            class_name="card_nivel_madurez",
            body=True,
            color="light",
        ),
        ]
    )
])


