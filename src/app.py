import dash
from dash import Dash, html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

app = Dash(__name__,pages_folder="pages",use_pages=True,suppress_callback_exceptions=True)
server = app.server


app.layout = html.Div(children=[
	dash.page_container,
])

if __name__ == '__main__':
    app.run_server(debug=True)
