import dash_bootstrap_components as dbc
import dash 
from dash import html, Output, Input, State, callback, dcc

dash.register_page(__name__,path='/')

layout = html.Div(children=[
    html.Div(className="background", children=[
        html.Div(className="home-page", children=[
            html.Div(className="title-buttons", children=[
                html.H2(className="home-title", children="Autodiagnóstico: Dependencias e impactos sobre el agua como servicio ecosistémico"),
                html.Div(className="home-buttons", children=[
                    html.Button(id="btn-comenzar", children="Comenzar"),
                    dcc.Location(id='url', refresh=True),
                ])
            ]),
            html.Img(className="home-image", src="assets/imagenes/home-image.jpg")
        ])
    ])
])

# Callback para ir a la dirección URL /arbol-decision
@callback(
    Output('url', 'pathname'),
    [Input('btn-comenzar', 'n_clicks')]
)
def change_layout(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        return '/indicadores'
        # return '/cuestionario'
    else:
        raise dash.exceptions.PreventUpdate
    