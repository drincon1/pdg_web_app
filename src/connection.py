
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os


user = os.environ.get("DB_USER")
password = os.environ.get("DB_PASS")

uri = f"mongodb+srv://{user}:{password}@clusterpdg.psjdd0v.mongodb.net/?retryWrites=true&w=majority&appName=ClusterPDG"


# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'), tls=True)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
