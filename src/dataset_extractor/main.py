from .searched_database.processed_records import read_last_processed, update_last_processed
from .data_classes.twitter_results import SearchResults, SearchUserItem
from .data_classes.twitter_twitt import TwitterTweet
from .extractor import create_users_csv, calculate_additional_metrics, create_tweets_csv, update_users_csv, update_sentiment_in_tweets_csv
from ..lib_tweeterpy.scrap_tweeterpy import TwitterDataCollector
import nltk


def scrape_data(collector, search_query, total_per_run=100):
    try:
        last_result_index, _ = read_last_processed(search_query)
        search_payload = collector.search_users(search_query,
                                                end_cursor=last_result_index,
                                                total=total_per_run)
        search_results = SearchResults.from_payload(search_payload)
        user_payloads = []
        for item in search_results.items:
            if isinstance(item, SearchUserItem):
                user_payloads.append(item.user)

        if user_payloads:
            update_last_processed(search_query, search_results.cursor_endpoint,
                                None)
    except Exception as e:
        print(e)
        pass
    
    return user_payloads


def scrape_tweets(collector, user_payloads, search_query, total_per_run=100):
    _, last_tweet_cursor = read_last_processed(search_query)
    tweets_payloads = []

    try:
        for user in user_payloads:
            print("Buscando tweets de usuario: ", user.screen_name)
            user_tweets_payload = collector.get_user_tweets(
                user.id,
                end_cursor=last_tweet_cursor,
                with_replies=True,
                total=total_per_run)
            tweet_data = user_tweets_payload.get('data', [])
            cursor_endpoint = user_tweets_payload.get('cursor_endpoint', None)
            has_next_page = user_tweets_payload.get('has_next_page', False)
            for tweet in tweet_data:
                tweet_content = tweet.get('content', {}).get(
                    'itemContent', {}).get('tweet_results',
                                           {}).get('result', {})
                tweets_payloads.append(
                    TwitterTweet.from_payload(tweet_content))

            if has_next_page and cursor_endpoint:
                update_last_processed(search_query, None, cursor_endpoint)

    except Exception as e:
        print(e)
        pass

    return tweets_payloads


def exec_process(search_query, total_per_run=100):
    try:
        nltk.data.find('tokenizers/punkt')
    except Exception as e:
        try:
            nltk.download('punkt')
        except Exception as e:
            print(f"No se pudo descargar el recurso nltk 'punkt': {e}")

    print("Iniciando proceso de extracción de datos")    
    collector = TwitterDataCollector()
    print("Buscando datos de usuarios...")
    user_payloads = scrape_data(collector, search_query, total_per_run)
    print("Datos obtenidos", len(user_payloads))
    print("Creando CSV de usuarios...")
    create_users_csv(user_payloads)
    # tweets_limit_cap = int(total_per_run / 10)
    tweets_limit_cap = total_per_run
    print("Buscando tweets para: ", len(user_payloads), " usuarios...")
    tweets_payloads = scrape_tweets(
        collector, user_payloads, search_query,
        tweets_limit_cap if tweets_limit_cap > 0 else 1)
    print("Datos obtenidos", len(tweets_payloads))
    print("Creando CSV de tweets...")
    create_tweets_csv(tweets_payloads)
    print("Actualizando CSV de usuarios con datos de twitts...")
    update_users_csv()
    print("Calculando métricas adicionales de los usuarios con los twitts...")
    calculate_additional_metrics()
    print("Actualizando CSV de tweets con datos de sentimiento...")
    update_sentiment_in_tweets_csv()
    print("Proceso finalizado")
