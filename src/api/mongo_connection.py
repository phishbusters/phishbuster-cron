from dotenv import load_dotenv
import os
from pymongo import MongoClient
from ..utils.levenstein import levenshtein_distance

def connect_to_mongodb():
    try:

        # Obtener la dirección IP y el nombre de la base de datos desde las variables de entorno

        db_ip = os.getenv('DB_IP')
        db_name = os.getenv('DB_NAME')
        client = MongoClient(f"mongodb://{db_ip}:27017/")
        db = client[db_name]
        return db
    except Exception as e:
        print(f"Error al conectar con MongoDB: {e}")
        return None

db = connect_to_mongodb()
if db:
    print("Conexión establecida con éxito.")
else:
    print("No se pudo establecer la conexión.")

# Función para buscar el usuario de la compañía más cercano en MongoDB
def find_closest_company_user(screen_name, db, collection):
    min_distance = float('inf')
    closest_user = None
    for user in collection.find({"company.companyName": {"$exists": True}}):
        company_name = user['company']['companyName']
        dist = levenshtein_distance(screen_name, company_name)
        if dist < min_distance:
            min_distance = dist
            closest_user = user
    return closest_user

# Función para buscar activos digitales en MongoDB
def find_digital_assets(user, db, collection):
    asset_ids = user.get('company', {}).get('digitalAssets', [])
    assets = []
    for asset_id in asset_ids:
        asset = collection.find_one({"_id": asset_id})
        if asset:
            assets.append(asset)
    return assets
