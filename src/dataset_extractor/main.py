from extractor import create_users_csv, calculate_additional_metrics, create_tweets_csv, update_users_csv
import pandas as pd


def scrape_data():
    user_payloads = []
    tweets_payloads = []
    return user_payloads, tweets_payloads

if __name__ == "__main__":
    user_payloads, tweets_payloads = scrape_data()
    create_users_csv(user_payloads)
    create_tweets_csv(tweets_payloads)
    update_users_csv()
    calculate_additional_metrics()
