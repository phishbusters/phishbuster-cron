import re
from time import sleep
from googletrans import Translator
from textblob import TextBlob
from requests.exceptions import HTTPError
import math

def analyze_sentiment(text):
    try:
        if text is None or text == '' or (isinstance(text, float) and math.isnan(text)):
            return 0

        # Eliminar URLs del texto
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        if text.strip() == '':
            return 0

        translator = Translator(service_urls=['translate.google.com'])
        translated = translator.translate(text, dest='en')
        if translated and translated.text:
            blob = TextBlob(translated.text)
            return blob.sentiment.polarity
        else:
            return 0
    except HTTPError as httpError:
        if httpError.response.status == 429:
            print("Rate limit exceeded, sleeping for 60 seconds")
            sleep(20)
            return analyze_sentiment(text)
        else:
            print("Sentiment analysis fail on ", text, " because: ", httpError)
            return 0
    except Exception as e:
        print("Sentiment analysis fail on ", text, " because: ", e)
        return 0
