""" ---------- LIBRERIAS ---------- """
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
import plotly.graph_objects as go
import os

""" ---------- ATRIBUTOS ---------- """
mongo = MongoDB()

df_indicadores: pd.DataFrame = pd.DataFrame()

""" ---------- METODOS ---------- """
dash.register_page(__name__)

""" ---------- CALLBACKS ---------- """

@callback(
    Output('dropdown-indicadors','options'),
    Input('switches-indicadores-seleccionados','value'),
)
def get_indicadores(switch):
    global df_indicadores
    if switch is not None and len(switch) > 0:
        df_indicadores = mongo.get_indicadores_seleccionados_sankey()
    else:
        df_indicadores = mongo.get_indicadores_sankey()

    return df_indicadores['indicador'].unique()

@callback(
    [Output('sankey-diagram','figure'),
     Output('alert-indicadores', 'is_open'),
     Output('alert-indicadores', 'children'),
     Output('dropdown-funciones','options')],
    Input('dropdown-indicadors','value')
)
def get_indicadores(indicadores_sele):
    global df_indicadores
    
    if indicadores_sele is None: # or len(indicadores_sele) == 0:
        return {}, True, 'No hay indicadores selecionados. Por favor seleccione por lo menos un indicador', []
    
    

    indicadores_seleccionados = df_indicadores['indicador'].isin(indicadores_sele)
    df_sankey = df_indicadores[indicadores_seleccionados]

    df_temp1 = df_sankey.groupby(['indicador', 'servicio']).size().reset_index(name='count')
    df_temp1 = df_temp1.rename(columns={'indicador': 'source', 'servicio': 'target', 'count': 'value'})

    df_temp2 = df_sankey.groupby(['servicio', 'funcion']).size().reset_index(name='count')
    df_temp2 = df_temp2.rename(columns={'servicio': 'source', 'funcion': 'target', 'count': 'value'})

    links = pd.concat([df_temp1,df_temp2], axis=0)

    unique_source_target = list(pd.unique(links[['source','target']].values.ravel('K')))

    mapping_dict = {k: v for v, k in enumerate(unique_source_target)}

    links['source'] = links['source'].map(mapping_dict)
    links['target'] = links['target'].map(mapping_dict)

    links_dict = links.to_dict(orient='list')

    fig = go.Figure(data=[go.Sankey(
        node= dict(
            pad = 15,
            thickness = 20,
            # line = dict(color='black'),
            label = unique_source_target,
        ),
        link=dict(
            source=links_dict['source'],
            target=links_dict['target'],
            value=links_dict['value'],
        )
    )]
    )

    fig.update_layout(title_text = 'Relación: Indicadores - Servicios Ecosistémicos - Funciones Ecosistémicas')

    return fig, False, '', df_sankey['funcion'].unique()


@callback(
    Output('div-card-funcion','children'),
    Input('dropdown-funciones','value')
)
def set_card_funcion(funcion):
    if funcion is None:
        raise dash.exceptions.PreventUpdate
    
    global df_indicadores
    print(df_indicadores)

    proceso_ecologico = df_indicadores[df_indicadores['funcion'] == funcion]['proceso_ecologico'].unique()[0]
    indicadores = df_indicadores[df_indicadores['funcion'] == funcion]['indicador'].unique()

    markdown_text = ""
    for indc in indicadores:
        markdown_text = f'* {indc}\n' + markdown_text

    dcc.Markdown()
    return dbc.Card([
        dbc.CardHeader('Proceso ecológico e Indicadores asociados ', style={'color':'black'}),
        dbc.CardBody([
            html.H5('Proceso ecologico'),
            html.P(proceso_ecologico),
            html.Hr(),
            html.H5('Indicadores'),
            dcc.Markdown(markdown_text),
            # html.P([f'- {indc}' for indc in indicadores])
        ], style={'color':'black'})
    ])

@callback(
    Output('url_madurez', 'pathname'),
    Input('btn-madurez', 'n_clicks'),
    prevent_initial_call=True
)
def go_madurez(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate    
        
    return '/madurez'

""" ---------- LAYOUT ---------- """
layout = dbc.Container([
    # Título 
    dbc.Row([
        dbc.Col([
            html.Div(
                id="banner",
                className="banner",
                children=[
                    html.Img(className="water-image", src="assets/imagenes/water-drop.png"),
                    html.H3(f"Autodiagnóstico empresarial sobre el uso del agua - Relaciones", id='heading-relaciones'),
                ],
            ),
            # html.H1("Nivel de madurez", id="title_madurez" ,style={'textAlign': 'center'}),
            html.Br(),
            html.Hr()
        ], width=12)
    ]),
    # Sankey Diagram
    dbc.Row([
        dbc.Col([
            html.H3('Relación'),
            dbc.Label('Seleccione los indicadores que desea incluir en la gráfica'),
            dbc.Checklist(
                options=[{'label':"Indicadores seleccionados", 'value': True}],
                id="switches-indicadores-seleccionados",
                switch=True,
            ),
            dbc.Alert(color="warning", id='alert-indicadores', is_open=False),
            dcc.Dropdown(id="dropdown-indicadors", multi=True),
            dcc.Graph(
                id='sankey-diagram',
                figure={},
            ),
            html.Hr(),
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.H3('Funciones ecosistémicas'),
            dcc.Dropdown(id="dropdown-funciones", style={'margin-bottom':'30px'}),
            html.Div(id='div-card-funcion')
        ], width=8)
    ],justify="center"),
    dbc.Row([
        html.Div(className='seccion-terminar', children=[
                html.Button("Nivel de madurez",id='btn-madurez', className='btn-cuestionario'),
                dcc.Location(id='url_madurez', refresh=True),
        ]),
    ]),
], fluid=True)