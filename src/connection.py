from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import os
from classes.pregunta import Pregunta
import pandas as pd

class MongoDB:

    DATABASE = 'web_app'

    def __init__(self):
        user = os.environ.get("DB_USER")
        password = os.environ.get("DB_PASS")

        try:
            uri = f"mongodb+srv://{user}:{password}@clusterpdg.psjdd0v.mongodb.net/?retryWrites=true&w=majority&appName=ClusterPDG"

            self.client = MongoClient(uri, server_api=ServerApi('1'), tls=True)
            self.database = self.client[self.DATABASE]

        except Exception(e) as e:
            print(e)

# ---------------- INICIAR SESION ----------------
    def iniciar_sesion(self,usuario:str, contrasena:str) -> bool:
        try:
            usr = self.get_usuario(usuario=usuario)
            if usr is None:
                return False

            if usr['contrasena'] != contrasena:
                return False

            # Set an environment variable
            os.environ['USERNAME'] = usuario

            return True

        except Exception as e:
            print(e)
# -----------------------------------------

# ---------------- PREGUNTA ---------------
    def get_preguntas(self) -> dict:
        try:
            preguntas: dict = {}
            collection = self.database['preguntas']
            preguntas_dict = collection.find()

            for prg in preguntas_dict:
                preguntas[prg['numero']] = prg

            return preguntas

        except Exception as e:
            print(e)


# -----------------------------------------

# ---------------- USUARIO ----------------
    def get_usuario(self, usuario: str) -> dict:
        try:
            collection = self.database['usuarios']
            usu_dict = collection.find_one({"usuario": usuario})

            return usu_dict  # Return the user document if found, None otherwise

        except Exception as e:
            print(e)
    

    def create_usuario(self, usuario: str, contrasena: str) -> str:
        try:
            if usuario == '' or usuario is None or contrasena is None or contrasena == '':
                return 'Usuario o Contraseña está vació'

            existe = self.get_usuario(usuario)
            if not existe:
                collection = self.database['usuarios']
                # Creating a dictionary with student details
                data = {
                    '_id': ObjectId(),
                    'usuario': usuario,
                    'contrasena': contrasena,
                    'sector': "",
                    'industria': "",
                    'departamentos': [],
                    'municipios': [],
                    'respuestas': [],
                    'indicadores': [],
                    'ssee': []
                }

                # Inserting the student data into the 'students' collection and obtaining the inserted ID
                collection.insert_one(data)

                return f'{usuario} creado con éxito'

            return f"El usuario '{usuario}' ya existe"

        except Exception as e:
            print(e)
# ---------------------------------------------

# ---------------- DIMENSIONES ----------------

    def get_dimensiones(self) -> pd.DataFrame:
        collection = self.database['dimensiones']
        dict_dimensiones = collection.find()
        
        df_dimensiones = pd.DataFrame()

        for dim in dict_dimensiones:
            data = {
                'total_dim': dim['puntos_dim'],
                'peso_expertos': dim['pesos_expertos'],
                'definicion': dim['definicion']
            }
            df_temp = pd.DataFrame(data,index=[dim['dimension']])
            df_dimensiones = pd.concat([df_dimensiones, df_temp], ignore_index=False)


        return df_dimensiones


    def get_puntos_por_dimension(self) -> dict:
        rsp_mongo = self.get_respuestas()
        
        if rsp_mongo is None:
            return {}
        
        respuestas:list = rsp_mongo['respuestas']
        puntos_dimension:dict = {
            'Contexto de la organización': 0,
            'Liderazgo': 0,
            'Planificación':0,
            'Soporte': 0,
            'Operación': 0,
            'Evaluación del desempeño': 0,
            'Mejora': 0
        }

        # print(respuestas)

        for rsp in respuestas:
            for dimension in puntos_dimension:
                if isinstance(rsp, dict):
                    if dimension == rsp['dimension']:
                        # print(dimension, ':', puntos_dimension[dimension])
                        if rsp['puntos'] is not None:
                            if isinstance(rsp['respuesta'], list):
                                puntos_dimension[dimension] = puntos_dimension[dimension] + len(rsp['respuesta'])
                            else:
                                puntos_dimension[dimension] = puntos_dimension[dimension] + rsp['puntos']
                if isinstance(rsp,list):
                    for resp_ in rsp:
                        if dimension == resp_['dimension']:
                            if resp_['puntos'] is not None:
                                if isinstance(resp_['respuesta'],list):
                                    puntos_dimension[dimension] = puntos_dimension[dimension] + len(resp_['respuesta'])
                                else:
                                    puntos_dimension[dimension] = puntos_dimension[dimension] + resp_['puntos']

        # print(puntos_dimension)

        return puntos_dimension

        
# --------------------------------------------

# ---------------- RESPUESTAS ----------------

    def get_respuestas(self) -> dict:
        try:
            user = os.environ.get("USERNAME")
            # if user == None:
            #     user = "daniel"
            collection = self.database['usuarios']
            usu_dict = collection.find_one({"usuario": user}, {'respuestas':1,"_id": 0})
        
            return usu_dict  # Return the user document if found, None otherwise

        except Exception as e:
            print(e)

    def update_respuestas(self, respuestas: dict) -> bool:
        try:
            respuestas_update = []
            for key in respuestas:
                respuestas_update.append(respuestas[key])

            usuario = os.environ.get("USERNAME")

            collection = self.database['usuarios']

            document_to_update = {"usuario": usuario}

            new_respuestas = {"$set" : {"respuestas": respuestas_update}}

            result = collection.update_one(document_to_update, new_respuestas)
            return True

        except Exception as e:
            print(e)
# ---------------------------------------------

# ---------------- INDICADORES ----------------

    def _get_indicadores(self) -> dict:
        try:
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

            collection = self.database['indicadores']
            indicadores_dict = collection.find()

            if indicadores_dict is None:
                return indicadores

            for indicador in indicadores_dict:
                indicadores[indicador['numero']] = {
                    'nombre': indicador['nombre'], # Nombre del indicador
                    'unidad': indicador['unidad'], # Unidades del indicador
                    'categoria': indicador['categoria'], # Categoría del indicador
                    'fuente': indicador['fuente'], # URL de donde se puede encontrar más información del indicador
                    'propio': None, # El indicador es propio de la empresa (SI/NO)
                    'mide': None, # La empresa mide (SI,NO,NS/NR) el indicador
                    'dimensiones': {
                        'Granularidad': None, # Respuesta para la dimensión 'Granularidad'
                        'Frecuencia': None, # Respuesta para la dimensión 'Frecuencia'
                        'Comparabilidad': None, # Respuesta para la dimensión 'Comparabilidad'
                        'Fuente': None, # Respuesta para la dimensión 'Fuente'
                        'Tipo': None, # Respuesta para la dimensión 'Tipo'
                        'SBT': None, # Respuesta para la dimensión 'SBT'
                        'Validación Externa': None, # Respuesta para la dimensión 'Validación Externa'
                    }
                }

            return indicadores

        except Exception as e:
            print(e)

    
    def get_indicadores_usuario(self) -> dict:
        try:
            indicadores = self._get_indicadores()
            # user = os.environ.get("USERNAME")
            user = 'daniel'
            collection = self.database['usuarios']
            indicadores_dict = collection.find_one({"usuario": user}, {'indicadores':1,"_id": 0})

            if indicadores_dict is not None:
                for indc in indicadores_dict['indicadores']:
                    if indc['propio'] is None:
                        indicadores[indc['numero']]['propio'] = indc['propio']
                        indicadores[indc['numero']]['mide'] = indc['mide']
                        indicadores[indc['numero']]['dimensiones'] = indc['dimensiones']

            return indicadores  # Return the user document if found, None otherwise

        except Exception as e:
            print(e)

    def get_indicadores_df(self):
        try:
            df_indicadores = pd.DataFrame()
            indicadores_dict = self.get_indicadores_usuario()
            for key in indicadores_dict:
                if indicadores_dict[key]['mide'] is not None:
                    indicador = indicadores_dict[key]
                    dimensiones = indicadores_dict[key]['dimensiones']
                    data = {
                        'numero': key,
                        'nombre': indicador['nombre'],
                        'propio': indicador['propio'],
                        'mide': indicador['mide'],
                        'categoria': indicador['categoria'],
                        'Granularidad': dimensiones['Granularidad'],
                        'Frecuencia': dimensiones['Frecuencia'],
                        'Comparabilidad': dimensiones['Comparabilidad'],
                        'Fuente': dimensiones['Fuente'],
                        'Tipo': dimensiones['Tipo'],
                        'SBT': dimensiones['SBT'],
                    }

                    df_temp = pd.DataFrame(data,index=[0])
                    df_indicadores = pd.concat([df_indicadores, df_temp], ignore_index=False)

            return df_indicadores

        except Exception as e:
            print(e)    
        

    def set_indicadores(self, indicadores):
        try:
            usuario = os.environ.get("USERNAME")
            usuario = 'daniel'
            
            collection = self.database['usuarios']

            document_to_update = {"usuario": usuario}

            new_respuestas = {"$set" : {"indicadores": indicadores}}

            result = collection.update_one(document_to_update, new_respuestas)
            return True

        except Exception as e:
            print(e)

# ----------------------------------------------------------------------------------

# ---------------- INDUSTRIAS, SECTORES, DEPARTAMENTOS & MUNICIPIOS ----------------
    
    def get_departamentos_municipios(self) -> dict:
        try:
            collection = self.database['depo_muni']
            dict_depo_muni = collection.find()

            depo_muni = {}

            # depo_muni = {
            #     'departamento': ['municipios']
            # }

            for elemento in dict_depo_muni:
                depo_muni[elemento['departamento']] = elemento['municipios']
            
            return depo_muni

        except Exception as e:
            print(e)
    
    def get_departamentos_usuario(self) -> dict:
        try:
            user = os.environ.get("USERNAME")
            collection = self.database['usuarios']
            departamentos_dict = collection.find_one({"usuario": user}, {'departamentos':1,"_id": 0})
        
            return departamentos_dict  # Return the user document if found, None otherwise

        except Exception as e:
            print(e)

    def get_municipios_usuario(self) -> dict:
        try:
            user = os.environ.get("USERNAME")
            collection = self.database['usuarios']
            municipios_dict = collection.find_one({"usuario": user}, {'municipios':1,"_id": 0})
        
            return municipios_dict  # Return the user document if found, None otherwise

        except Exception as e:
            print(e)

    def update_departamentos_usuario(self, departamentos: list):
        try:
            
            usuario = os.environ.get("USERNAME")

            collection = self.database['usuarios']

            document_to_update = {"usuario": usuario}

            new_respuestas = {"$set" : {"departamentos": departamentos}}

            result = collection.update_one(document_to_update, new_respuestas)
            return True

        except Exception as e:
            print(e)
    
    def update_municipios_usuario(self, municipios: list):
        try:
            
            usuario = os.environ.get("USERNAME")

            collection = self.database['usuarios']

            document_to_update = {"usuario": usuario}

            new_respuestas = {"$set" : {"municipios": municipios}}

            result = collection.update_one(document_to_update, new_respuestas)
            return True

        except Exception as e:
            print(e)
    
    def get_sectores_industrias(self) -> dict:
        try:
            collection = self.database['sectores_industrias']
            dict_sectores_industrias = collection.find()

            sectores_industrias = {}

            for elemento in dict_sectores_industrias:
                sectores_industrias[elemento['sector']] = elemento['industrias']
            
            return sectores_industrias

        except Exception as e:
            print(e)

    def get_sector_usuario(self) -> dict:
        try:
            user = os.environ.get("USERNAME")
            collection = self.database['usuarios']
            sector_dict = collection.find_one({"usuario": user}, {'sector':1,"_id": 0})
        
            return sector_dict  # Return the user document if found, None otherwise

        except Exception as e:
            print(e)

    def get_industria_usuario(self) -> dict:
        try:
            user = os.environ.get("USERNAME")
            collection = self.database['usuarios']
            industria_dict = collection.find_one({"usuario": user}, {'industria':1,"_id": 0})
        
            return industria_dict  # Return the user document if found, None otherwise

        except Exception as e:
            print(e)

    def update_sector_usuario(self, sector: str):
        try:
            
            usuario = os.environ.get("USERNAME")

            collection = self.database['usuarios']

            document_to_update = {"usuario": usuario}

            new_respuestas = {"$set" : {"sector": sector}}

            result = collection.update_one(document_to_update, new_respuestas)
            return True

        except Exception as e:
            print(e)
    
    def update_industria_usuario(self, industria: str):
        try:
            
            usuario = os.environ.get("USERNAME")

            collection = self.database['usuarios']

            document_to_update = {"usuario": usuario}

            new_respuestas = {"$set" : {"industria": industria}}

            result = collection.update_one(document_to_update, new_respuestas)
            return True

        except Exception as e:
            print(e)

# -----------------------------------------------------------------------------------

