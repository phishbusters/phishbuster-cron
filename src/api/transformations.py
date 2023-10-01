import pandas as pd
import re

from collections import Counter
from .sentiment_analysis import analyze_sentiment

def exec(user, tweets):
    user_df = create_users_csv(user)
    tweets_df = create_tweets_csv(tweets)
    tweets_df = update_tweet_sentiments(tweets_df)
    user_df = update_users_csv(user_df, tweets_df)
    user_df = calculate_additional_metrics(user_df, tweets_df)
    user_df = calculate_and_update_user_features(user_df, tweets_df)

    return user_df

def create_users_csv(user_objects):
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
            'possibly_sensitive': user.possibly_sensitive,
            'profile_image_url_https': user.profile_image_url_https,
            'created_at': user.created_at,
        }
        rows.append(row)

    return pd.DataFrame(rows)


def create_tweets_csv(tweet_objects):
    rows = []
    for tweet in tweet_objects:
        text = tweet.full_text
        # sentiment = analyze_sentiment(text)
        row = {
            'tweet_id': str(tweet.rest_id),
            'user_id': str(tweet.user_id),
            'text': text,
            'created_at': tweet.created_at,
            'retweet_count': tweet.retweet_count,
            'favorite_count': tweet.favorite_count,
            'in_reply_to_status_id_str': tweet.in_reply_to_status_id_str,
            'hashtags': ','.join(tweet.hashtags),
            'user_mentions': ','.join(tweet.user_mentions),
            'urls': ','.join(tweet.urls),
            'sentiment': '',
            'has_image': tweet.has_image,
        }
        rows.append(row)

    new_df = pd.DataFrame(rows)
    return new_df


def update_users_csv(users_df, tweets_df):
    tweets_df = tweets_df.dropna(subset=['tweet_id', 'user_id'])
    users_df['response_count'] = 0
    users_df['most_responded_user'] = ''
    users_df['retweet_ratio'] = 0.0
    users_df['engagement_rate'] = 0.0
    users_df['top_words'] = ''

    for index, user_row in users_df.iterrows():
        user_id = user_row['id']
        user_tweets = tweets_df[tweets_df['user_id'] == user_id]

        response_count = user_tweets['in_reply_to_status_id_str'].count()
        most_responded_user = user_tweets['in_reply_to_status_id_str'].mode(
        ).iloc[0] if not user_tweets['in_reply_to_status_id_str'].mode(
        ).empty else ''
        retweet_ratio = user_tweets['retweet_count'].sum() / len(
            user_tweets) if len(user_tweets) > 0 else 0
        total_engagement = user_tweets['retweet_count'].sum(
        ) + user_tweets['favorite_count'].sum()
        engagement_rate = total_engagement / len(user_tweets) if len(
            user_tweets) > 0 else 0
        average_sentiment = user_tweets['sentiment'].mean() if len(
            user_tweets) > 0 else 0
        all_texts = ' '.join(user_tweets['text'].dropna())
        words = re.findall(r'\w+', all_texts.lower())
        top_words = Counter(words).most_common(5)
        tweets_count = int(len(user_tweets))
        users_df.at[index, 'tweets_count'] = tweets_count
        users_df.at[index, 'response_count'] = response_count
        users_df.at[index, 'most_responded_user'] = most_responded_user
        users_df.at[index, 'retweet_ratio'] = retweet_ratio
        users_df.at[index, 'engagement_rate'] = engagement_rate
        users_df.at[index,
                    'top_words'] = ', '.join([word for word, _ in top_words])
        users_df.at[index, 'average_sentiment'] = average_sentiment

    return users_df


def calculate_additional_metrics(users_df, tweets_df):
    users_df['hashtags_per_tweet'] = 0.0
    users_df['mentions_per_tweet'] = 0.0
    users_df['duplicate_content_ratio'] = 0.0
    if 'is_fake' not in users_df.columns:
        users_df['is_fake'] = None

    for index, user_row in users_df.iterrows():
        user_id = user_row['id']

        # Filtrar tweets de este usuario
        user_tweets = tweets_df[tweets_df['user_id'] == user_id]

        if len(user_tweets) == 0:
            continue

        # Calcular hashtags_per_tweet
        total_hashtags = user_tweets['hashtags'].apply(
            lambda x: len(str(x).split(',')) if pd.notna(x) else 0).sum()
        users_df.at[index,
                    'hashtags_per_tweet'] = total_hashtags / len(user_tweets)

        # Calcular mentions_per_tweet
        total_mentions = user_tweets['user_mentions'].apply(
            lambda x: len(str(x).split(',')) if pd.notna(x) else 0).sum()
        users_df.at[index,
                    'mentions_per_tweet'] = total_mentions / len(user_tweets)

        # Calcular duplicate_content_ratio
        unique_tweets = user_tweets['text'].nunique()
        users_df.at[index, 'duplicate_content_ratio'] = (
            len(user_tweets) -
            unique_tweets) / len(user_tweets) if len(user_tweets) > 0 else 0

    return users_df


def calculate_and_update_user_features(users_df, tweets_df):
    for col in [
            'account_age', 'tweet_frequency', 'average_activity_time',
            'text_to_image_ratio'
    ]:
        if col not in users_df.columns:
            users_df[col] = 0 if col != 'average_activity_time' else 0

    users_df['tweet_frequency'] = users_df['tweet_frequency'].astype('float64')
    for index, row in users_df.iterrows():
        user_id = row['id']
        user_tweets = tweets_df[tweets_df['user_id'] == user_id].copy()

        if pd.notna(row['created_at']):
            account_created_at = pd.to_datetime(row['created_at'],
                                                errors='coerce')
            if account_created_at.tzinfo is not None:
                account_created_at = account_created_at.tz_convert(None)

            current_time = pd.Timestamp.now()
            if current_time.tzinfo is not None:
                current_time = current_time.tz_convert(None)

            account_age = (current_time - account_created_at).days
            tweet_frequency = row[
                'statuses_count'] / account_age if account_age != 0 else 0
        else:
            account_age = 0.0
            tweet_frequency = 0.0

        if not user_tweets.empty:
            user_tweets['created_at'] = pd.to_datetime(
                user_tweets['created_at'],
                format='%a %b %d %H:%M:%S %z %Y',
                errors='coerce')
            user_tweets.dropna(subset=['created_at'], inplace=True)
            if user_tweets['created_at'].dt.tz is not None:
                user_tweets['created_at'] = user_tweets[
                    'created_at'].dt.tz_convert(None)

            user_tweets['hour'] = user_tweets['created_at'].dt.hour
            average_activity_time = user_tweets['hour'].mean()

            total_tweets = len(user_tweets)
            image_tweets = len(user_tweets[user_tweets['has_image'] == True])
            text_tweets = total_tweets - image_tweets
            text_to_image_ratio = text_tweets / total_tweets if total_tweets > 0 else None
        else:
            average_activity_time = None
            text_to_image_ratio = None

        users_df.at[index, 'account_age'] = account_age
        users_df.at[index, 'tweet_frequency'] = tweet_frequency
        users_df.at[index, 'average_activity_time'] = average_activity_time
        users_df.at[index, 'text_to_image_ratio'] = text_to_image_ratio

    return users_df


def update_tweet_sentiments(tweets_df):
    filtered_df = tweets_df[(tweets_df['sentiment'].isna()) |
                            (tweets_df['sentiment'] == '') |
                            (tweets_df['sentiment'] == 0)]
    for index, row in filtered_df.iterrows():
        text = row['text']
        sentiment = analyze_sentiment(text)
        tweets_df.loc[index, 'sentiment'] = sentiment

    tweets_df['tweet_id'] = tweets_df['tweet_id'].astype(str)
    tweets_df['user_id'] = tweets_df['user_id'].astype(str)
    return tweets_df

