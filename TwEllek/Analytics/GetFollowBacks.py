import json
import tweepy
from tweepy import Stream
from tweepy.streaming import StreamListener
import os
import pickle
import time
import datetime
import TwitterAPI as tapi
import matplotlib.pyplot as plt
import itertools


def loadDictionary(path):
    print("loading dict at: ", path)
    program_path = os.path.dirname(os.path.realpath(__file__))
    file = open(program_path + path, "rb")
    unpickler = pickle.Unpickler(file)
    t = unpickler.load()
    return t


def plot_graph(x_data, x_label, y_data, y_label, graph_title):
    x_data_avg = sum(x_data)/len(x_data)
    y_data_avg = sum(y_data)/len(y_data)

    tick_count = 10
    range = (max(x_data) - min(x_data))
    spacing = int(range / tick_count)
    index = min(x_data) - spacing
    array_of_tick_locations = []

    for n in itertools.repeat(None, tick_count + 4):
        array_of_tick_locations.append(index)
        index = index + spacing


    plt.title(graph_title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.scatter(x_data, y_data, 5)
    plt.axis([min(array_of_tick_locations), max(array_of_tick_locations), 0, max(y_data) + 0.1*y_data_avg])
    plt.xticks(array_of_tick_locations)
    plt.show()


if __name__ == '__main__':
    dict = loadDictionary('/twitter/elleklinton_follower_tweets.pk')

    array_of_tweets = []

    for user in dict:
        for tweet in dict[user]:
            array_of_tweets.append(tweet)

    print(len(array_of_tweets))

    x_data = []
    y_data = []

    hour_count_dict = {}

    for tweet in array_of_tweets:
        if (tweet['tweet_time'].hour not in hour_count_dict):
            hour_count_dict[tweet['tweet_time'].hour] = 1
        else:
            hour_count_dict[tweet['tweet_time'].hour] = hour_count_dict[tweet['tweet_time'].hour] + 1


    for hour in hour_count_dict:
        x_data.append(hour)
        y_data.append(hour_count_dict[hour])

    print(hour_count_dict)

    plot_graph(x_data, 'hour', y_data, 'count', 'count of tweets by hour')




