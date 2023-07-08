from twitter_api.api import TwitterAPI

def run_cron_job():
    api = TwitterAPI()
    tweets = api.search_tweets('python')
    # Implementa la lógica para almacenar los datos de los tweets
