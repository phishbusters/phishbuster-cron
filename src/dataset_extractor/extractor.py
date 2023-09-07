import pandas as pd
from collections import Counter
from.sentiment_analysis import analyze_sentiment
import re

def create_users_csv(user_objects):
    try:
        df = pd.read_csv('users.csv', sep='\t')
    except FileNotFoundError:
        df = pd.DataFrame()

    rows = []
    for user in user_objects:
        row = {
            'id': user.id,
            'name': user.name,
            'screen_name': user.screen_name,
            'statuses_count': user.statuses_count,
            'followers_count': user.followers_count,
            'friends_count': user.friends_count,
            'favourites_count': user.favourites_count,
            'listed_count': user.listed_count,
            'default_profile': user.default_profile,
            'default_profile_image': user.default_profile_image,
            'location': user.location,
            'description': user.description,
            'description_has_url': user.description_has_url,
            'description_url': user.description_url,
            'followers_to_following_ratio': user.followers_to_following_ratio,
            'verified_type': user.verified_type,
            'verified': user.verified,
            'is_blue_verified': user.is_blue_verified,
            'has_graduated_access': user.has_graduated_access,
            'can_dm': user.can_dm,
            'media_count': user.media_count,
            'has_custom_timelines': user.has_custom_timelines,
            'has_verification_info': user.has_verification_info,
            'possibly_sensitive': user.possibly_sensitive
        }
        rows.append(row)

    new_df = pd.DataFrame(rows)
    df = pd.concat([df, new_df]).drop_duplicates(subset='id', keep='last').reset_index(drop=True)
    df.to_csv('users.csv', sep='\t', index=False)


def create_tweets_csv(tweet_objects):
    try:
        df = pd.read_csv('tweets.csv', sep='\t')
    except FileNotFoundError:
        df = pd.DataFrame()

    rows = []
    for tweet in tweet_objects:
        text = tweet.full_text
        sentiment = analyze_sentiment(text)
        row = {
            'tweet_id': tweet.rest_id,
            'user_id': tweet.user_id,
            'text': text,
            'created_at': tweet.created_at,
            'retweet_count': tweet.retweet_count,
            'favorite_count': tweet.favorite_count,
            'in_reply_to_status_id_str': tweet.in_reply_to_status_id_str,
            'hashtags': ','.join(tweet.hashtags),
            'user_mentions': ','.join(tweet.user_mentions),
            'urls': ','.join(tweet.urls),
            'sentiment': sentiment,
        }
        rows.append(row)

    new_df = pd.DataFrame(rows)
    df = pd.concat([df, new_df]).drop_duplicates(subset='tweet_id', keep='last').reset_index(drop=True)
    df.to_csv('tweets.csv', sep='\t', index=False)

def update_users_csv():
    try:
        users_df = pd.read_csv('users.csv', sep='\t')
        tweets_df = pd.read_csv('tweets.csv', sep='\t')
    except FileNotFoundError:
        return

    users_df['response_count'] = 0
    users_df['most_responded_user'] = ''
    users_df['retweet_ratio'] = 0.0
    users_df['engagement_rate'] = 0.0
    users_df['top_words'] = ''
    for index, user_row in users_df.iterrows():
        user_id = user_row['id']
        user_tweets = tweets_df[tweets_df['user_id'] == user_id]
        response_count = user_tweets['in_reply_to_status_id_str'].count()
        most_responded_user = user_tweets['in_reply_to_status_id_str'].mode().iloc[0] if not user_tweets['in_reply_to_status_id_str'].mode().empty else ''
        retweet_ratio = user_tweets['retweet_count'].sum() / len(user_tweets) if len(user_tweets) > 0 else 0
        total_engagement = user_tweets['retweet_count'].sum() + user_tweets['favorite_count'].sum()
        engagement_rate = total_engagement / len(user_tweets) if len(user_tweets) > 0 else 0
        all_texts = ' '.join(user_tweets['text'].dropna())
        words = re.findall(r'\w+', all_texts.lower())
        top_words = Counter(words).most_common(5)
        users_df.at[index, 'response_count'] = response_count
        users_df.at[index, 'most_responded_user'] = most_responded_user
        users_df.at[index, 'retweet_ratio'] = retweet_ratio
        users_df.at[index, 'engagement_rate'] = engagement_rate
        users_df.at[index, 'top_words'] = ', '.join([word for word, _ in top_words])
        
    users_df.to_csv('users_updated.csv', sep='\t', index=False)

def calculate_additional_metrics():
    try:
        tweets_df = pd.read_csv('tweets.csv', sep='\t')
    except FileNotFoundError:
        return
    
    # Inicializar nuevas columnas en el DataFrame de usuarios
    users_df = pd.read_csv('users_updated.csv', sep='\t')
    users_df['hashtags_per_tweet'] = 0.0
    users_df['mentions_per_tweet'] = 0.0
    users_df['duplicate_content_ratio'] = 0.0
    
    for index, user_row in users_df.iterrows():
        user_id = user_row['id']
        
        # Filtrar tweets de este usuario
        user_tweets = tweets_df[tweets_df['user_id'] == user_id]
        
        if len(user_tweets) == 0:
            continue
        
        # Calcular hashtags_per_tweet
        total_hashtags = user_tweets['hashtags'].apply(lambda x: len(str(x).split(',')) if pd.notna(x) else 0).sum()
        users_df.at[index, 'hashtags_per_tweet'] = total_hashtags / len(user_tweets)
        
        # Calcular mentions_per_tweet
        total_mentions = user_tweets['user_mentions'].apply(lambda x: len(str(x).split(',')) if pd.notna(x) else 0).sum()
        users_df.at[index, 'mentions_per_tweet'] = total_mentions / len(user_tweets)
        
        # Calcular duplicate_content_ratio
        unique_tweets = user_tweets['text'].nunique()
        users_df.at[index, 'duplicate_content_ratio'] = (len(user_tweets) - unique_tweets) / len(user_tweets) if len(user_tweets) > 0 else 0
    
    # Actualizar el archivo CSV de usuarios
    users_df.to_csv('users_final.csv', sep='\t', index=False)
