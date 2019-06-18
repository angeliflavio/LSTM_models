# sentiment analysis using TextBlob

from textblob import TextBlob    


# sentiment analysis function to get article polarity, using TextBlob
def get_sentiment(text):
    blob=TextBlob(text)
    return(blob.polarity)