import dash
from dash import html, callback, Input, State, Output, dcc

dash.register_page(__name__)

layout = html.Div([
    html.H1("Cuestionario")
])