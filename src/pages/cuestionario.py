import sys
sys.path.append("..")
import pandas as pd
import dash
from dash import html, callback, Input, State, Output, dcc, ALL
from dash.exceptions import PreventUpdate
from connection import MongoDB
import json

""" ---------------- ATRIBUTOS ---------------- """
preguntas: dict = {}
mongo = MongoDB()
# respuestas_locales será un diccionario de diccionarios
respuestas: dict = {}

""" ------------------------------------------- """

dash.register_page(__name__)

layout = html.Div(children=[
    html.Div(className="background", id='background', children=[
        html.Div(className="seccion-cuestionario", children=[
            html.Div(className='seccion-progreso',children=[
                dcc.Slider(id='avance-preguntas',min=1, max=40, step=1, value=1,disabled=True)
            ]),
            html.Div(className='seccion-botones', children=[
                html.Button("Atrás",id='btn-atras'),
                html.Button("Guardar respuestas",id='btn-guardar-respuestas'),
                html.Button("Siguiente",id='btn-siguiente'),
            ]),
            html.Div(className="seccion-preguntas-respuestas", children=[
                html.Div(className='seccion-preguntas',id='seccion-preguntas'),
                html.Div(className='seccion-preguntas-hijas',id='seccion-preguntas-hijas')
            ]),
            html.Div(className='seccion-terminar', children=[
                html.Button("Terminar",id='btn-terminar'),
                dcc.Location(id='url_indicadores', refresh=True),
            ]),
        ])
    ])
])

# ---------------- MÉTODOS ----------------
def obtener_pregunta(numero_pregunta: str):
    global preguntas
    global respuestas

    pregunta = preguntas[numero_pregunta]


    tipo = pregunta['tipo']

    texto_pregunta = pregunta['pregunta']

    opciones = pregunta['opciones'] # lista de opciones

    texto_pregunta_html = html.P(texto_pregunta, className="texto-pregunta")

    if tipo == 'SN' or tipo == 'SU':
        respuesta_escogida = None
        if pregunta['numero'] in respuestas:
            respuesta_escogida = respuestas[pregunta['numero']]

        return html.Div([
            texto_pregunta_html,
            dcc.RadioItems(
                id={"type": "opc-pregunta", "index":numero_pregunta},
                options=[opc['opcion'] for opc in opciones],
                value = respuesta_escogida
            )
        ])

    elif tipo == 'SM':
        respuesta_escogida = []
        if pregunta['numero'] in respuestas:
            respuesta_escogida = respuestas[pregunta['numero']]

        return html.Div([
            texto_pregunta_html,
            dcc.Checklist(
                id={"type": "opc-pregunta", "index":numero_pregunta},
                options=[opc['opcion'] for opc in opciones],
                value = respuesta_escogida
                # options=[{'label': opcion, 'value': opcion} for opcion in opciones]
            ),
        ])

def display_pregunta_hija(pregunta: dict):
    numero_pregunta = pregunta['numero']
    tipo = pregunta['tipo']

    texto_pregunta = pregunta['pregunta']

    opciones = pregunta['opciones'] # lista de opciones

    texto_pregunta_html = html.P(texto_pregunta, className="texto-pregunta")

    if tipo == 'SN' or tipo == 'SU':
        respuesta_escogida = None
        if pregunta['numero'] in respuestas:
            respuesta_escogida = respuestas[pregunta['numero']]

        return html.Div([
            texto_pregunta_html,
            dcc.RadioItems(
                id={"type": "opc-pregunta", "index":numero_pregunta},
                options=[opc['opcion'] for opc in opciones],
                value = respuesta_escogida
            )
        ])

    elif tipo == 'SM':
        respuesta_escogida = []
        if pregunta['numero'] in respuestas:
            respuesta_escogida = respuestas[pregunta['numero']]

        return html.Div([
            texto_pregunta_html,
            dcc.Checklist(
                id={"type": "opc-pregunta", "index":numero_pregunta},
                options=[opc['opcion'] for opc in opciones],
                value = respuesta_escogida
                # options=[{'label': opcion, 'value': opcion} for opcion in opciones]
            ),
        ])

def get_preguntas():
    global preguntas
    preguntas = mongo.get_preguntas()


def get_respuestas():
    global respuestas
    respuestas = mongo.get_respuestas()['respuestas']
    # print(respuestas)


def update_respuestas():
    global respuestas
    mongo.update_respuestas(respuestas)



def get_pregunta_hija(num_pregunta: str, respuesta: str) -> {}:
    global preguntas
    pregunta = preguntas[num_pregunta]

    if len(pregunta['hijas']) == 0:
        return {}

    for hija in pregunta['hijas']:
        if hija['opcion_papa'] == respuesta:
            return hija

def get_hija_numeros(num_papa: str, num_hija: str):
    global preguntas
    pregunta = preguntas[num_papa]

    if len(pregunta['hijas']) == 0:
        return {}

    for hija in pregunta['hijas']:
        if hija['numero'] == num_hija:
            return hija

# -----------------------------------------

# ---------------- CALLBACKS ----------------
@callback(
    Output('seccion-preguntas','children'),
     Input('background','children'),
)
def obtener_primera_pregunta(children):
    get_respuestas()
    global preguntas
    get_preguntas()

    return obtener_pregunta('1')

@callback(
    Input('btn-guardar-respuestas','n_clicks')
)
def upload_respuestas(n_clicks):
    update_respuestas()


@callback(
    Output('seccion-preguntas-hijas','children'),
    Input({'type':'opc-pregunta','index':ALL}, 'value'),
    prevent_initial_call=True
)
def guardar_respuesta(value):
    global respuestas
    ctx = dash.callback_context
    dict_respuesta = ctx.triggered[0]

    if dict_respuesta['value'] is None:
        raise PreventUpdate

    # Pregunta hija
    if len(dict_respuesta['prop_id'].split('.')) > 2:
        respuesta = dict_respuesta['value']
        elementos = dict_respuesta['prop_id'].split('.')
        num_pregunta_hija = json.loads(elementos[0] + '.' + elementos[1])['index']

        respuestas[num_pregunta_hija] = respuesta

        num_pregunta_papa = num_pregunta_hija.split('.')[0]
        respuesta_papa = respuestas[num_pregunta_papa]

        if isinstance(respuesta_papa,str):
            hija = get_pregunta_hija(num_pregunta=num_pregunta_papa, respuesta=respuesta_papa)
            return display_pregunta_hija(hija)

        elif isinstance(respuesta_papa, list):
            displays_hijas = []

            for rsp in respuesta_papa:
                hija = get_pregunta_hija(num_pregunta=num_pregunta_papa, respuesta=rsp)

                displays_hijas.append(display_pregunta_hija(hija))

            return displays_hijas

    num_pregunta = str(json.loads(dict_respuesta['prop_id'].split('.')[0])['index'])
    respuesta = dict_respuesta['value']

    # guardar la respuesta hecha por el usuario
    respuestas[num_pregunta] = respuesta

    # el tipo de pregunta es SN o SU
    if isinstance(respuesta,str):
        hija = get_pregunta_hija(num_pregunta=num_pregunta, respuesta=respuesta)

        if hija is None:
            raise PreventUpdate

        return display_pregunta_hija(hija)

    elif isinstance(respuesta,list):
        display_hijas = []

        for rsp in respuesta:
            hija = get_pregunta_hija(num_pregunta=num_pregunta, respuesta=rsp)
            if hija:
                display_hijas.append(display_pregunta_hija(hija))
        return display_hijas


@callback(
    [Output('seccion-preguntas','children',allow_duplicate=True),
     Output('avance-preguntas','value',allow_duplicate=True),
     Output('seccion-preguntas-hijas','children',allow_duplicate=True)],
    State('avance-preguntas','value'),
    Input('btn-siguiente','n_clicks'),
    prevent_initial_call=True
)
def siguiente_pregunta(num_pregunta,n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    return obtener_pregunta(str(num_pregunta+1)),num_pregunta+1, []


@callback(
    [Output('seccion-preguntas','children',allow_duplicate=True),
     Output('avance-preguntas','value',allow_duplicate=True)],
    State('avance-preguntas','value'),
    Input('btn-atras','n_clicks'),
    prevent_initial_call=True
)
def anterior_pregunta(num_pregunta,n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    return obtener_pregunta(str(num_pregunta-1)),num_pregunta-1


@callback(
    Output('url_indicadores', 'pathname'),
    Input('btn-terminar', 'n_clicks'),
    prevent_initial_call=True
)
def iniciar_sesion(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    return '/nivel_madurez'

# ----------------------------------------
