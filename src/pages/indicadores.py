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
            ssee: {
                numero: { # numero del servicio ecosistemico j asociado al indicador i
                    nombre: '', # nombre del servicio ecosistemico j asociado al indicador i
                    dependencia:'', # [BAJA, MEDIA, ALTA]
                    impacto: '', # [POSITIVO, NEGATIVO]
                    funciones: [], # funciones asociadas al servicio ecositemico j del indicador i
                }, 
            }
            ]
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

""" ----------------------------------------- """

""" ---------------- MÉTODOS ---------------- """
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

def display_indicador(numero_indicador: str):
    global indicadores

    indicador: dict = indicadores[numero_indicador]

    valor_indicador = indicador['mide']
    # if valor_indicador != "SI":
    #     valor_indicador = None

    return html.Div([
        dbc.Card([
            dbc.CardHeader(indicador['categoria']),
            dbc.CardBody([
                html.H5(indicador['nombre'], className="card-title"),
                html.P(indicador['unidad']),
                dcc.Link('Más información', href=indicador['fuente'], target="_blank")
            ])
        ], color="light", style={"color":"black"}),

        html.P(style={"margin-top":"10px"},children="¿Su empresa mide o tiene en cuenta el anterior indicador para entender las dependencias, impactos y acciones que tiene sobre el agua?"),
        dcc.RadioItems(
                id={"type": "opc-indicador", "index":numero_indicador},
                options=['SI','NO','NS/NR'],
                value=valor_indicador
        )
    ])

def display_dimensiones_indicador(num_indicador: str):
    global dimensiones_indicadores
    global indicadores
    layout_indicadores: list = [html.Div(html.H5("Complete la siguiente información"))]

    respuestas_dimension = indicadores[num_indicador]['dimensiones']

    for dimension in dimensiones_indicadores:
        layout_indicadores.append(
            html.Div([
                dbc.Label(dimensiones_indicadores[dimension]['pregunta'], style={'margin-top':'5px','font-weight': 'bold'}),
                dbc.RadioItems(
                    id={"type": "opc-dimension-indicador", "index":f"{num_indicador}-{dimension}"},
                    options=dimensiones_indicadores[dimension]['opciones'],
                    inline=True,
                    value=respuestas_dimension[dimension]
                )
            ])
        )

    return layout_indicadores

""" ------------------------------------------- """

""" ---------------- CALLBACKS ---------------- """
# CALLBACK: OBTENER LOS INDICADORES Y LAS DIMENSIONES AL CARGAR LA PÁGINA POR PRIMERA VEZ
@callback(
    Output('seccion-indicadores','children'),
     Input('background','children'),
)
def obtener_indicadores(children):
    select_indicadores()
    select_dimensiones()
    return display_indicador(numero_indicador="1")

# CALLBACK: DISPLAY LAS DIMENSIONES SEGÚN SI LA EMPRESA SELECCIONO QUE SI LO MIDE
@callback(
    Output('seccion-dimensiones-indicadores','children'),
    Input({'type':'opc-indicador','index':ALL}, 'value')
)
def callback_display_dimensiones(opc_sele):
    ctx = dash.callback_context
    dict_respuesta = ctx.triggered[0]

    if dict_respuesta['value'] is None:
        raise PreventUpdate
    
    global indicadores
    
    num_indicador = str(json.loads(dict_respuesta['prop_id'].split('.')[0])['index'])
    
    if len(opc_sele) > 0:
        opc_sele = opc_sele[0]
        indicadores[num_indicador]['mide'] = opc_sele

    if opc_sele == None or opc_sele == 'NO' or opc_sele == 'NS/NR':
        return []


    layout_dimensiones = display_dimensiones_indicador(num_indicador=num_indicador)
        
    return layout_dimensiones

# CALLBACK: RESPUESTA DE DIMENSIÓN
@callback(
    Input({'type':'opc-dimension-indicador','index':ALL}, 'value')
)
def update_dimension_indicador(opc_sele):
    ctx = dash.callback_context
    dict_respuesta = ctx.triggered[0]
    if dict_respuesta['value'] is None:
        raise PreventUpdate
    
    global indicadores
    global dimensiones_indicadores

    indice = json.loads(dict_respuesta['prop_id'].split('.')[0])['index'].split('-')

    num_indicador = str(indice[0])
    dimension = str(indice[1])

    posicion = 0
    for dim in dimensiones_indicadores:
        if dim == dimension:
            break
        posicion += 1
    
    if len(opc_sele) > 0:
        indicadores[num_indicador]['dimensiones'][dimension] = opc_sele[posicion]
    

    
# CALLBACK: ACTUALIZAR PREGUNTA
@callback(
    [Output('seccion-indicadores', 'children', allow_duplicate=True),
     Output('seccion-dimensiones-indicadores', 'children', allow_duplicate=True),
     Output('btn-siguiente-indicador','disabled',allow_duplicate=True),
     Output('btn-terminar-indicadores','disabled',allow_duplicate=True),
     Output('btn-atras-indicador','disabled',allow_duplicate=True),],
    State('avance-indicadores', 'max'),
    Input('avance-indicadores', 'value'),
    prevent_initial_call=True
)
def actualizar_indicador(max_indicador, numero_pregunta):
    if numero_pregunta == max_indicador:
        return display_indicador(str(numero_pregunta)), [], True, False, False
    if numero_pregunta == 1:
        return display_indicador(str(numero_pregunta)), [], False, True, True
    
    return display_indicador(str(numero_pregunta)), [], False, True, False

# CALLBACK: SIGUIENTE PREGUNTA
@callback(
    [Output('seccion-indicadores','children',allow_duplicate=True),
     Output('seccion-dimensiones-indicadores', 'children', allow_duplicate=True),
     Output('avance-indicadores','value',allow_duplicate=True),
     Output('btn-siguiente-indicador','disabled',allow_duplicate=True),
     Output('btn-terminar-indicadores','disabled',allow_duplicate=True)],
    [State('avance-indicadores', 'max'),
     State('avance-indicadores','value')],
    Input('btn-siguiente-indicador','n_clicks'),
    prevent_initial_call=True
)
def siguiente_indicador(max_indicador,num_pregunta,n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    if num_pregunta == max_indicador:
         return display_indicador(str(num_pregunta+1)), [], num_pregunta+1, True, False
    return display_indicador(str(num_pregunta+1)),[],num_pregunta+1,False, True


# CALLBACK: ANTERIOR_PREGUNTA
@callback(
    [Output('seccion-indicadores','children',allow_duplicate=True),
     Output('seccion-dimensiones-indicadores', 'children', allow_duplicate=True),
     Output('avance-indicadores','value',allow_duplicate=True),],
    State('avance-indicadores','value'),
    Input('btn-atras-indicador','n_clicks'),
    prevent_initial_call=True
)
def anterior_indicador(num_pregunta,n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    return display_indicador(str(num_pregunta-1)),[],num_pregunta-1    

@callback(
        [Output('alerta-indicadores-guardados','children'),
        Output('alerta-indicadores-guardados','is_open'),
        Output('alerta-indicadores-guardados','duration')],
        Input('btn-guardar-indicadores','n_clicks'),
        prevent_initial_call = True
)
def guardar_indicadores(n_clicks):
    global indicadores
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

    return ('Respuestas guardadas con éxito!'), True, 2000

@callback(
    Output('url_nuevos_indicadores', 'pathname'),
    Input('btn-terminar-indicadores', 'n_clicks'),
    prevent_initial_call=True
)
def indicadores_resultados(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate    
    
    global indicadores
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

    
    return '/nuevos'

""" ---------------------------------------- """

""" ---------------- LAYOUT ---------------- """
layout = html.Div(children=[
    html.Div(className="background", id='background', children=[
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.Img(className="water-image", src="assets/imagenes/water-drop.png"),
                html.H3("Autodiagnóstico empresarial sobre el uso del agua - Indicadores"),
            ],
        ),
        html.Div(className="seccion-cuestionario", children=[
            html.Div(className='seccion-progreso',children=[
                dcc.Slider(id='avance-indicadores',min=1, max=30, step=1, value=1, className="slider"),
                html.Hr()
            ]),
            html.Div(className='seccion-botones', children=[
                html.Button("Atrás",id='btn-atras-indicador', className='btn-cuestionario', disabled=True),
                html.Button("Guardar respuestas",id='btn-guardar-indicadores', className='btn-cuestionario'),
                html.Button("Siguiente",id='btn-siguiente-indicador', className='btn-cuestionario'),
            ]),
            html.Div(className="seccion-preguntas-respuestas", children=[
                html.Div(className='seccion-preguntas',id='seccion-indicadores'),
                html.Div(className='seccion-preguntas-hijas',id='seccion-dimensiones-indicadores')
            ]),
            html.Div(className='seccion-terminar', children=[
                html.Button("Terminar",id='btn-terminar-indicadores', disabled=True, className='btn-cuestionario'),
                dcc.Location(id='url_nuevos_indicadores', refresh=True),
                dbc.Alert(id="alerta-indicadores-guardados", is_open=False, style={'margin-top': '10px'})
            ]),
        ])
    ])
])
""" ----------------------------------------- """