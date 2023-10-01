from flask import Flask, request, jsonify
import pandas as pd
import joblib

from .transformations import exec
from .mongo_connection import connect_to_mongodb, find_closest_company_user, find_digital_assets
from ..dataset_extractor.data_classes.twitter_user import TwitterUser
from ..dataset_extractor.data_classes.twitter_twitt import TwitterTweet
from ..lib_tweeterpy.scrap_tweeterpy import TwitterDataCollector
from ..utils.levenstein import levenshtein_distance
from ..utils.image_comparision import image_comparison

app = Flask(__name__)
scaler = joblib.load('profile-model-scaler.pkl')
model = joblib.load('profile-detection-model.pkl')
db = None

def preprocess_profile(df_profile):
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

# Función para hacer una predicción con confianza
def make_prediction_with_confidence(model, df_profile):
    df_preprocessed = preprocess_profile(df_profile)
    prediction = model.predict(df_preprocessed)
    prediction_proba = model.predict_proba(df_preprocessed)
    confidence = prediction_proba[0][prediction[0]]  # Asumiendo que solo hay una instancia
    return prediction, confidence

@app.route('/predict/profile', methods=['POST'])
def predict():
    screen_name = request.json['screen_name']
    if not screen_name:
        return jsonify({'error': 'screen_name is required'}), 400

    # # Buscar el usuario y los activos digitales más cercanos
    # closest_user = find_closest_company_user(screen_name, db, db['User'])
    # digital_assets = find_digital_assets(closest_user, db, db['DigitalAsset'])
    
    # # Comparaciones
    # leven_distance_with_company = levenshtein_distance(screen_name, closest_user['company']['companyName'])
    # image_similarity_score = image_comparison(user_info.profile_image, closest_user['company']['profile_image'])

    # Inicializa tu clase TwitterDataCollector
    twitter_collector = TwitterDataCollector()
    user_id = twitter_collector.get_user_id(screen_name)
    user_info = twitter_collector.get_user_info(user_id)
    user_info = TwitterUser.from_payload(user_info)
    tweets = twitter_collector.get_user_tweets(user_id, total=50)
    tweets_data = tweets.get('data', [])
    twitterTweets = []
    for tweet in tweets_data:
        tweet_content = tweet.get('content', {}).get(
                    'itemContent', {}).get('tweet_results',
                                           {}).get('result', {})
        twitterTweets.append(TwitterTweet.from_payload(tweet_content))

    user_df = exec([user_info], twitterTweets)
    user_df.to_csv('received requests.csv', sep='\t')
    preprocessed_data = preprocess_profile(user_df)

    print(preprocessed_data.to_dict(orient='list'))
    prediction, confidence = make_prediction_with_confidence(model, user_df)
    return jsonify({ 'prediction': prediction.tolist(), 'confidence': confidence })

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    db = connect_to_mongodb()

