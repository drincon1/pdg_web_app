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
        indice_display: { # El indice display sirve para facilitar el orden en el display 
            numero: '', # numero del servicio ecosistemico
            nombre: '', # nombre del servicio ecosistemico
            dependencia:'', # [BAJA, MEDIA, ALTA]
            impacto: '', # [POSITIVO, NEGATIVO],
            num_indicador = '', # numero del indicador asociado,
        }, 
    }
"""


""" ---------- METODOS ---------- """
dash.register_page(__name__)


def get_ssee():
    global ssee
    ssee = mongo.get_ssee_usuario()
    
    # ! El siguiente codigo NO se debe borrar
    # El siguiente codigo cambia el numero del ssee por un indice para poder cambiar entre preguntas sin problemas
    indice_display = 1
    ssee_temp = {}

    for s in ssee:
        ssee_temp[str(indice_display)] = ssee[s]
        indice_display += 1

    ssee = ssee_temp


def display_ssee(num_ssee: str):
    global ssee
    servicio = ssee[num_ssee]
    layout = html.Div([
        dbc.Card([
            dbc.CardHeader('Descripción del SSEE'),
            dbc.CardBody([
                html.H4(servicio['nombre']),
                html.H6(servicio['tipo']),
                html.P(servicio['descripcion']),
            ])
        ], color="light", style={"color":"black"}),

        html.P(style={"margin-top":"10px"},children="¿Cuál es el nivel de dependencia de su empresa sobre este servicio ecosistémico?"),
        dcc.RadioItems(
                id={"type": "opc-ssee-dependencia", "index":f'ssee-dependencia-{num_ssee}'},
                options=['BAJO','MEDIO','ALTO','NS/NR'],
                value=servicio['dependencia'],
        ),
        html.P(style={"margin-top":"10px"},children="¿Qué tipo de impacto tiene su empresa sobre este servicio ecosistémico?"),
        dcc.RadioItems(
                id={"type": "opc-ssee-impacto", "index":f'ssee-impacto-{num_ssee}'},
                options=['POSITIVO','NEGATIVO','NS/NR'],
                value=servicio['impacto'],
        )
    ])

    return layout

def set_servicios_guardar() -> list:
    global ssee
    ssee_guardar: list = []
    for key in ssee:
        servicio = ssee[key]
        ssee_guardar.append({
            'numero': servicio['numero'], 
            'nombre': servicio['nombre'], 
            'dependencia':servicio['dependencia'], 
            'impacto': servicio['impacto'], 
            'num_indicador': servicio['num_indicador'],
        })
    
    return ssee_guardar

""" ---------- CALLBACKS ---------- """
@callback(
    [Output('seccion-ssee','children'),
     Output('avance-ssee','max'),
     Output('modal_no_indicadores','is_open')],
    Input('background','children')
)
def display_primer_ssee(children):
    global see
    get_ssee()
    if len(ssee) == 0:
        return [], 1, True
    return display_ssee(num_ssee='1'),len(ssee), False

@callback(
    Output("url_relaciones_ssee", "pathname", allow_duplicate=True),
    Input("close", "n_clicks"),
    prevent_initial_call=True
)
def toggle_modal(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate    

    return '/funciones'

@callback(
    Input({'type':'opc-ssee-dependencia','index':ALL}, 'value')
)
def update_dependencia_ssee(opc_sele):
    ctx = dash.callback_context
    dict_respuesta = ctx.triggered[0]

    if dict_respuesta['value'] is None:
        raise PreventUpdate
    
    global ssee

    indice = json.loads(dict_respuesta['prop_id'].split('.')[0])['index'].split('-')
    num_indicador = str(indice[2])
    nivel = dict_respuesta['value']

    ssee[num_indicador]['dependencia'] = nivel

@callback(
    Input({'type':'opc-ssee-impacto','index':ALL}, 'value')
)
def update_impacto_ssee(opc_sele):
    ctx = dash.callback_context
    dict_respuesta = ctx.triggered[0]

    if dict_respuesta['value'] is None:
        raise PreventUpdate
    
    global ssee

    indice = json.loads(dict_respuesta['prop_id'].split('.')[0])['index'].split('-')
    num_indicador = str(indice[2])
    tipo = dict_respuesta['value']

    ssee[num_indicador]['impacto'] = tipo

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
    mongo.update_servicios(servicios=set_servicios_guardar())

    return ('Respuestas guardadas con éxito!'), True, 2000


@callback(
    Output('url_relaciones_ssee', 'pathname'),
    Input('btn-terminar-ssee', 'n_clicks'),
    prevent_initial_call=True
)
def go_ssee(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate    

    mongo.update_servicios(servicios=set_servicios_guardar())
    
    return '/funciones'

@callback(
    Output("modal_advertencia-ssee", "is_open"),
    Input("close-advertencia-ssee", "n_clicks"),
    prevent_initial_call=True
)
def toggle_modal(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate    

    return False

@callback(
    Output("modal-explicacion-ssee", "is_open"),
    [Input("btn-explicacion-ssee", "n_clicks"), Input("btn-cerrar-explicacion-ssee", "n_clicks")],
    [State("modal-explicacion-ssee", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


""" ---------- LAYOUT ---------- """
layout = html.Div(children=[
    html.Div(className="background", id='background', children=[
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.Img(className="water-image", src="assets/imagenes/water-drop.png"),
                html.H3("Autodiagnóstico empresarial sobre el uso del agua - Servicios Ecosistémicos relacionados a los indicadores"),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Advertencia"), close_button=False),
                        dbc.ModalBody("Usted no ha seleccionado ningun tipo de indicador. Será redirigido al siguiente paso"),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Continuar", id="close", className="ms-auto", n_clicks=0
                            )
                        ),
                    ],
                    id="modal_no_indicadores",
                    is_open=False,
                    keyboard=False,
                    backdrop="static",
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Advertencia"), close_button=False),
                        dbc.ModalBody("Las respuestas NO se guardarán automáticamente. Si quiere guardarlas, debe presionar el botón 'Guardar respuestas'. Al presionar el botón 'Terminar' se guardarán las respuestas, pero se redirigirá al siguiente paso."),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Continuar", id="close-advertencia-ssee", className="ms-auto", n_clicks=0
                            )
                        ),
                    ],
                    id="modal_advertencia-ssee",
                    is_open=True,
                    keyboard=False,
                    backdrop="static",
                ),
            ],
        ),
        html.Div(className="seccion-cuestionario", children=[
            html.Div(className='seccion-progreso',children=[
                # Número de servicios ecosistémicos relacionados
                dcc.Slider(id='avance-ssee',min=1, step=1, value=1, className="slider"),
                html.Hr()
            ]),
            html.Div(className='seccion-botones', children=[
                html.Button("Atrás",id='btn-atras-ssee', className='btn-cuestionario', disabled=True),
                dbc.Button("Explicación",id='btn-explicacion-ssee', color="info",className='btn-cuestionario'),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Servicios Ecosistémicos")),
                        dbc.ModalBody("A continuación usted podrá seleccionar el nivel de dependencia y el tipo de impacto que tiene sobre los servicios ecosistémicos. Estos servicios fueron seleccionados basados en las respuestas de los indicadores. Es decir, aparecen los servicios ecosistémicos relacionados a los indicadores que su empresa mide o contempla."),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Cerrar", id="btn-cerrar-explicacion-ssee", className="ms-auto", n_clicks=0
                            )
                        ),
                    ],
                    id="modal-explicacion-ssee",
                    is_open=False,
                ),
                dbc.Button("Guardar respuestas",id='btn-guardar-ssee', color="primary",className='btn-cuestionario'),
                html.Button("Siguiente",id='btn-siguiente-ssee', className='btn-cuestionario'),
            ]),
            html.Div(className="seccion-preguntas-respuestas", children=[
                # Sección SSEE + Pregunta 
                html.Div(className='seccion-preguntas',id='seccion-ssee'),
            ]),
            html.Div(className='seccion-terminar', children=[
                dbc.Button("Terminar",id='btn-terminar-ssee', color="success", disabled=True, className='btn-cuestionario'),
                dcc.Location(id='url_relaciones_ssee', refresh=True),
                dbc.Alert(id="alerta-ssee-guardados", is_open=False, style={'margin-top': '10px'})
            ]),
        ])
    ])
])
