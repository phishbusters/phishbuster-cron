from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from dotenv import load_dotenv
from ..api.mongo_connection import connect_to_mongodb
from ..lib_tweeterpy.scrap_tweeterpy import TwitterDataCollector
from ..dataset_extractor.data_classes.twitter_results import SearchResults

import os
import requests

# Cargar variables de entorno
load_dotenv()

flask_api_url = os.getenv('PROFILE_ANALYSIS_API_URL')
db = connect_to_mongodb()
collector = TwitterDataCollector()

DB_USER_COLLECTION = 'users'
DB_COMPLAINTS_COLLECTION = 'complaints'
DB_ANALYZED_PROFILES_COLLECTION = 'analyzedprofiles'
PHISHING_STATS_COLLECTION = 'phishingstats'

def get_stat_by_date(date):
    phishing_stats = db[PHISHING_STATS_COLLECTION]
    start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0)
    end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)

    existing_stat = phishing_stats.find_one({
        'date': {
            '$gte': start_of_day,
            '$lte': end_of_day
        }
    })

    return existing_stat


def create_or_update_stat(date, field_to_update):
    phishing_stats = db[PHISHING_STATS_COLLECTION]
    existing_stat = get_stat_by_date(date)

    if existing_stat:
        print('Updating existing stat')
        phishing_stats.update_one(
            {'_id': existing_stat['_id']},
            {'$inc': {field_to_update: 1}}
        )
        return phishing_stats.find_one({'_id': existing_stat['_id']})
    else:
        print('Creating new stat')
        new_stat = {
            'date': date,
            'phishingChatsDetected': 0,
            'fakeProfilesDetected': 0,
            'complaintsClosed': 0,
            'complaintsCreated': 0,
            'complaintsInProgress': 0,
            field_to_update: 1
        }
        phishing_stats.insert_one(new_stat)
        return new_stat

def start_cron_process():
    print('Starting cron process...')
    users = db[DB_USER_COLLECTION].find({})
    for user in users:
        user_id = user.get('_id', '')
        if not user_id or user_id == '':
            continue

        company_name = user.get("company", {}).get("companyName", "")
        if not company_name or company_name == '':
            print(f'No company name found for {user["_id"]}, skipping...')
            continue

        stored_cursor_endpoint = user.get('cursor_endpoint', None)
        print(
            f'Processing company {company_name}')
        similar_profiles = collector.search_users(
            company_name, total=10,  end_cursor=stored_cursor_endpoint)
        search_results = SearchResults.from_payload(similar_profiles)
        new_cursor_endpoint = search_results.cursor_endpoint
        for item in search_results.items:
            twitter_profile = item.user
            screen_name = twitter_profile.screen_name
            print(f'Processing profile {screen_name}')
            response = requests.post(flask_api_url, json={
                                     "screen_name": screen_name})
            if response.status_code == 200:
                print(f'Profile {screen_name} processed successfully')
                result = response.json()
                if result['prediction_label'] == 'fake':
                    model_related_company = result['related_company']
                    print(
                        f'Profile {screen_name} is fake, and its related company is: {model_related_company}')
                    if model_related_company != '' and model_related_company == company_name:
                        complaint_data = {
                            "status": "Created",
                            "actionRequired": False,
                            "createdAt": datetime.utcnow(),
                            "updatedAt": datetime.utcnow()
                        }
                        complaint_id = db[DB_COMPLAINTS_COLLECTION].insert_one(
                            complaint_data).inserted_id
                        print(f'Complaint created with id {complaint_id}')
                        analyzed_profile_data = {
                            "profileId": screen_name,
                            "confidenceLevel": result['confidence'],
                            "analysisDate": datetime.utcnow(),
                            "relatedCompanyName": company_name,
                            "complaintId": complaint_id,
                            "detectedBy": "system",
                            "userInteractions": [],
                            "markAsFalsePositive": False,
                            "createdAt": datetime.utcnow()
                        }

                        try:
                            db[DB_ANALYZED_PROFILES_COLLECTION].insert_one(
                                analyzed_profile_data)
                            print("Updating phishing stats...")
                            create_or_update_stat(datetime.now(), 'fakeProfilesDetected')
                            print("Updating complaints stats...")
                            create_or_update_stat(datetime.now(), 'complaintsCreated')
                        except DuplicateKeyError:
                            print(
                                f"Duplicate profileId found for {screen_name}, skipping...")
                        print(
                            f'Analyzed profile created with id {screen_name}')
                    else:
                        print(
                            f'Profile {screen_name} is not related to company {company_name}, skipping...')
                else:
                    print(
                        f'Profile {screen_name} is real, skipping...')           
            else:
                print(
                    f'Profile {screen_name} could not be processed, skipping...')

        print(
            f'Updating cursor endpoint for company {company_name}')
        db[DB_USER_COLLECTION].update_one(
            {'_id': user_id}, {'$set': {'cursor_endpoint': new_cursor_endpoint}})


if __name__ == '__main__':
    start_cron_process()
