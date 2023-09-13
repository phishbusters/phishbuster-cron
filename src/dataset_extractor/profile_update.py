import pandas as pd
import re

from time import sleep
from ..lib_tweeterpy.scrap_tweeterpy import TwitterDataCollector
from .main import scrape_tweets
from collections import Counter
from ..utils.image_comparision import image_comparison
from .sentiment_analysis import analyze_sentiment
from ..utils.levenstein import levenshtein_distance
from .extractor import create_users_csv, create_tweets_csv, update_users_csv, calculate_additional_metrics, calculate_and_update_user_features, update_with_manual_classifications
from .data_classes.twitter_user import TwitterUser


def scrape_user_data(collector, screen_name):
    user = None
    try:
        user_data = collector.get_user_info_by_username(screen_name)
        user = TwitterUser.from_payload(user_data)
    except Exception as e:
        print(e)
        pass

    return user


def update_profiles():
    collector = TwitterDataCollector()
    users_df = pd.read_csv('users_final.csv', sep='\t')
    print("Updating user profiles...")

    try:
        for _, user_row in users_df.iterrows():
            screen_name = user_row['screen_name']
            user = scrape_user_data(collector, screen_name)
            create_users_csv([user])
            tweets_data = scrape_tweets(collector, [user],
                                        with_replies=False,
                                        total_per_run=30)
            create_tweets_csv(tweets_data)
            update_users_csv()
            calculate_additional_metrics()
            calculate_and_update_user_features()
            sleep(20)
    except Exception as e:
        print(e)
        pass

    print("All user profiles and tweets have been updated.")


if __name__ == "__main__":
    # update_profiles()
    update_with_manual_classifications()
