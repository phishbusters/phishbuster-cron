from .data_classes.twitter_results import SearchResults, SearchUserItem
from .data_classes.twitter_twitt import TwitterTweet
from .extractor import create_users_csv, calculate_additional_metrics, create_tweets_csv, update_users_csv
from ..lib_tweeterpy.scrap_tweeterpy import TwitterDataCollector 
import nltk

def scrape_data(collector):
    search_payload = collector.search_users("Javier Milei", total=1)
    search_results = SearchResults.from_payload(search_payload)
    
    user_payloads = []
    for item in search_results.items:
        if isinstance(item, SearchUserItem):
            user_payloads.append(item.user)

    return user_payloads

def scrape_tweets(collector, user_payloads):
    try:
        nltk.data.find('tokenizers/punkt')
    except Exception as e:
        try:
            nltk.download('punkt')
        except Exception as e:
            print(f"No se pudo descargar el recurso nltk 'punkt': {e}")

    tweets_payloads = []
    for user in user_payloads:
        user_tweets_payload = collector.get_user_tweets(user.id, total=1)
        tweet_data = user_tweets_payload.get('data', [])
        for tweet in tweet_data:
            tweet_content = tweet.get('content', {}).get('itemContent', {}).get('tweet_results', {}).get('result', {})
            tweets_payloads.append(TwitterTweet.from_payload(tweet_content))

    return tweets_payloads

if __name__ == "__main__":
    collector = TwitterDataCollector(username="MiraFercho76833", password="Ferchu$$91")
    user_payloads = scrape_data(collector)

    # Crear y actualizar el CSV de usuarios
    create_users_csv(user_payloads)
    # Scrapear y guardar los tweets
    tweets_payloads = scrape_tweets(collector, user_payloads)
    create_tweets_csv(tweets_payloads)
    
    update_users_csv()
    # Calcular métricas adicionales
    calculate_additional_metrics()