import sys
sys.path.append("..")
import os
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
        numero: {numero: "", respuesta: "", puntos: "", dimension: ""}
    }
    
"""

""" ------------------------------------------- """

dash.register_page(__name__)

layout = html.Div(children=[
    html.Div(className="background", id='background', children=[
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.Img(className="water-image", src="assets/imagenes/water-drop.png"),
                html.H3("Autodiagnóstico empresarial sobre el uso del agua - Cuestionario"),
            ],
        ),
        html.Div(className="seccion-cuestionario", children=[
            html.Div(className='seccion-progreso',children=[
                dcc.Slider(id='avance-preguntas',min=1, max=41, step=1, value=1, className="slider"),
                html.Hr()
            ]),
            html.Div(className='seccion-botones', children=[
                html.Button("Atrás",id='btn-atras', className='btn-cuestionario', disabled=True),
                html.Button("Guardar respuestas",id='btn-guardar-respuestas', className='btn-cuestionario'),
                html.Button("Siguiente",id='btn-siguiente', className='btn-cuestionario'),
            ]),
            html.Div(className="seccion-preguntas-respuestas", children=[
                html.Div(className='seccion-preguntas',id='seccion-preguntas'),
                html.Div(className='seccion-preguntas-hijas',id='seccion-preguntas-hijas')
            ]),
            html.Div(className='seccion-terminar', children=[
                html.Button("Terminar",id='btn-terminar', disabled=True, className='btn-cuestionario'),
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

def display_sectores(sectores_industrias: dict):
    sector = None
    sector_mongo = mongo.get_sector_usuario()

    if sector_mongo is not None:
        sector = sector_mongo['sector']

    return html.Div([
            html.P("Seleccione su sector"),
            dcc.Dropdown(
                id="select-sector",
                options=[key for key in sectores_industrias],
                value = sector
            )
        ])

def display_industrias(sectores_industrias: dict):
    industrias = []
    industria = None

    sector_mongo = mongo.get_sector_usuario()
    if sector_mongo is not None and sector_mongo['sector'] is not None:
        industria_mongo = mongo.get_industria_usuario()
        if industria_mongo is not None:
            industria = industria_mongo['industria']
            industrias = sectores_industrias[sector_mongo['sector']]
    else:
        for key in sectores_industrias:
            for indu in sectores_industrias[key]:
                industrias.append(indu)

    return html.Div([
            html.P("Seleccione su sector"),
            dcc.Dropdown(
                id="select-industria",
                options=[ind for ind in industrias],
                value=industria
            )
        ])

def display_departamentos():
    departamento = []
    departamentos = mongo.get_departamentos_usuario()['departamentos']
    if len(departamentos) > 0:
        departamento = departamentos
    departamentos = mongo.get_departamentos_municipios()

    return html.Div([
            html.P("Seleccione sus departamentos", style={'margin-top':'10px'}),
            dcc.Dropdown(
                id="select-departamentos",
                options=[key for key in departamentos],
                multi=True,
                value = departamento,
            )
        ])

def display_municipios():
    municipio = []
    municipios = mongo.get_municipios_usuario()['municipios']
    if len(municipios) > 0:
        municipio = municipios
    departamentos = mongo.get_departamentos_municipios()

    depa_muni = []
    for depa in departamentos:
        for muni in departamentos[depa]:
            depa_muni.append(f"{depa}-{muni}")

    return html.Div([
            html.P("Seleccione sus municipios",style={'margin-top':'10px'}),
            dcc.Dropdown(
                id="select-municipios",
                options=[dm for dm in depa_muni],
                multi=True,
                value = municipio,
            )
        ])
    



def get_preguntas():
    global preguntas
    preguntas = mongo.get_preguntas()


def get_respuestas():
    global respuestas
    mongo_rsp = mongo.get_respuestas()['respuestas']

    dict_respuestas = {}
    for rsp in mongo_rsp:
        if isinstance(rsp, dict):
            dict_respuestas[rsp['numero']] = rsp
        elif isinstance(rsp, list):
            dict_respuestas[rsp[0]['numero']] = rsp
    
    respuestas = dict_respuestas


def update_respuestas():
    global respuestas
    mongo.update_respuestas(respuestas)
    

def get_puntos_num_pregunta_respuesta(num_pregunta: str, respuesta: str) -> int:
    global preguntas
    pregunta = preguntas[num_pregunta]

    for opc in pregunta['opciones']:
        if opc['opcion'] == respuesta:
            return opc['puntos']

def get_puntos_pregunta_hija(hija: dict, respuesta: str) -> int:
    opciones = hija['opciones']
    if isinstance(respuesta,list):
        if len(respuesta) > 0:
            respuesta = respuesta[0]
        else:
            return 0

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
    Input('select-sector','value')
)
def set_sector(sector):
    mongo.update_sector_usuario(sector)

@callback(
    Input('select-industria','value')
)
def set_industria(industria):
    mongo.update_industria_usuario(industria)

@callback(
    Input('select-departamentos','value')
)
def set_departamentos(departamentos):
    mongo.update_departamentos_usuario(departamentos)

@callback(
    Input('select-municipios','value')
)
def set_municipios(municipios):
    mongo.update_municipios_usuario(municipios)



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
            print(respuestas)
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

        
        if num_pregunta == '1' and respuesta == 'SI':
            sectores_industrias = mongo.get_sectores_industrias()
            return display_sectores(sectores_industrias)
        
        elif num_pregunta == '1' and respuesta == 'NS/NR':
            mongo.update_sector_usuario(None)
            mongo.update_industria_usuario(None)
            return []
        
        elif num_pregunta == '2' and respuesta == 'SI':
            sectores_industrias = mongo.get_sectores_industrias()
            return display_industrias(sectores_industrias)
        
        elif num_pregunta == '2' and respuesta == 'NS/NR':
            mongo.update_industria_usuario(None)
            return []
        
        elif hija is None or len(hija) == 0:
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
        
        if len(respuesta) > 0:
            respuestas[num_pregunta] = respuestas_guardar
        
        if num_pregunta == '3' and 'Departamento' in respuesta and 'Municipio' not in respuesta:
            return display_departamentos()
        elif num_pregunta == '3' and 'Municipio' in respuesta and 'Departamento' not in respuesta:
            return display_municipios()
        elif num_pregunta == '3' and 'Municipio' in respuesta and 'Departamento' in respuesta:
            return [display_departamentos(),display_municipios()]

        return display_hijas


@callback(
    [Output('seccion-preguntas', 'children', allow_duplicate=True),
     Output('seccion-preguntas-hijas','children',allow_duplicate=True),
     Output('btn-siguiente','disabled',allow_duplicate=True),
     Output('btn-terminar','disabled',allow_duplicate=True),
     Output('btn-atras','disabled',allow_duplicate=True),],
    Input('avance-preguntas', 'value'),
    prevent_initial_call=True
)
def actualizar_pregunta(numero_pregunta):
    if numero_pregunta == 41:
        return obtener_pregunta(str(numero_pregunta)), [], True, False, False
    if numero_pregunta == 1:
        return obtener_pregunta(str(numero_pregunta)), [], False, True, True
    
    return obtener_pregunta(str(numero_pregunta)), [], False, True, False

@callback(
    [Output('seccion-preguntas','children',allow_duplicate=True),
     Output('avance-preguntas','value',allow_duplicate=True),
     Output('seccion-preguntas-hijas','children',allow_duplicate=True),
     Output('btn-siguiente','disabled',allow_duplicate=True),
     Output('btn-terminar','disabled',allow_duplicate=True)],
    State('avance-preguntas','value'),
    Input('btn-siguiente','n_clicks'),
    prevent_initial_call=True
)
def siguiente_pregunta(num_pregunta,n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    if num_pregunta == 40:
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
def indicadores_resultados(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate    
    
    update_respuestas()
    
    global respuestas
    pregunta_indicadores = "41"
    
    if pregunta_indicadores in respuestas.keys() and respuestas[pregunta_indicadores]['respuesta'] == 'SI':
        return '/indicadores'
    
    return '/madurez'

# ----------------------------------------
