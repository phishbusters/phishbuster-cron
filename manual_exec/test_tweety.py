
import sys
 
sys.path.insert(0, 'D:\\Projects\\phishbuster-cron')
from src.twitter_api.api import TwitterAPI
import pprint

def test_twitter_api():
    query = input("Please enter the search query for the tweets: ")
    api = TwitterAPI()
    # tweets = api.search_tweets(query)

    # for tweet in tweets:
    #     print(f'Tweet by @{tweet.user.screen_name}: {tweet.text}\n')
    #     pprint.pprint(tweet._json)
    #     print('\n---\n')

    clients = api.search_profiles(query)
    print(clients)
    for client in clients.data:
        pprint.pprint(client)
        print('\n---\n')

if __name__ == '__main__':
    test_twitter_api()
