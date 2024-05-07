import dash
from dash import Dash, html, dcc

app = Dash(__name__)

server = app.server

app.layout = html.Div([
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
])