from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import os

class MongoDB:
    
    DATABASE = 'web_app'
    
    def __init__(self):
        user = os.environ.get("DB_USER")
        password = os.environ.get("DB_PASS")
        
        uri = f"mongodb+srv://{user}:{password}@clusterpdg.psjdd0v.mongodb.net/?retryWrites=true&w=majority&appName=ClusterPDG"
        
        self.client = MongoClient(uri, server_api=ServerApi('1'), tls=True)
        self.database = self.client[self.DATABASE]
        
    
    def iniciar_sesion(self,usuario:str, contrasena:str) -> bool:
        try:
            usr = self.get_usuario(usuario=usuario)
            if usr is None: 
                return False
            
            if usr['contrasena'] != contrasena:
                return False
            
            return True
            
        except Exception as e:
            print(e)
    
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
                    'contrasena': contrasena
                }

                # Inserting the student data into the 'students' collection and obtaining the inserted ID
                collection.insert_one(data)
                
                return f'{usuario} creado con éxito'
            
            return f"El usuario '{usuario}' ya existe"
        
        except Exception as e:
            print(e)
