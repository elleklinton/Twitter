import json
import tweepy
from tweepy import Stream
from tweepy.streaming import StreamListener
import os
import pickle
import time
import datetime
import TwitterAPI as tapi


access_token = 'XXX'
access_secret = 'XXX'
consumer_key = 'XXX'
consumer_secret = 'XXX'


def auth():
    globals()
    auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    api.verify_credentials()
    return api, auth


def get_followers_of_username(username, api):
    pages = []
    for page in tweepy.Cursor(api.followers, screen_name=username, count=200).pages():
        pages.extend(page)
        print(len(pages))
        print(datetime.datetime.now())
        dumpDictionary(pages, '/twitter/follower_analysis_elleklinton.pk')


def get_tweets_from_user_list(user_list, how_far_back, file_name):
    tapi.run(
        max_days_back=how_far_back,
        users_to_fetch=user_list,
        file_name=file_name
    )


def dumpDictionary(obj, path):
    program_path = os.path.dirname(os.path.realpath(__file__))
    file = open(program_path + path, "wb")
    pickle.dump(obj, file, pickle.HIGHEST_PROTOCOL)


def loadDictionary(path):
    print("loading dict at: ", path)
    program_path = os.path.dirname(os.path.realpath(__file__))
    file = open(program_path + path, "rb")
    unpickler = pickle.Unpickler(file)
    t = unpickler.load()
    return t


if __name__ == '__main__':
    account_name = 'elleklinton'

    api, auth = auth()

    # get_followers_of_username(account_name, api)

    dict = loadDictionary('/twitter/follower_analysis_elleklinton.pk')

    list_of_usernames = []
    count = 0
    for entry in dict:
        print(entry.screen_name)
        list_of_usernames.append(entry.screen_name)

    how_many_days_back = 1

    get_tweets_from_user_list(list_of_usernames, how_many_days_back, 'elleklinton_follower_tweets')
