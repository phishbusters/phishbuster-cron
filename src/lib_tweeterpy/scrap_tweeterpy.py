import time
import pandas as pd
from tweeterpy import TweeterPy
from tweeterpy.util import RateLimitError
from requests.exceptions import HTTPError
from datetime import datetime

class TwitterDataCollector:
    loginDatabaseFile = "login_twitter.csv"

    def __init__(self, username=None, password=None):
        self.twitter = TweeterPy()
        self.logged_in = False
        self.current_account = 0
        if username is None and password is None:
            self.accounts = self._load_accounts_from_db()
            self.login_next_account()
        elif username is not None and password is not None:
            self.login(username, password)
        else:
            raise ValueError("Both username and password must be provided, or neither.")

    def _load_accounts_from_db(self):
        try:
            accounts_df = pd.read_csv(self.loginDatabaseFile, sep='\t')
        except FileNotFoundError:
            accounts_df = pd.DataFrame(columns=['username', 'password', 'lastLogin'])
            accounts_df.to_csv(self.loginDatabaseFile, sep='\t', index=False)

        return accounts_df

    def _add_or_update_account(self, username, password):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df = self.accounts
        if username in df['username'].values:
            df.loc[df['username'] == username, 'lastLogin'] = now
        else:
            new_row = {'username': username, 'password': password, 'lastLogin': now}
            df = df.append(new_row, ignore_index=True)
        
        df.to_csv(self.loginDatabaseFile, sep='\t', index=False)

    def _is_next_account_available(self):
        return self.current_account > len(self.accounts)

    def login_next_account(self):
        if self._is_next_account_available():
            raise Exception("No more accounts available for login.")
        
        account = self.accounts.iloc[self.current_account]
        print("logging in with account: ", account['username'])
        self.login(account['username'], account['password'])
        self.current_account += 1
        self._add_or_update_account(account['username'], account['password'])

    def login(self, username, password):
        self.twitter.login(username, password)
        self.logged_in = True
        self.twitter.save_session(session_name=username)
        self._add_or_update_account(username, password)

    def is_logged_in(self):
        return self.twitter.logged_in()

    def search_users(self, query, end_cursor=None, total=None):
        try:
            payload = self.twitter.search(search_query=query,
                                    end_cursor=end_cursor,
                                    total=total,
                                    search_filter="People")
            has_next_page = payload.get('has_next_page', False)
            api_rate_limit = payload.get('api_rate_limit', False)
            limit_exhausted = api_rate_limit.get("rate_limit_exhausted")
            if has_next_page and limit_exhausted:
                self.login_next_account()
                return self.search_users(query, end_cursor, total)

            return payload
        except HTTPError as e:
            if e.response.status == 429:
                time.sleep(60)
                return self.search_users(query, end_cursor, total)
            else:
                raise e
        except RateLimitError:
            self.login_next_account()
            return self.search_users(query, end_cursor, total)

    def get_user_info_by_id(self, user_id):
        return self.twitter.get_user_info(user_id)
    
    def get_user_info(self, user_id):
        return self.twitter.get_user_info(user_id)

    def get_user_id(self, screen_name):
        return self.twitter.get_user_id(screen_name)

    def get_user_info_by_username(self, username):
        try:
            return self.twitter.get_user_data(username)
        except HTTPError as e:
            if e.response.status == 429:
                time.sleep(60)
                return self.get_user_info_by_username(username)
            else:
                raise e
        except RateLimitError:
            self.login_next_account()
            return self.get_user_info_by_username(username)

    def get_multiple_users_info(self, user_ids):
        return self.twitter.get_multiple_users_data(user_ids)

    def get_user_tweets(self,
                        user_id,
                        with_replies=False,
                        total=None,
                        end_cursor=None):
        try:
            payload = self.twitter.get_user_tweets(user_id,
                                                with_replies=with_replies,
                                                end_cursor=end_cursor,
                                                total=total)
            has_next_page = payload.get('has_next_page', False)
            api_rate_limit = payload.get('api_rate_limit', False)
            limit_exhausted = api_rate_limit.get("rate_limit_exhausted")
            if has_next_page and limit_exhausted:
                self.login_next_account()
                return self.get_user_tweets(user_id, with_replies, total)

            return payload
        except HTTPError as e:
            if e.response.status == 429:
                time.sleep(60)
                return self.get_user_tweets(user_id, with_replies, total)
            else:
                raise e
        except RateLimitError:
            self.login_next_account()
            return self.get_user_tweets(user_id, with_replies, total)

    def get_tweet_details(self,
                          tweet_id,
                          with_tweet_replies=False,
                          total=None):
        return self.twitter.get_tweet(tweet_id,
                                      with_tweet_replies=with_tweet_replies,
                                      total=total)

    def get_friends(self,
                    user_id,
                    follower=False,
                    following=False,
                    mutual_follower=False,
                    total=None):
        return self.twitter.get_friends(user_id,
                                        follower=follower,
                                        following=following,
                                        mutual_follower=mutual_follower,
                                        total=total)


# Uso de la clase
if __name__ == "__main__":
    # Iniciar sesión automáticamente al instanciar
    collector = TwitterDataCollector(username="your_username",
                                     password="your_password")

    # Verificar estado de inicio de sesión
    print("Logged in:", collector.is_logged_in())

    # Buscar usuarios
    users = collector.search_users("Javier Milei", total=10)
    print(users)

    # Obtener información de usuario por ID
    user_info = collector.get_user_info_by_id(4020276615)
    print(user_info)

    # Y así sucesivamente para los otros métodos
