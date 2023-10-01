from flask import Flask, request, jsonify
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import os
import joblib

from .transformations import exec
from .mongo_connection import connect_to_mongodb, find_closest_company_user, find_digital_assets, check_social_network_url_in_assets
from ..dataset_extractor.data_classes.twitter_user import TwitterUser
from ..dataset_extractor.data_classes.twitter_twitt import TwitterTweet
from ..lib_tweeterpy.scrap_tweeterpy import TwitterDataCollector
from ..utils.image_comparision import image_similarity

app = Flask(__name__)
scaler = joblib.load('profile-model-scaler.pkl')
model = joblib.load('profile-detection-model.pkl')
db = None
twitter_collector = TwitterDataCollector()

def preprocess_profile(df_profile):
    df_profile = df_profile.copy()
    expected_columns_order = [
        'statuses_count', 'followers_count', 'friends_count',
        'favourites_count', 'listed_count', 'followers_to_following_ratio',
        'media_count', 'response_count', 'retweet_ratio', 'engagement_rate',
        'tweets_count', 'average_sentiment', 'hashtags_per_tweet',
        'mentions_per_tweet', 'duplicate_content_ratio', 'account_age',
        'tweet_frequency', 'average_activity_time', 'text_to_image_ratio',
        'default_profile', 'default_profile_image', 'verified',
        'is_blue_verified', 'can_dm', 'has_custom_timelines',
        'possibly_sensitive', 'verified_type', 'has_verification_info'
    ]

    columns_to_normalize = [
        'statuses_count', 'followers_count', 'friends_count', 
        'favourites_count', 'listed_count', 'media_count', 
        'response_count', 'tweets_count'
    ]

    # Ensure all expected columns are present, fill with -1 if not
    for col in columns_to_normalize:
        if col not in df_profile.columns:
            df_profile[col] = 0  # Set a default value
    
    # Apply the pre-fitted MinMax transformation
    df_profile[columns_to_normalize] = scaler.transform(df_profile[columns_to_normalize])
    categorical_columns = [
        'default_profile', 'default_profile_image', 
        'verified', 'is_blue_verified', 'can_dm', 
        'has_custom_timelines', 'possibly_sensitive', 
        'verified_type', 'has_verification_info'
    ]
    
    for col in categorical_columns:
        if col in df_profile.columns:
            df_profile[col] = df_profile[col].astype('category')
        else:
            df_profile[col] = pd.Series(0).astype('category')  # Set a default value

    numeric_columns = df_profile.select_dtypes(include=['float64']).columns
    df_profile[numeric_columns] = df_profile[numeric_columns].fillna(-1.0)
    bool_columns = df_profile.select_dtypes(include=['bool']).columns
    df_profile[bool_columns] = df_profile[bool_columns].astype(int)
    df_profile = df_profile[expected_columns_order]
    return df_profile

def make_prediction_with_confidence(model, df_profile):
    df_preprocessed = preprocess_profile(df_profile)
    prediction = model.predict(df_preprocessed)
    prediction_proba = model.predict_proba(df_preprocessed)
    confidence = prediction_proba[0][int(prediction[0])]
    return prediction, confidence

@app.route('/predict/profile', methods=['POST'])
def predict():
    screen_name = request.json['screen_name']
    if not screen_name:
        return jsonify({'error': 'screen_name is required'}), 400
    
    user_id = twitter_collector.get_user_id(screen_name)
    user_info = twitter_collector.get_user_info(user_id)
    user_info = TwitterUser.from_payload(user_info)
    tweets = twitter_collector.get_user_tweets(user_id, total=10)
    tweets_data = tweets.get('data', [])
    twitterTweets = []
    for tweet in tweets_data:
        tweet_content = tweet.get('content', {}).get(
                    'itemContent', {}).get('tweet_results',
                                           {}).get('result', {})
        twitterTweets.append(TwitterTweet.from_payload(tweet_content))

    closest_company = find_closest_company_user(user_info.name, db['users'])
    image_similarity_score = None
    is_real_active = check_social_network_url_in_assets(screen_name, db['digitalassets'])
    if is_real_active is True:
        prediction_time = datetime.now().isoformat()
        return jsonify({ 
            'prediction': [0.0], 
            'model_prediction_label': 'real',
            'confidence': 1.0,
            'combined_confidence': 1.0,
            'prediction_label': 'real',
            'prediction_time': prediction_time,
            'related_company': closest_company,
        })

    if closest_company is not None:
        digital_assets = find_digital_assets(closest_company, db['digitalassets'])
        image_assets = [asset for asset in digital_assets if asset['assetType'] == 'Image']
        for asset in image_assets:
            image_similarity_score = image_similarity(user_info.profile_image_url_https, asset['assetContent'])
            print('Image Similarity: ', image_similarity_score)
            if image_similarity_score > 0.3:
                break

    user_df = exec([user_info], twitterTweets)
    user_df.to_csv('received requests.csv', sep='\t')
    preprocessed_data = preprocess_profile(user_df)

    prediction, confidence = make_prediction_with_confidence(model, preprocessed_data)
    combined_confidence = confidence
    if image_similarity_score is not None:
        combined_confidence = (0.9 * confidence) + (0.1 * image_similarity_score)

    if combined_confidence > 0.6:
        prediction_label = "real"
    else:
        prediction_label = "fake"

    print("predicted: ", prediction, " with confidence: ", confidence)
    model_prediction_label = "fake" if prediction[0] == 1.0 else "real"
    prediction_time = datetime.now().isoformat()
    return jsonify({ 
        'prediction': prediction.tolist(), 
        'model_prediction_label': model_prediction_label,
        'confidence': confidence,
        'combined_confidence': combined_confidence,
        'prediction_label': prediction_label,
        'prediction_time': prediction_time,
        'related_company': closest_company,
    })

if __name__ == '__main__':
    # Especifica la ruta al archivo .env
    # dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env'))
    is_loaded = load_dotenv() 
    print(f"Dotenv loaded: {is_loaded}")
    db = connect_to_mongodb()
    app.run(host='0.0.0.0', debug=True)

