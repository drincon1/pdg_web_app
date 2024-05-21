import sys
sys.path.append("..")
import dash
from dash import html, callback, Input, State, Output, dcc, ALL
from dash.exceptions import PreventUpdate
from connection import MongoDB
from components import referencias
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

@callback(
    Output("modal-referencias", "is_open"),
    Input("btn-referencias", "n_clicks"),
    State("modal-referencias", "is_open"),
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open


""" -------------------------------------------- """

""" ---------------- COMPONENTS ---------------- """

model_referencias = html.Div(dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Referencias")),
        dbc.ModalBody([
            html.Div("A continuación podrá encontrar la lista de referencias que fueron utilizadas para crear esta herramientas. Estas referencias incluyen la creación del modelo de madurez, preguntas y la selección de dimensiones,servicios ecosistémicos y funciones ecosistémicas"),
            html.Div(referencias.markdown_referencias)
        ]),
    ],
    id="modal-referencias",
    size="xl",
    is_open=False,
),)

""" ------------------------------------------- """


""" ---------------- MARKDOWND ---------------- """

markdown = '''
    ### Introducción
    A través de una serie de preguntas, se buscará determinar el nivel de madurez de la empresa con respecto a las dependencias e impactos que tiene sobre el agua.
    El nivel de madurez estará determinado por siete dimensiones diferentes (Contexto de la organización, Liderazgo, Planificación, Soporte, Operación, Evaluación del desempeño, Mejora).
    Cada una de estas dimensiones tendrá un número de puntos que se podrán obtener respondiendo las preguntas. Luego, ponderando las dimensiones por su importancia dada por expertos,
    se obtendrá el total de puntos y así su nivel de madurez ((1) Comenzando el camino, (2) Sorteando desafíos del camino, (3) Avanzando por el camino, y (4) Liderando el camino)
    
    Adicionalmente, se podrá determinar cuales indicadores la empresa está midiendo o contemplando y cuales debería medir/contemplar. De esta manera, se podrá relacionar con servicios ecosistémicos
    en específico. Posteriormente, se relacionará estos servicios ecosistémicos con sus funciones ecosistémicas, permitiendo así relacionar el negocio con el agua y sus componentes. 

    ### Objetivos
    1. Determinar el nivel de madurez a partir de la evaluación de el conocimiento y acciones que tiene la empresa acerca de las dependencias y los impactos sobre el agua.
    2. Entender, de las dimensiones a evaluar, cuál es la mejor dimensión actualmente que tiene la empresa.
    3. Exponer a la empresa, según los indicadores que ellos miden, cuáles servicios ecosistémicos y funciones ecosistémicas deberían contemplar en los reportes relacionados al agua.

    ### Funcionamiento
    Esta herramienta se dividen en 6 pasos.

    1. Cuestionario: En este paso la empresa deberá responder un conjunto de preguntas relacionadas a los conocimientos y acciones que actualmente está haciendo en relación a las dependencias e impactos sobre el agua.
    2. Indicadores: La empresa deberá seleccionar los indicadores que actualmente estén midiendo o contemplando en reportes relacionados al agua.
    3. Nuevos indicadores: La empresa podrá ingresar sus propios indicadores, que no encontró en la anterior sección, a la herramienta.
    4. Servicios Ecosistémicos: La empresa, a partir de los indicadores seleccionados de la herramienta, podrá determinar el nivel de dependencia y el tipo de impacto que tiene sobre los servicios ecosistémicos.
    5. Funciones Ecosistémicas: La empresa podrá ver una visualización de la relación entre indicadores, servicios ecosistémicos y funciones ecosistémicas, para entender la importancia en la relación entre el negocio y el agua y sus servicios ecosistémicos.
    6. Resultados: En este último paso, la empresa podrá saber cuál es su nivel de madurez, su puntaje obtenido, su mejor dimensión, el puntaje y descripción por dimensión y unas gráficas descriptivas para los indicadores escogidos.

    #### Importante
    Asegúrese de siempre iniciar sesion antes de usar cualquier funcionalidad
    
'''

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
                    html.H3("Autodiagnóstico empresarial sobre el uso del agua"),
                ],
            ),
            # html.H1("Autodiagnóstico empresarial sobre el uso del agua",style={'textAlign': 'center'}),
            # html.Hr()
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H3("Explicación",className="text-center",),
                dcc.Markdown(markdown, style={'padding-left': '10px'})
            ], style={'border':'1px solid black',  'border-style': 'dotted', 'border-radius': '5px'})
        ], width=12)
    ],align="center",),
    dbc.Row([
        dbc.Col([
            model_referencias,
            dbc.Button("Referencias", id='btn-referencias', color="light", style={'margin-top':'10px', 'margin-right': '50px'}),
            dbc.Button("Continuar",id='btn-continuar',className="primary",style={'margin-top':'10px'}),
            dcc.Location(id='url-cuestionario', refresh=True),
        ], className="d-flex justify-content-end", width=12)
    ])

],fluid=True)
""" ----------------------------------------- """