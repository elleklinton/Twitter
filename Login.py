import tweepy
import dill
import pickle
import os.path
import webbrowser
from Saver import *

def login(username='berkeleybaddie'):
    consumer_key = 'XXX'
    consumer_secret = 'XXX'

    cached_api = load_dill(username + '_cached_api.dl')

    if cached_api:
        return cached_api
    else:
        api = authenticate_with_browser(consumer_key, consumer_secret)
        save_dill(api, username + '_cached_api.dl')
        return api


def authenticate_with_browser(consumer_key, consumer_secret):
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

        url = auth.get_authorization_url(signin_with_twitter=True)
        print(url)
        webbrowser.open(url)
        pin = input('Verification pin number from twitter.com: ').strip()
        auth.get_access_token(verifier=pin)

        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        api.verify_credentials()

        return api

    except Exception as error:
        print(error)
        return error
