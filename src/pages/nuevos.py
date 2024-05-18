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
indicadores: dict = {}
"""
    indicadores = {
        "numero" = {
            nombre: '', # Nombre del indicador
            unidad: '', # Unidades del indicador
            categoria: '', # Categoría del indicador
            fuente: '', # URL de donde se puede encontrar más información del indicador
            propio: '', # El indicador es propio de la empresa (SI/NO)
            mide: '', # La empresa mide (SI,NO,NS/NR) el indicador
            dimensiones: {
                'Granularidad': "", # Respuesta para la dimensión 'Granularidad'
                'Frecuencia': "", # Respuesta para la dimensión 'Frecuencia'
                'Comparabilidad': "", # Respuesta para la dimensión 'Comparabilidad'
                'Fuente': "", # Respuesta para la dimensión 'Fuente'
                'Tipo': "", # Respuesta para la dimensión 'Tipo'
                'SBT': "", # Respuesta para la dimensión 'SBT'
                'Validación Externa': "", # Respuesta para la dimensión 'Validación Externa'
            }
        }
    }
"""

dimensiones_indicadores: dict = {}
"""
    dimensiones_indicadores = {
        "dimension" = {
            'pregunta': "", # Pregunta que se debe hacer para la dimensión
            'opciones': [] # Lista de opciones correspondientes a la pregunta
            'tipo': # NOTA: Por ahora no se va a usar este atributo
        }
    }
"""

dimensiones_temporales:dict = {
    'Granularidad': None,
    'Frecuencia': None,
    'Comparabilidad': None,
    'Fuente': None,
    'Tipo': None,
    'SBT': None,
    'Validación Externa': None
}

numero_nuevo_indicador: int = None

""" ----------------------------------------- """

""" ---------------- MÉTODOS ---------------- """

def get_max_numero() -> int:
    global indicadores
    max = 0

    for numero in indicadores:
        if int(numero) > max:
            max = int(numero)
    
    global numero_nuevo_indicador
    numero_nuevo_indicador = max + 1

def select_indicadores():
    """
        Obtener los indicadores que están almacenados en Mongo DB
    """
    global indicadores
    indicadores = mongo.get_indicadores_usuario()

def select_dimensiones():
    """Obtener las dimensiones que se evaluan de cada indicador. 
        Estas dimensiones no están almacenadas en Mongo.
    """
    global dimensiones_indicadores
    dimensiones_indicadores= {
        'Granularidad': {
            'pregunta': 'Seleccione el nivel de granularidad de los datos',
            'opciones': ['País','Departamento','Municipio','Cuenca','NS/NR']
        },
        'Frecuencia': {
            'pregunta':'Seleccione la frecuencia de los datos utilizados para armar/calcular los indicadores',
            'opciones': ['Diaria','Semanal','Mensual','Bimestral','Semestral','Anual','NS/NR']
        },
        'Comparabilidad': {
            'pregunta': '¿Sus datos han sido comparados con otros datos externos?',
            'opciones': ['SI','NO','NS/NR']
        },
        'Fuente': {
            'pregunta': '¿Cuál es la fuente principal de los datos utilizados para armar/calcular los indicadores?',
            'opciones': ['Datos primarios','Datos secundatios','NS/NR']
        },'Tipo': {
            'pregunta':'¿Qué tipo de indicador es?',
            'opciones': ['Cualitativo','Cuantitativo','NS/NR']
        },
        'SBT': {
            'pregunta': '¿Sus datos son Science Based Targets (SBT)?',
            'opciones': ['SI','NO','NS/NR']
        },
        'Validación Externa': {
            'pregunta': '¿Los datos utilizados para armar/calcular el indicador han sido validados por una organización externa (entes gubernamentales, organizaciones científicas, empresas de mismo sector, etc.)',
            'opciones': ['SI','NO','NS/NR']
        },
        
    }

def display_dimensiones_indicador(num_indicador: str):
    global dimensiones_indicadores

    layout_indicadores: list = [html.Div(html.H5("Complete la siguiente información"))]

    for dimension in dimensiones_indicadores:
        layout_indicadores.append(
            html.Div([
                dbc.Label(dimensiones_indicadores[dimension]['pregunta'], style={'margin-top':'5px','font-weight': 'bold'}),
                dbc.RadioItems(
                    id={"type": "opc-dimension-nuevo-indicador", "index":f"{num_indicador}-{dimension}"},
                    options=dimensiones_indicadores[dimension]['opciones'],
                    inline=True
                )
            ])
        )

    return layout_indicadores

""" ------------------------------------------- """

""" ---------------- CALLBACKS ---------------- """
# CALLBACK: OBTENER LOS INDICADORES Y LAS DIMENSIONES AL CARGAR LA PÁGINA POR PRIMERA VEZ
@callback(
    Output('seccion-dimensiones-nuevo-indicador','children'),
     Input('background','children'),
)
def obtener_indicadores(children):
    select_indicadores()
    select_dimensiones()
    get_max_numero()
    global numero_nuevo_indicador
    return display_dimensiones_indicador(str(numero_nuevo_indicador))

@callback(
    Output("modal", "is_open"),
    [Input("btn-explicacion", "n_clicks"), Input("btn-cerrar", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@callback(
    Input({"type": "opc-dimension-nuevo-indicador", "index":ALL},'value'),
    prevent_initial_call=True
)
def set_dimensiones_temporales(value):
    ctx = dash.callback_context
    dict_respuesta = ctx.triggered[0]
    if dict_respuesta['value'] is None:
        raise PreventUpdate
    
    global indicadores
    global dimensiones_indicadores
    global dimensiones_temporales

    indice = json.loads(dict_respuesta['prop_id'].split('.')[0])['index'].split('-')

    num_indicador = str(indice[0])
    dimension = str(indice[1])

    posicion = 0
    for dim in dimensiones_indicadores:
        if dim == dimension:
            break
        posicion += 1
    
    if len(value) > 0:
        dimensiones_temporales[dimension] = value[posicion]
    


@callback(
    [Output('alerta-indicador-guarado','children'),
     Output('alerta-indicador-guarado','color'),
     Output('alerta-indicador-guarado','is_open'),
     Output('alerta-indicador-guarado','duration'),
     Output('input-nombre', 'value'),
     Output('input-unidad', 'value'),
     Output('select-categoria', 'value'),
     Output('seccion-dimensiones-nuevo-indicador','children',allow_duplicate=True)],
    [State('input-nombre', 'value'),
     State('input-unidad', 'value'),
     State('select-categoria', 'value')],
    Input('btn-guardar-nuevo-indicador', 'n_clicks'),
    prevent_initial_call=True
)
def guardar_nuevo_indicador(nombre,unidad,categoria,n_clicks):
    global dimensiones_temporales, numero_nuevo_indicador, indicadores
    if nombre is None or unidad is None or categoria is None:
        return ("Información incompleta"), "danger",True, 2000, None, None, None, display_dimensiones_indicador(str(numero_nuevo_indicador))
    if numero_nuevo_indicador < 31:
        numero_nuevo_indicador = 31

    indicadores[str(numero_nuevo_indicador)] = {
        'nombre': nombre,
        'unidad': unidad,
        'categoria': categoria,
        'fuente': None,
        'propio': 'SI',
        'mide': 'SI',
        'dimensiones': dimensiones_temporales
    }

    indicadores_guardar = []
    for numero in indicadores:
        # if indicadores[numero]['mide'] == 'SI':
        indicadores_guardar.append({
            'numero': numero,
            'nombre': indicadores[numero]['nombre'],
            'propio': indicadores[numero]['propio'],
            'mide': indicadores[numero]['mide'],
            'dimensiones': indicadores[numero]['dimensiones'],
        })
    mongo.set_indicadores(indicadores=indicadores_guardar)

    # SE DEBE REINICIAR EL MAXIMO INDICE
    numero_nuevo_indicador += 1

    # DESPUES DE GUARDAR SE DEBE REINICIAR EL DICTIONARIO DE DIMENSINOES TEMPORALES
    dimensiones_temporales = {
        'Granularidad': None,
        'Frecuencia': None,
        'Comparabilidad': None,
        'Fuente': None,
        'Tipo': None,
        'SBT': None,
        'Validación Externa': None
    }

    return ("Indicador guardado con éxito"), "success", True, 2000, None, None, None, display_dimensiones_indicador(str(numero_nuevo_indicador))

@callback(
    Output('url_ssee', 'pathname'),
    Input('btn-terminar-nuevos-indicadores', 'n_clicks'),
    prevent_initial_call=True
)
def go_ssee(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate    
        
    return '/ssee'
    
""" -------------------------------------------- """

""" ---------------- COMPONENTS ---------------- """


""" ---------------------------------------- """


""" ---------------- LAYOUT ---------------- """
layout = html.Div(children=[
    html.Div(className="background", id='background', children=[
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.Img(className="water-image", src="assets/imagenes/water-drop.png"),
                html.H3("Autodiagnóstico empresarial sobre el uso del agua - Nuevos Indicadores"),
            ],
        ),
        html.Div(className="seccion-cuestionario", children=[
            html.Div(className='seccion-botones', children=[
                dbc.Button("Explicación", id="btn-explicacion", n_clicks=0),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Ingrese sus indicadores")),
                        dbc.ModalBody("En esta parte podrá ingresar los indicadores que no encontró en la sección anterior. Cuando llene toda la información presione el botón 'Guardar' para guardar su nuevo indicador. Si no quiere añadir ningún indicador o ya ha agregado todos sus propios indicadores presione el botón 'Terminar'."),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Cerrar", id="btn-cerrar", className="ms-auto", n_clicks=0
                            )
                        ),
                    ],
                    id="modal",
                    is_open=False,
                ),
                html.Button("Guardar",id='btn-guardar-nuevo-indicador', className='btn-cuestionario'),
            ]),
            html.Div(className="seccion-preguntas-respuestas", children=[
                # Nombre del indicador
                dbc.InputGroup(
                    [dbc.InputGroupText("Nombre"), dbc.Input(placeholder="Ingrese acá el nombre de su indicador", id="input-nombre")],
                    className="mb-3",
                ),
                # Unidad del indicador
                dbc.InputGroup(
                    [dbc.InputGroupText("Unidad"), dbc.Input(placeholder="Ingrese acá la unidad de su indicador", id="input-unidad")],
                    className="mb-3",
                ),

                # Dimensiones del indicador
                dbc.InputGroup(
                    [
                        dbc.Select(
                            options=['Desempeño','Riesgo','Impacto','Dependencia'],
                            id="select-categoria"
                        ),
                        dbc.InputGroupText("Categoría de indicador"),
                    ]
                ),
                html.Div(className='seccion-preguntas-hijas',id='seccion-dimensiones-nuevo-indicador')
            ]),
            html.Div(className='seccion-terminar', children=[
                html.Button("Terminar",id='btn-terminar-nuevos-indicadores', className='btn-cuestionario'),
                dcc.Location(id='url_ssee', refresh=True),
                dbc.Alert(id="alerta-indicador-guarado", is_open=False, style={'margin-top': '10px'}),
            ]),
        ])
    ])
])
""" ----------------------------------------- """