import tweepy
import webbrowser
import ProcessCompanyKeywords as ProcessKeywords
from ProcessCompanyKeywords import Tweet
from StoreDetails import save_dill, load_dill
from datetime import datetime, timedelta
import time


tweets = []
time_to_end_stream = datetime.now() + timedelta(seconds=60*60)
length_of_stream = 60*60


class Streamer(tweepy.StreamListener):

    def on_connect(self):
        print("Connection established!!")

    def on_disconnect(self, notice):
        print("Connection ended :(")
        print(notice)

    def on_error(self, status_code):
        print('error notice')
        print(status_code)

    def on_warning(self, notice):
        print('warning notice')
        print(notice)

    def on_limit(self, status):
        print('on limit')
        print(status)

    def on_status(self, status):
        global time_to_end_stream
        global tweets
        global length_of_stream

        if datetime.now() >= time_to_end_stream:
            now = datetime.now().strftime("%Y-%B-%d--%Hh-%Mm (" + str(length_of_stream) + ' secs).dl')
            save_dill(tweets, 'cached_tweets/' + now)
            print('saving', len(tweets), 'tweets as', now)
            return False
        else:
            if should_track(keyword_list, status):
                try:
                    tweets.append(Tweet(status))
                    str_to_display = 'Tweets Captured: {}'.format(len(tweets))
                    print(str_to_display)
                except Exception as err:
                    print('error saving tweet:', err)





def should_track(keywords, status):
    text = status.text.lower()

    if 'rt' in text:
        return False
    elif keywords_in_text(keywords, text):
        return True
    else:
        return False

def keywords_in_text(keywords, text):
    for keyword in keywords:
        if keyword.lower() in text:
            return True
    return False





def authenticate_with_tokens(access_token, access_secret, consumer_key, consumer_secret):
    try:
        auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)

        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        return api
    except Exception as error:
        print(error)
        return error




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




def login(api_file_name='cached_api.dl'):
    consumer_key = 'XXX'
    consumer_secret = 'XXX'

    cached_api = load_dill(api_file_name)

    if cached_api:
        return cached_api
    else:
        api = authenticate_with_browser(consumer_key, consumer_secret)
        save_dill(api, api_file_name)
        return api




def create_stream(api, keywords, seconds_to_run_for=60*60):
    global time_to_end_stream
    global length_of_stream

    length_of_stream = seconds_to_run_for
    time_to_end_stream = get_time_in_future(seconds_to_run_for)
    stream = tweepy.Stream(api.auth, Streamer())
    stream.filter(track=keywords, async=True, stall_warnings=True, languages=['en'])
    return tweets
    


def get_time_in_future(how_many_seconds):
    return datetime.now() + timedelta(seconds=how_many_seconds)



if __name__ == '__main__':

    api = login() #login as @_the_bitchqueen

    keyword_list = []

    # keyword_list.extend(ProcessKeywords.find_company('nike').keywords)
    # keyword_list.extend(ProcessKeywords.find_company('apple').keywords)
    # keyword_list.extend(ProcessKeywords.find_company('tesla').keywords)
    keyword_list.extend(ProcessKeywords.find_company('netflix').keywords)
    # keyword_list.extend(ProcessKeywords.find_company('google').keywords)


    tweet_list = create_stream(
        api=api, 
        keywords=keyword_list, 
        seconds_to_run_for=2*60)
    # print(company_to_track.keywords)
