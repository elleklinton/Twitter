import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob


def clean_tweet(tweet):
    '''
    Utility function to clean tweet text by removing links, special characters
    using simple regex statements.
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\ / \ / \S+)", " ", tweet).split())

def get_tweet_sentiment(tweet):
    '''
    Utility function to classify sentiment of passed tweet
    using textblob's sentiment method
    '''
    # create TextBlob object of passed tweet text
    analysis = TextBlob(clean_tweet(tweet))
    # set sentiment
    if analysis.sentiment.polarity > 0:
        return 'positive', analysis.sentiment.polarity, analysis.sentiment.subjectivity
    elif analysis.sentiment.polarity == 0:
        return 'neutral', analysis.sentiment.polarity, analysis.sentiment.subjectivity
    else:
        return 'negative', analysis.sentiment.polarity, analysis.sentiment.subjectivity


if __name__ == "__main__":
	# calling main function
    # creating object of TwitterClient Class
    text = "Love happy marriage"
    clean_text = clean_tweet(text)

    print(get_tweet_sentiment(text))
