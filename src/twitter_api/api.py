import tweepy
from .constants import API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

class TwitterAPI:
    def __init__(self):
        auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth)

    def search_tweets(self, query):
        return self.api.search_tweets(query)
    
    def search_profiles(self, query):
        return self.api.search_users(query)