import pandas as pd
from collections import Counter
import re

def create_users_csv(user_payloads):
    rows = []
    for payload in user_payloads:
        legacy_data = payload.get('legacy', {})
        followers_count = legacy_data.get('followers_count', 0)
        friends_count = legacy_data.get('friends_count', 0)
        description = legacy_data.get('description', '')
        urls = [url['expanded_url'] for url in legacy_data.get('entities', {}).get('description', {}).get('urls', [])]
        row = {
            'id': payload.get('rest_id', ''),
            'name': legacy_data.get('name', ''),
            'screen_name': legacy_data.get('screen_name', ''),
            'statuses_count': legacy_data.get('statuses_count', 0),
            'followers_count': followers_count,
            'friends_count': friends_count,
            'favourites_count': legacy_data.get('favourites_count', 0),
            'listed_count': legacy_data.get('listed_count', 0),
            'default_profile': legacy_data.get('default_profile', False),
            'default_profile_image': legacy_data.get('default_profile_image', False),
            'location': legacy_data.get('location', ''),
            'description': description,
            'description_has_url': bool(urls),
            'description_url': ','.join(urls) if urls else '',
            'followers_to_following_ratio': followers_count / friends_count if friends_count != 0 else 0,
            'verified_type': legacy_data.get('verified_type', ''),
            'verified': legacy_data.get('verified', False),
            'is_blue_verified': payload.get('is_blue_verified', False),
            'has_graduated_access': payload.get('has_graduated_access', False),
            'can_dm': legacy_data.get('can_dm', False),
            'media_count': legacy_data.get('media_count', 0),
            'has_custom_timelines': legacy_data.get('has_custom_timelines', False),
            'has_verification_info': payload.get('verification_info', ''),
            'possibly_sensitive': legacy_data.get('possibly_sensitive', False),
        }

        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv('users.csv', index=False)


def create_tweets_csv(tweets_payloads):
    rows = []
    for payload in tweets_payloads:
        text = payload.get('text', '')
        row = {
            'tweet_id': payload.get('id_str', ''),
            'user_id': payload.get('user', {}).get('id_str', ''),
            'text': text,
            'created_at': payload.get('created_at', ''),
            'retweet_count': payload.get('retweet_count', 0),
            'favorite_count': payload.get('favorite_count', 0),
            'in_reply_to_status_id_str': payload.get('in_reply_to_status_id_str', ''),
            'in_reply_to_user_id_str': payload.get('in_reply_to_user_id_str', ''),
            'hashtags': ','.join([tag['text'] for tag in payload.get('entities', {}).get('hashtags', [])]),
            'user_mentions': ','.join([mention['id_str'] for mention in payload.get('entities', {}).get('user_mentions', [])]),
            'urls': ','.join([url['expanded_url'] for url in payload.get('entities', {}).get('urls', [])]),
            'sentiment': 1 if 'good' in text else (-1 if 'bad' in text else 0),
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv('tweets.csv', sep='\t', index=False)

def update_users_csv():
    users_df = pd.read_csv('users.csv')
    tweets_df = pd.read_csv('tweets.csv', sep='\t')
    users_df['response_count'] = 0
    users_df['most_responded_user'] = ''
    users_df['retweet_ratio'] = 0.0
    users_df['engagement_rate'] = 0.0
    users_df['top_words'] = ''
    for index, user_row in users_df.iterrows():
        user_id = user_row['id']
        user_tweets = tweets_df[tweets_df['user_id'] == user_id]
        response_count = user_tweets['in_reply_to_status_id_str'].count()
        most_responded_user = user_tweets['in_reply_to_user_id_str'].mode().iloc[0] if not user_tweets['in_reply_to_user_id_str'].mode().empty else ''
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
        
    users_df.to_csv('users_updated.csv', index=False)

def calculate_additional_metrics():
    # Leer el archivo CSV existente de tweets
    tweets_df = pd.read_csv('tweets.csv', sep='\t')
    
    # Inicializar nuevas columnas en el DataFrame de usuarios
    users_df = pd.read_csv('users_updated.csv')
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
    users_df.to_csv('users_final.csv', index=False)
