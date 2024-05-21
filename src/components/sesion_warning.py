import dash
from dash import html, dcc, callback, Output,Input
import dash_bootstrap_components as dbc
import os

def create_no_user_warning(url: str):
    user = os.environ.get("USERNAME")
    if user is None or user == "USERNAME":
        return html.Div([
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Advertencia"), close_button=False),
                    dbc.ModalBody("¡Ups! No has iniciado sesión, por favor, inicia sesión para poder continuar"),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                            "Iniciar sesión", id="btn-warning-iniciar-sesion", className="ms-auto", n_clicks=0
                            ),
                            dcc.Location(id='url-ini-sesion', refresh=True),
                        ]
                    ),
                ],
                id="modal-iniciar-sesion",
                is_open=True,
                keyboard=False,
                backdrop="static",
            ),
            
        ])
    
    return []

@callback(
    Output('url-ini-sesion','pathname'),
    Input('btn-warning-iniciar-sesion', 'n_clicks')
)
def go_iniciar_sesion(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise dash.exceptions.PreventUpdate
    
    return '/'
