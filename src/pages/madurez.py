import sys
sys.path.append("..")
import dash
from dash import html, callback, Input, State, Output, dcc, ALL
from dash.exceptions import PreventUpdate
from connection import MongoDB
import json
import dash_bootstrap_components as dbc

mongo = MongoDB()


dash.register_page(__name__)

""" ---------------- ATRIBUTOS ---------------- """
# Puntos por dimension del usuario
puntos_dimension:dict = {}

# Dimensiones que se evaluan del usuario
dimensiones:dict = {
    'Contexto de la organización': {'total':25, 'peso': 0.0838},
    'Liderazgo': {'total':13, 'peso': 0.0844},
    'Planificación':{'total':31, 'peso': 0.1812},
    'Soporte': {'total':22, 'peso': 0.1732},
    'Operación': {'total':7, 'peso': 0.0822},
    'Evaluación del desempeño': {'total':28, 'peso': 0.3737},
    'Mejora': {'total':5, 'peso': 0.0215}
}

# Niveles y sus respectivos minimos y máximos para determinar el nivel
niveles:dict = {
    'Comenzando el camino': {'puntaje_min': 0, 'puntaje_max': 30},
    'Sorteando desafios del camino': {'puntaje_min':31 , 'puntaje_max': 50},
    'Avanzando por el camino': {'puntaje_min':51, 'puntaje_max':75},
    'Liderando el camino': {'puntaje_min': 76, 'puntaje_max': 100}
}

porcentajes : list = []
pesos: list = []
puntos_total = 0
nivel = ""

""" ----------------------------------------- """

""" ---------------- MÉTODOS ---------------- """
def definir_nivel():
    global puntos_dimension, dimensiones, niveles, porcentajes, pesos, puntos_total, nivel
    puntos_dimension = mongo.get_puntos_por_dimension()
    
    for dimen in puntos_dimension:
        puntos = puntos_dimension[dimen]
        total = dimensiones[dimen]['total']
        peso = dimensiones[dimen]['peso']
        porcentaje = (puntos/total)*100
        porcentajes.append(porcentaje)
        puntos_ponderados = peso * porcentaje
        pesos.append(puntos_ponderados)
        puntos_total = puntos_total + puntos_ponderados

    for level, level_details in niveles.items():
        puntaje_min = level_details["puntaje_min"]
        puntaje_max = level_details["puntaje_max"]

        if puntaje_min <= puntos_total <= puntaje_max:
            nivel = level


    # print('porcentajes', porcentajes, '\npesos', pesos, '\npuntos_total', puntos_total, '\nnivel', nivel)

def Header(name):
    title = html.H2(name, style={"margin-top": 5})

    return dbc.Row([dbc.Col(title, md=9)])

""" ------------------------------------------- """

""" ---------------- CALLBACKS ---------------- """
# @callback(
#     Output('nivel_madurez','children'),
#     Input('nivel_madurez','children')
# )
# def get_puntos_por_dimension(children):
    
#     definir_nivel()


""" -------------------------------------------- """

""" ---------------- COMPONENTS ---------------- """
def cmp_cards() -> list:
    global puntos_total, nivel
    cards = [
        dbc.Card(
            [
                html.H2(nivel, className="card-title"),
                html.P("Nivel de madurez", className="card-text"),
            ],
            body=True,
            color="light",
        ),
        dbc.Card(
            [
                html.H2(round(puntos_total,2), className="card-title"),
                html.P("Puntos obtendios", className="card-text"),
            ],
            body=True,
            color="dark",
            inverse=True,
        ),
        dbc.Card(
            [
                html.H2(round(puntos_total/131*100,2), className="card-title"),
                html.P("Porcentaje de puntos obtenidos", className="card-text"),
            ],
            body=True,
            color="primary",
            inverse=True,
        ),
    ]

    return cards

""" ---------------------------------------- """

""" ---------------- LAYOUT ---------------- """

definir_nivel()

layout = html.Div(className="madurez-background", id='nivel_madurez', children=[
    dbc.Container(
        [
            Header("Nivel de madurez"),
            dbc.Row([dbc.Col(card) for card in cmp_cards()]),
        ]
    )
])
""" ----------------------------------------- """