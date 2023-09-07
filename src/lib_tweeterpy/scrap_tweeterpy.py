from tweeterpy import TweeterPy

class TwitterDataCollector:
    def __init__(self, username=None, password=None):
        self.twitter = TweeterPy()
        self.logged_in = False
        if username and password:
            self.login(username, password)

    def login(self, username, password):
        self.twitter.login(username, password)
        self.logged_in = True
        self.twitter.save_session(session_name=username)

    def is_logged_in(self):
        return self.twitter.logged_in()

    def search_users(self, query, end_cursor=None, total=None):
        return self.twitter.search(search_query=query, end_cursor=end_cursor, total=total, search_filter="People")

    def get_user_info_by_id(self, user_id):
        return self.twitter.get_user_info(user_id)

    def get_user_info_by_username(self, username):
        return self.twitter.get_user_data(username)

    def get_multiple_users_info(self, user_ids):
        return self.twitter.get_multiple_users_data(user_ids)

    def get_user_tweets(self, user_id, with_replies=False, total=None, end_cursor=None):
        return self.twitter.get_user_tweets(user_id, with_replies=with_replies, end_cursor=end_cursor, total=total)

    def get_tweet_details(self, tweet_id, with_tweet_replies=False, total=None):
        return self.twitter.get_tweet(tweet_id, with_tweet_replies=with_tweet_replies, total=total)

    def get_friends(self, user_id, follower=False, following=False, mutual_follower=False, total=None):
        return self.twitter.get_friends(user_id, follower=follower, following=following, mutual_follower=mutual_follower, total=total)

# Uso de la clase
if __name__ == "__main__":
    # Iniciar sesión automáticamente al instanciar
    collector = TwitterDataCollector(username="your_username", password="your_password")

    # Verificar estado de inicio de sesión
    print("Logged in:", collector.is_logged_in())

    # Buscar usuarios
    users = collector.search_users("Javier Milei", total=10)
    print(users)

    # Obtener información de usuario por ID
    user_info = collector.get_user_info_by_id(4020276615)
    print(user_info)

    # Y así sucesivamente para los otros métodos
