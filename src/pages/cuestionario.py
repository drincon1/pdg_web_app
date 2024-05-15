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

"""
    respuestas = { 
        numero: {numero: "", respuesta: "", puntos: ""}
    }
    
"""

""" ------------------------------------------- """

dash.register_page(__name__)

layout = html.Div(children=[
    html.Div(className="background", id='background', children=[
        html.Div(className="seccion-cuestionario", children=[
            html.Div(className='seccion-progreso',children=[
                dcc.Slider(id='avance-preguntas',min=1, max=40, step=1, value=1)
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
                html.Button("Terminar",id='btn-terminar', className="button-primary", disabled=True),
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
    
    texto_pregunta = "(" + numero_pregunta + ")  " + pregunta['pregunta']
  
    opciones = pregunta['opciones'] # lista de opciones

    texto_pregunta_html = html.P(texto_pregunta, className="texto-pregunta")

    if tipo == 'SN' or tipo == 'SU':
        respuesta_escogida = None
        if pregunta['numero'] in respuestas:
            respuesta_escogida = respuestas[pregunta['numero']]['respuesta']

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
            for respuesta in respuestas[pregunta['numero']]:
                respuesta_escogida.append(respuesta['respuesta'])
             
            # respuesta_escogida = respuestas[pregunta['numero']]['respuesta']

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
            respuesta_escogida = respuestas[pregunta['numero']]['respuesta']

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
            respuesta_escogida = respuestas[pregunta['numero']]['respuesta']

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
    respuestas = mongo.get_respuestas()


def update_respuestas():
    global respuestas
    mongo.update_respuestas(respuestas)
    # print(respuestas)
    

def get_puntos_num_pregunta_respuesta(num_pregunta: str, respuesta: str) -> int:
    global preguntas
    pregunta = preguntas[num_pregunta]

    for opc in pregunta['opciones']:
        if opc['opcion'] == respuesta:
            return opc['puntos']

def get_puntos_pregunta_hija(hija: dict, respuesta: str) -> int:
    opciones = hija['opciones']

    for opc in opciones:
        if opc['opcion'] == respuesta:
            return opc['puntos']

def get_pregunta_hija(num_pregunta: str, respuesta: str) -> dict:
    global preguntas
    pregunta = preguntas[num_pregunta]

    if len(pregunta['hijas']) == 0:
        return {}

    for hija in pregunta['hijas']:
        if hija['opcion_papa'] == respuesta:
            return hija


def get_hija_numeros(num_papa: str, num_hija: str) -> str:
    """
    Devuelve la opción que activa esta pregunta.
    Usualmente es usado cuando la pregunta tiene más de una hija.
    """
    global preguntas
    pregunta = preguntas[num_papa]

    if len(pregunta['hijas']) == 0:
        return {}

    for hija in pregunta['hijas']:
        if hija['numero'] == num_hija:
            return hija['opcion_papa']

def get_hija_num_papa_num_hija(num_papa: str, num_hija: str) -> str:
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
    # get_respuestas()
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
    global preguntas
    ctx = dash.callback_context
    dict_respuesta = ctx.triggered[0]

    if dict_respuesta['value'] is None:
        raise PreventUpdate

    # Pregunta hija
    if len(dict_respuesta['prop_id'].split('.')) > 2:
        respuesta = dict_respuesta['value']
        elementos = dict_respuesta['prop_id'].split('.')
        num_pregunta_hija = json.loads(elementos[0] + '.' + elementos[1])['index']
        # print("dict_respuesta",dict_respuesta)

        num_pregunta_papa = num_pregunta_hija.split('.')[0]
        respuesta_papa = ""
        display_final = []

        if isinstance(respuestas[num_pregunta_papa],dict):
            respuesta_papa = respuestas[num_pregunta_papa]['respuesta']
        elif isinstance(respuestas[num_pregunta_papa],list):
            # Este condicional solo ocurre para la pregunta #3
            respuestas_papa = respuestas[num_pregunta_papa]
            for elemento in respuestas_papa:
                if elemento['respuesta'] == get_hija_numeros(num_papa=num_pregunta_papa,num_hija=num_pregunta_hija):
                    respuesta_papa = elemento['respuesta']

        if isinstance(respuesta_papa,str):
            hija = get_pregunta_hija(num_pregunta=num_pregunta_papa, respuesta=respuesta_papa)
            puntos = get_puntos_pregunta_hija(hija=hija, respuesta=respuesta)
            
            respuestas[num_pregunta_hija] = {'numero': num_pregunta_hija, 'respuesta': respuesta, 'puntos': puntos, 'dimension': hija['dimension']}
            
            # print("Respuestas:\n", respuestas)
            display_final.append(display_pregunta_hija(hija))

            # return display_pregunta_hija(hija)

        elif isinstance(respuesta_papa, list):
            displays_hijas = []
            respuestas_guardar = []

            for rsp in respuesta_papa:
                hija = get_pregunta_hija(num_pregunta=num_pregunta_papa, respuesta=rsp)

                puntos = get_puntos_pregunta_hija(hija=hija, respuesta=rsp)
                
                nueva_respuesta = {'numero': num_pregunta_hija,'respuesta': rsp, 'puntos':puntos, 'dimension': hija['dimension']}

                if num_pregunta_hija in respuestas:
                    if nueva_respuesta not in respuestas_guardar:
                        respuestas_guardar.append(nueva_respuesta)
                else:
                    respuestas_guardar.append(nueva_respuesta)

                display_final.append(display_pregunta_hija(hija))
                displays_hijas.append(display_pregunta_hija(hija))
            
            # print("Respuestas:\n", respuestas)

            if len(respuesta_papa) > 0:
                respuestas[num_pregunta] = respuestas_guardar
            
            # return displays_hijas

        return display_final
        

    num_pregunta = str(json.loads(dict_respuesta['prop_id'].split('.')[0])['index'])
    respuesta = dict_respuesta['value']


    # el tipo de pregunta es SN o SU
    if isinstance(respuesta,str):
        puntos = get_puntos_num_pregunta_respuesta(num_pregunta=num_pregunta, respuesta=respuesta)
        
        hija = get_pregunta_hija(num_pregunta=num_pregunta, respuesta=respuesta)
        
        # guardar la respuesta hecha por el usuario
        respuestas[num_pregunta] = {'numero': num_pregunta,'respuesta': respuesta, 'puntos':puntos, 'dimension': preguntas[num_pregunta]['dimension']}

        
         # print("Respuestas:\n", respuestas)

        if hija is None or len(hija) == 0:
            delete_key = ""
            for key in respuestas:
                if '.' in key and key.split('.')[0] == num_pregunta:
                    delete_key = key
            if delete_key != "":
                respuestas.pop(delete_key)
            return []
        
        return display_pregunta_hija(hija)

    elif isinstance(respuesta,list):

        display_hijas = []
        respuestas_guardar = []

        for rsp in respuesta:
            puntos = get_puntos_num_pregunta_respuesta(num_pregunta=num_pregunta, respuesta=rsp)
            nueva_respuesta = {'numero': num_pregunta,'respuesta': rsp, 'puntos':puntos, 'dimension': preguntas[num_pregunta]['dimension']}

            if num_pregunta in respuestas:
                if nueva_respuesta not in respuestas_guardar:
                    respuestas_guardar.append(nueva_respuesta)
            else:
                respuestas_guardar.append(nueva_respuesta)

            hija = get_pregunta_hija(num_pregunta=num_pregunta, respuesta=rsp)
            if hija:
                display_hijas.append(display_pregunta_hija(hija))
        # print("Respuestas:\n", respuestas)
        if len(respuesta) > 0:
            respuestas[num_pregunta] = respuestas_guardar
        
        return display_hijas


@callback(
    [Output('seccion-preguntas', 'children', allow_duplicate=True),
     Output('seccion-preguntas-hijas','children',allow_duplicate=True)],
    Input('avance-preguntas', 'value'),
    prevent_initial_call=True
)
def actualizar_pregunta(numero_pregunta):
    return obtener_pregunta(str(numero_pregunta)), []

@callback(
    [Output('seccion-preguntas','children',allow_duplicate=True),
     Output('avance-preguntas','value',allow_duplicate=True),
     Output('seccion-preguntas-hijas','children',allow_duplicate=True),
     Output('btn-siguiente','disabled'),
     Output('btn-terminar','disabled')],
    State('avance-preguntas','value'),
    Input('btn-siguiente','n_clicks'),
    prevent_initial_call=True
)
def siguiente_pregunta(num_pregunta,n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    if num_pregunta == 39:
         return obtener_pregunta(str(num_pregunta+1)),num_pregunta+1, [], True, False
    return obtener_pregunta(str(num_pregunta+1)),num_pregunta+1, [], False, True


@callback(
    [Output('seccion-preguntas','children',allow_duplicate=True),
     Output('avance-preguntas','value',allow_duplicate=True),
     Output('seccion-preguntas-hijas','children',allow_duplicate=True)],
    State('avance-preguntas','value'),
    Input('btn-atras','n_clicks'),
    prevent_initial_call=True
)
def anterior_pregunta(num_pregunta,n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    return obtener_pregunta(str(num_pregunta-1)),num_pregunta-1, []


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
