import os
from pymongo import MongoClient
from ..utils.levenstein import normalized_levenshtein

def connect_to_mongodb():
    try:

        # Obtener la dirección IP y el nombre de la base de datos desde las variables de entorno

        db_ip = os.getenv('DB_IP')
        db_name = os.getenv('DB_NAME')
        db_port = os.getenv('DB_PORT')
        db_user = os.getenv('DB_USERNAME')
        db_password = os.getenv('DB_PASSWORD')

        print(f"Conectando a MongoDB en {db_ip}:{db_port}...")
        client = MongoClient(f"mongodb://{db_user}:{db_password}@{db_ip}:{int(db_port)}/")
        db = client[db_name]
        print("Conexión exitosa")
        return db
    except Exception as e:
        print(f"Error al conectar con MongoDB: {e}")
        return None

# Función para buscar el usuario de la compañía más cercano en MongoDB
def find_closest_company_user(profile_name, collection):
    min_distance = 0.8
    closest_user = None
    for user in collection.find({"company.companyName": {"$exists": True}}):
        company_name = user['company']['companyName'].lower()
        profile_name_lower = profile_name.lower()
        if company_name in profile_name_lower:
            print('Found exact match:', company_name, 'in', profile_name_lower)
            return user
        
        dist = normalized_levenshtein(profile_name_lower, company_name.lower())
        print('Comparing', profile_name, 'with', company_name.lower(), 'distance:', dist)
        if dist < min_distance:
            print('Found new closest user:', company_name)
            min_distance = dist
            closest_user = user
    return closest_user

# Función para buscar activos digitales en MongoDB
def find_digital_assets(companyFromDB, collection):
    asset_ids = companyFromDB.get('company', {}).get('digitalAssets', [])
    assets = []
    for asset_id in asset_ids:
        asset = collection.find_one({"_id": asset_id})
        if asset:
            assets.append(asset)
    return assets


def check_social_network_url_in_assets(screen_name, collection):
    query = {"assetType": "SocialNetworkUrl", "assetContent": {"$regex": screen_name, "$options": "i"}}
    return collection.find_one(query) is not None