from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import os
from classes.pregunta import Pregunta

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
# --------------------------------------------

# ---------------- RESPUESTAS ----------------

    def get_respuestas(self) -> dict:
        try:
            user = os.environ.get("USERNAME")
            collection = self.database['usuarios']
            usu_dict = collection.find_one({"usuario": user}, {'respuestas':1,"_id": 0})

            return usu_dict  # Return the user document if found, None otherwise

        except Exception as e:
            print(e)

    def update_respuestas(self, respuestas: dict) -> bool:
        try:
            usuario = os.environ.get("USERNAME")

            collection = self.database['usuarios']

            document_to_update = {"usuario": usuario}

            new_respuestas = {"$set" : {"respuestas": respuestas}}
            
            result = collection.update_one(document_to_update, new_respuestas)

            return True

        except Exception as e:
            print(e)
# -----------------------------------------
