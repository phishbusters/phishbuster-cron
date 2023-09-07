import re
from googletrans import Translator
from textblob import TextBlob

def analyze_sentiment(text):
    if text is None or text == '':
        return 0

    # Verificar si el texto es una URL
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    www_pattern = re.compile(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    if url_pattern.match(text) or www_pattern.match(text):
        return 0

    translator = Translator(service_urls=['translate.google.com'])
    translated = translator.translate(text, dest='en')
    
    if translated and translated.text:
        blob = TextBlob(translated.text)
        return blob.sentiment.polarity
    else:
        return 0
