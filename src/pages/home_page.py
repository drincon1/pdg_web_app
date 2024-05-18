import sys
sys.path.append("..")
import dash_bootstrap_components as dbc
import dash
from dash import html, Output, Input, State, callback, dcc
from connection import MongoDB

dash.register_page(__name__,path='/')

mongo = MongoDB()

layout = html.Div(children=[
    html.Div(className="background", children=[
        html.Div(className="home-page", children=[
            html.Div(className="title-buttons", children=[
                html.P(className="home-title", children="Autodiagnóstico empresarial sobre el uso del agua"),
                html.Div(className="home-login", children=[
                    html.Label("Usuario"),
                    dcc.Input(id='input-usuario'),
                    html.Label("Contraseña"),
                    dcc.Input(type='password',id='input-contrasena'),
                    html.Div(className='home-buttons',children=[
                        html.Button(id="btn-log-in", children="Log-In"),
                        html.Button(id="btn-registrarse", children="Registrarse"),
                        dcc.Location(id='url', refresh=True),
                    ]),
                    html.P(id="error-message",className="error-message")
                ])
            ]),
            html.Img(className="home-image", src="assets/imagenes/home-image.jpg")
        ])
    ])
])

@callback(
    Output('error-message','children',allow_duplicate=True),
    [State('input-usuario','value'),
     State('input-contrasena','value')],
    Input('btn-registrarse','n_clicks'),
    prevent_initial_call=True
)
def registrarse(usuario,contrasena,n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    new_usuario = mongo.create_usuario(usuario=usuario,contrasena=contrasena)
    return f'{new_usuario}'



@callback(
    [Output('url', 'pathname'),
     Output('error-message','children'),],
    [State('input-usuario','value'),
     State('input-contrasena','value')],
    Input('btn-log-in', 'n_clicks'),
    prevent_initial_call=True
)
def iniciar_sesion(usuario, contrasena, n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    usuario_valido = mongo.iniciar_sesion(usuario=usuario, contrasena=contrasena)

    if usuario_valido:
        return '/madurez', ''
        # return '/introduccion',''
    else:
        return '/','Usuario o Contraseña incorrecta'
