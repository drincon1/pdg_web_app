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
    [Output('dropdown-indicadors','options'),
     Output('alert-indicadores', 'is_open'),
     Output('alert-indicadores', 'children'),
     Output('alert-indicadores', 'color'),
     Output('alert-gestiones', 'is_open'),
     Output('alert-gestiones', 'children'),],
    Input('switches-indicadores-seleccionados','value')
)
def get_indicadores(switch):
    global df_indicadores
    if switch is not None and len(switch) > 0:
        df_indicadores = mongo.get_indicadores_seleccionados_sankey()
    
        if df_indicadores.empty:
            df_indicadores = mongo.get_indicadores_sankey()
            mensaje = 'Debe iniciar sesión para poder utilizar su información'
            return df_indicadores['indicador'].unique(), True, mensaje, 'danger', True, mensaje
    else:
        df_indicadores = mongo.get_indicadores_sankey()


    return df_indicadores['indicador'].unique(), False, '', '', False, ''



@callback(
    [Output('sankey-diagram','figure'),
     Output('alert-indicadores', 'is_open',allow_duplicate=True),
     Output('alert-indicadores', 'children',allow_duplicate=True),
     Output('dropdown-funciones','options'),
     Output('alert-funciones', 'is_open'),
     Output('alert-funciones', 'children'),],
    Input('dropdown-indicadors','value'),
    prevent_initial_call=True
)
def get_indicadores(indicadores_sele):
    global df_indicadores
    
    if indicadores_sele is None: # or len(indicadores_sele) == 0:
        mensaje = 'No hay indicadores selecionados. Por favor seleccione por lo menos un indicador'
        return {}, True, mensaje, [], True, mensaje
    
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

    node_titles = ['Title A', 'Title B', 'Title C']

    fig = go.Figure(data=[go.Sankey(
            node= dict(
                pad = 15,
                thickness = 20,
                # line = dict(color='black'),
                label = unique_source_target
            ),
            link=dict(
                source=links_dict['source'],
                target=links_dict['target'],
                value=links_dict['value'],
            )
        )]
    )

    fig.update_layout(title_text = 'Relación: Indicadores - Servicios Ecosistémicos - Funciones Ecosistémicas')

    return fig, False, '', df_sankey['funcion'].unique(), False, '',


@callback(
    Output('div-card-funcion','children'),
    State('dropdown-indicadors','value'),
    Input('dropdown-funciones','value')
)
def set_card_funcion(indicadores_sele,funcion):
    if funcion is None:
        raise dash.exceptions.PreventUpdate
    
    global df_indicadores

    indicadores_seleccionados = df_indicadores['indicador'].isin(indicadores_sele)
    df_sankey = df_indicadores[indicadores_seleccionados]

    proceso_ecologico = df_sankey[df_sankey['funcion'] == funcion]['proceso_ecologico'].unique()[0].split('-')
    indicadores = df_sankey[df_sankey['funcion'] == funcion]['indicador'].unique()

    markdown_procesos = ""
    for prc in proceso_ecologico:
        markdown_procesos = f'* {prc}\n' + markdown_procesos

    markdown_text = ""
    for indc in indicadores:
        markdown_text = f'* {indc}\n' + markdown_text

    dcc.Markdown()
    return dbc.Card([
        dbc.CardHeader('Procesos ecológicos e Indicadores asociados ', style={'color':'black'}),
        dbc.CardBody([
            html.H5('Procesos ecologicos'),
            dcc.Markdown(markdown_procesos),
            html.Hr(),
            html.H5('Indicadores'),
            dcc.Markdown(markdown_text),
            # html.P([f'- {indc}' for indc in indicadores])
        ], style={'color':'black'})
    ])


@callback(
    Output('div-card-gestion','children'),
    [Input('div-card-gestion','children'),
     Input('switches-indicadores-seleccionados','value')]
)
def set_card_gestiones(funcion, switch):
    gestiones: list = []

    if switch is not None and len(switch) > 0:
        gestiones = mongo.get_gestion_ecosistemicas_usuario()
    else:
        gestiones = mongo.get_gestion_ecosistemicas()

    if gestiones is None or len(gestiones) == 0:
        raise dash.exceptions.PreventUpdate

    markdown_text = ""
    for gst in gestiones:
        markdown_text = f'* {gst}\n' + markdown_text

    dcc.Markdown()
    return dbc.Card([
        dbc.CardHeader('Indicadores asociados a la gestión ecosistémica', style={'color':'black'}),
        dbc.CardBody([
            html.H5('Indicadores'),
            dcc.Markdown(markdown_text),
            html.Hr(),
            html.H5('¿Qué es una gestión ecosistémica?'),
            html.P('Definición de gestión ecosistémica'),
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
                options=[{'label':html.P('Indicadores seleccionados',id='target-indicadores'), 'value': 'Indicadores seleccionados'}],
                id="switches-indicadores-seleccionados",
                switch=True,
            ),
            dbc.Tooltip("Solo aparecen los indicadores que escogió en la sección 'Indicadores'",target="target-indicadores",),
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
            dbc.Alert(color="warning", id='alert-funciones', is_open=False),
            dcc.Dropdown(id="dropdown-funciones", style={'margin-bottom':'30px'}),
            html.Div(id='div-card-funcion')
        ], width=5),
        dbc.Col([
            html.H3('Gestiones ecosistémicas'),
            dbc.Alert(color="danger", id='alert-gestiones', is_open=False),
            html.Div(id='div-card-gestion')
        ], width=5)
    ],justify="center"),
    dbc.Row([
        html.Div(className='seccion-terminar', children=[
                html.Button("Nivel de madurez",id='btn-madurez', className='btn-cuestionario'),
                dcc.Location(id='url_madurez', refresh=True),
        ]),
    ]),
], fluid=True)