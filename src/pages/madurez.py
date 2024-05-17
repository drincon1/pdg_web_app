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

mongo = MongoDB()


dash.register_page(__name__)

""" ---------------- ATRIBUTOS ---------------- """
df_dimensiones = pd.DataFrame()

# Niveles y sus respectivos minimos y máximos para determinar el nivel
niveles:dict = {
    'Comenzando el camino': {'puntaje_min': 0, 'puntaje_max': 30},
    'Sorteando desafios del camino': {'puntaje_min':31 , 'puntaje_max': 50},
    'Avanzando por el camino': {'puntaje_min':51, 'puntaje_max':75},
    'Liderando el camino': {'puntaje_min': 76, 'puntaje_max': 100}
}
nivel = ""

puntos_total = 0


""" ----------------------------------------- """

""" ---------------- MÉTODOS ---------------- """
def definir_nivel():
    global df_dimensiones, niveles, nivel, puntos_total
    puntos_dimension = mongo.get_puntos_por_dimension()
    df_dimensiones = mongo.get_dimensiones()

    df_dimensiones['puntos_usuario'] = pd.Series(puntos_dimension)

    df_dimensiones['porcentaje_usuario'] = (df_dimensiones['puntos_usuario'] / df_dimensiones['total_dim']) * 100

    df_dimensiones['pesos_usuario'] = df_dimensiones['porcentaje_usuario'] * df_dimensiones['peso_expertos']

    puntos_total = df_dimensiones['pesos_usuario'].sum()

    for level, level_details in niveles.items():
        puntaje_min = level_details["puntaje_min"]
        puntaje_max = level_details["puntaje_max"]

        if puntaje_min <= puntos_total <= puntaje_max:
            nivel = level

""" ------------------------------------------- """

""" ---------------- CALLBACKS ---------------- """
@callback(
    [Output('title_madurez','children'),
     Output('card_nivel_madurez','children'),
     Output('card_puntaje_obtenido','children'),
     Output('card_mejor_dimension','children'),
     Output('dropdown-dimensiones','value'),
     Output('bar-graph-dimensiones','figure'),],
    Input('title_madurez','children')
)
def get_puntos_por_dimension(children):
    global df_dimensiones, niveles, nivel, puntos_total
    definir_nivel()

    # Dimension con mejor porcentaje de puntos
    porcentaje_max = df_dimensiones['porcentaje_usuario'].max()
    dimension_max = df_dimensiones[df_dimensiones['porcentaje_usuario'] == porcentaje_max].index[0]
    
    # Bar Graph: % Puntos obtenidos vs Dimensión
    figure = px.bar(df_dimensiones, x=df_dimensiones.index, y='porcentaje_usuario', title='Porcentaje de puntos obtenidos por dimensión')
    figure.update_xaxes(title_text='Dimensión')
    figure.update_yaxes(title_text='% Puntos obtenidos')

    # Titulo madurez
    titulo = "Autodiagnóstico empresarial sobre el uso del agua - Resultados"
    if os.getenv("USERNAME") is not None:
        titulo = titulo + ": " + os.getenv("USERNAME")

    return [titulo],[nivel], [round(puntos_total,2)], [dimension_max],dimension_max,figure


@callback(
    [Output('card-puntaje-dimension','children'),
     Output('card-porcentaje-dimension','children'),
     Output('definicion-dimension','children'),
     Output('placeholder-nombre-dimension','children')],
    Input('dropdown-dimensiones','value')
)
def get_info_dimension_seleccionada(dimension):
    global df_dimensiones
    
    puntos_dimension = df_dimensiones.loc[dimension, 'puntos_usuario']
    porcentage_dimension = df_dimensiones.loc[dimension, 'porcentaje_usuario']
    definicion = df_dimensiones.loc[dimension, 'definicion']


    return [round(puntos_dimension,2)],[f"{round(porcentage_dimension,2)}%"], [definicion], [dimension]
""" -------------------------------------------- """

""" ---------------- COMPONENTS ---------------- """


""" ---------------------------------------- """


""" ---------------- LAYOUT ---------------- """
layout = dbc.Container([
    # Título 
    dbc.Row([
        dbc.Col([
            html.Div(
                id="banner",
                className="banner",
                children=[
                    html.Img(className="water-image", src="assets/imagenes/water-drop.png"),
                    html.H3(f"Autodiagnóstico empresarial sobre el uso del agua - Resultados",id="title_madurez"),
                ],
            ),
            # html.H1("Nivel de madurez", id="title_madurez" ,style={'textAlign': 'center'}),
            html.Br(),
            html.Hr()
        ], width=12)
    ]),
    # Nivel de Madurez
    dbc.Row([
        # Nivel de madurez
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4(id="card_nivel_madurez"),
                        html.P("Nivel de madurez")
                    ]
                ), className="text-center m-4", color="primary"
            ),
        ], width=4),

        # Puntaje obtenido
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4(id="card_puntaje_obtenido"),
                        html.P("Puntaje obtenido")
                    ]
                ), className="text-center m-4", color="info"
            )
        ], width=4),

        # Mejor dimensión
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4(id="card_mejor_dimension"),
                        html.P("Mejor dimensión")
                    ]
                ), className="text-center m-4", color="success"
            )
        ], width=4)
    ]), 
    # Bar Graph: Porcentaje de puntos por dimensión
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='bar-graph-dimensiones',
                figure={},
            ),
        ])
    ]),
    # Dropdown: Seleccionar dimensión
    dbc.Row([
        # Seleccionar la dimension que quiera ver los datos y su definición
        dbc.Col([
            html.Hr(),
            html.H2("Información por dimensión", className="text-center"),
            html.Label("Escoja la dimensión que quiera analizar"),
            dcc.Dropdown(id="dropdown-dimensiones",options=['Contexto de la organización','Liderazgo','Planificación','Soporte','Operación','Evaluación del desempeño','Mejora'])
        ], width=12),
        dbc.Col([
            dbc.Card(
                [
                    dbc.CardHeader(html.H6(id="placeholder-nombre-dimension", className="card-title",style={'color': 'black', 'margin-top':'5px'}),),
                    dbc.CardBody(
                        [
                            html.P(
                                id="definicion-dimension",
                                className="card-text",
                                style={'color': 'black'}
                            ),
                        ]
                    )
                ], className="text-center m-4", color="dark", outline=True
            ),
        ], width=12),
    ]),
    # Mostrar puntos y porcentaje por dimensión seleccionada
    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4(id="card-puntaje-dimension"),
                        html.P("Puntaje obtenido")
                    ]
                ), className="text-center m-4", color="primary"
            ),
        ],width=5),
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4(id="card-porcentaje-dimension"),
                        html.P("Porcentaje de puntos obtenidos")
                    ]
                ), className="text-center m-4", color="info"
            )
        ],width=5)
    ], justify="evenly")
],fluid=True)
""" ----------------------------------------- """