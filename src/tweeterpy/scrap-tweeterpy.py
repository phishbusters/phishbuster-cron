from tweeterpy import TweeterPy

twitter = TweeterPy()
twitter.login("MiraFercho76833","Ferchu$$91")
print("Milei ->")
print(twitter.get_user_info(4020276615))
# print(twitter.get_user_id("jmilei"))
# print(twitter.get_user_data("jmilei"))

# print("\n \n Search ->")
# print(twitter.search(search_query="Javier Milei", search_filter="People", total=10))
