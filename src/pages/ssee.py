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
import os

""" ---------- ATRIBUTOS ---------- """
mongo = MongoDB()

ssee: dict = {}
"""
    ssee: {
        numero: { # numero del servicio ecosistemico j asociado al indicador i
            nombre: '', # nombre del servicio ecosistemico j asociado al indicador i
            dependencia:'', # [BAJA, MEDIA, ALTA]
            impacto: '', # [POSITIVO, NEGATIVO]
        }, 
    }
"""


""" ---------- METODOS ---------- """
dash.register_page(__name__)


def get_ssee():
    global ssee
    ssee = mongo.get_ssee_usuario()

def display_ssee(num_ssee: str):


    layout = html.Div([
        dbc.Card([
            dbc.CardHeader('Descripción del SSEE'),
            dbc.CardBody([
                html.H5('NOMBRE DEL SSEE'),
                html.P('DESCRIPCION DEL SSEE'),
            ])
        ], color="light", style={"color":"black"}),

        html.P(style={"margin-top":"10px"},children="¿Cuál es el nivel de dependencia de su empresa sobre este servicio ecosistémico?"),
        dcc.RadioItems(
                id={"type": "opc-ssee-dependencia", "index":1},
                options=['BAJO','MEDIO','ALTO','NS/NR'],
        ),
        html.P(style={"margin-top":"10px"},children="¿Qué tipo de impacto tiene su empresa sobre este servicio ecosistémico?"),
        dcc.RadioItems(
                id={"type": "opc-ssee-impacto", "index":1},
                options=['POSITIVO','NEGATIVO','NS/NR'],
        )
    ])

    return layout

""" ---------- CALLBACKS ---------- """
@callback(
    Output('seccion-ssee','children'),
    Input('seccion-ssee','children')
)
def display_primer_ssee(children):
    get_ssee()
    return display_ssee(num_ssee='1')
    

# CALLBACK: ACTUALIZAR PREGUNTA
@callback(
    [Output('seccion-ssee', 'children', allow_duplicate=True),
     Output('btn-siguiente-ssee','disabled',allow_duplicate=True),
     Output('btn-terminar-ssee','disabled',allow_duplicate=True),
     Output('btn-atras-ssee','disabled',allow_duplicate=True),],
    State('avance-ssee', 'max'),
    Input('avance-ssee', 'value'),
    prevent_initial_call=True
)
def actualizar_ssee(max_indicador, numero_pregunta):
    if numero_pregunta == max_indicador:
        return display_ssee(str(numero_pregunta)), True, False, False
    if numero_pregunta == 1:
        return display_ssee(str(numero_pregunta)), False, True, True
    
    return display_ssee(str(numero_pregunta)), False, True, False

# CALLBACK: SIGUIENTE PREGUNTA
@callback(
    [Output('seccion-ssee','children',allow_duplicate=True),
     Output('avance-ssee','value',allow_duplicate=True),
     Output('btn-siguiente-ssee','disabled',allow_duplicate=True),
     Output('btn-terminar-ssee','disabled',allow_duplicate=True)],
    [State('avance-ssee', 'max'),
     State('avance-ssee','value')],
    Input('btn-siguiente-ssee','n_clicks'),
    prevent_initial_call=True
)
def siguiente_ssee(max_indicador,num_pregunta,n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    if num_pregunta == max_indicador:
         return display_ssee(str(num_pregunta+1)), num_pregunta+1, True, False
    return display_ssee(str(num_pregunta+1)), num_pregunta+1,False, True


# CALLBACK: ANTERIOR_PREGUNTA
@callback(
    [Output('seccion-ssee','children',allow_duplicate=True),
     Output('avance-ssee','value',allow_duplicate=True),],
    State('avance-ssee','value'),
    Input('btn-atras-ssee','n_clicks'),
    prevent_initial_call=True
)
def anterior_ssee(num_pregunta,n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    return display_ssee(str(num_pregunta-1)),num_pregunta-1    

@callback(
        [Output('alerta-ssee-guardados','children'),
        Output('alerta-ssee-guardados','is_open'),
        Output('alerta-ssee-guardados','duration')],
        Input('btn-guardar-ssee','n_clicks'),
        prevent_initial_call = True
)
def guardar_ssee(n_clicks):
    return ('Respuestas guardadas con éxito!'), True, 2000


@callback(
    Output('url_relaciones_ssee', 'pathname'),
    Input('btn-terminar-ssee', 'n_clicks'),
    prevent_initial_call=True
)
def go_ssee(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate    

    return '/funciones'


""" ---------- LAYOUT ---------- """
layout = html.Div(children=[
    html.Div(className="background", id='background', children=[
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.Img(className="water-image", src="assets/imagenes/water-drop.png"),
                html.H3("Autodiagnóstico empresarial sobre el uso del agua - Servicios Ecosistémicos relacionados a los indicadores"),
            ],
        ),
        html.Div(className="seccion-cuestionario", children=[
            html.Div(className='seccion-progreso',children=[
                # Número de servicios ecosistémicos relacionados
                dcc.Slider(id='avance-ssee',min=1, max=30, step=1, value=1, className="slider"),
                html.Hr()
            ]),
            html.Div(className='seccion-botones', children=[
                html.Button("Atrás",id='btn-atras-ssee', className='btn-cuestionario', disabled=True),
                html.Button("Guardar respuestas",id='btn-guardar-ssee', className='btn-cuestionario'),
                html.Button("Siguiente",id='btn-siguiente-ssee', className='btn-cuestionario'),
            ]),
            html.Div(className="seccion-preguntas-respuestas", children=[
                # Sección SSEE + Pregunta 
                html.Div(className='seccion-preguntas',id='seccion-ssee'),
            ]),
            html.Div(className='seccion-terminar', children=[
                html.Button("Terminar",id='btn-terminar-ssee', disabled=True, className='btn-cuestionario'),
                dcc.Location(id='url_relaciones_ssee', refresh=True),
                dbc.Alert(id="alerta-ssee-guardados", is_open=False, style={'margin-top': '10px'})
            ]),
        ])
    ])
])
