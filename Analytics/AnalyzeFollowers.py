import matplotlib.pyplot as plt
import pickle
import os
import datetime
import tweepy
import webbrowser




def get_auth():
    globals()

    try:
        try:
            consumer_key = 'XXX'
            consumer_secret = 'XXX'
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

            webbrowser.open(auth.get_authorization_url())
            pin = input('Verification pin number from twitter.com: ').strip()
            token = auth.get_access_token(verifier=pin)

            print('Access token successful')

            api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
            api.verify_credentials()
            # print('  Key: %s' % token.key)
            # print('  Secret: %s' % token.secret)
            return api, auth
        except Exception as error:
            print('error')
            print(error)

    except:
        print('error authenticating')



def dumpDictionary(obj, system_path, file_name):
    print('saving: ' + file_name + ' at path: ' + str(system_path))
    program_path = os.path.dirname(os.path.realpath(__file__)) + '/'
    file = open(system_path + '/'+ file_name, "wb")
    pickle.dump(obj, file, pickle.HIGHEST_PROTOCOL)




def format_progress_string(completed, total):
    new_total = total
    if (total == 0):
        new_total = 1
    return '\rprogress: ' + str(completed) + '/' + str(total) + ' (' + str(int(completed*100/new_total)) + '%)'




def get_followers_from_account(username, api, max_users):
    followers = []
    follower_count = api.get_user(username).followers_count


    print(format_progress_string(0,follower_count), end='')

    for page in tweepy.Cursor(api.followers, screen_name=username, count=200).pages():
        for entry in page:
            if (len(followers) < max_users):
                followers.append(entry)
                print(format_progress_string(len(followers), follower_count), end='')
            elif (len(followers) >= max_users):
                return followers

        # followers.extend(page)
        # print(format_progress_string(len(followers),follower_count), end='')
        # if (len(followers) >= max_users):
        #     return followers

    return followers




def get_tweets_from_followers(followers, api, max_days_back, include_rts):

    follower_tweet_dict = {}
    account_count = len(followers)

    for account in followers:
        print(str(datetime.datetime.now()) + ': ' + format_progress_string(len(follower_tweet_dict),account_count), end='')
        tweets = get_tweets_from_account(username=account.screen_name, api=api, max_days_back=max_days_back, include_rts=include_rts)
        follower_tweet_dict[account.screen_name] = tweets

    return follower_tweet_dict




def make_user_container(username):
    program_path = os.path.dirname(os.path.realpath(__file__))
    user_path = program_path + '/' + username

    if not os.path.exists(user_path):
        os.makedirs(user_path)
    return user_path




def save_data(username, user_timeline_tweets, user_followers, follower_tweet_dict):
    user_container = make_user_container(username)

    dumpDictionary(user_timeline_tweets, user_container, 'user_timeline_tweets.pk')
    dumpDictionary(user_followers, user_container, 'user_followers.pk')
    dumpDictionary(follower_tweet_dict, user_container, 'follower_tweet_dict.pk')




def collect_data(api, username, max_days_back_for_followers, include_follower_rts, max_users=1000):
    print('\n\ngathering ' + username + "'s tweets")
    user_timeline_tweets = get_tweets_from_account(username=username, api=api, max_days_back=365,
                                                   include_rts=False)  # get last year of tweets

    print('\n\ngathering ' + username + "'s followers")
    user_followers = get_followers_from_account(username, api, max_users)

    print('\n\ngathering ' + username + "'s followers' tweets")
    follower_tweet_dict = get_tweets_from_followers(followers=user_followers, api=api,
                                                    max_days_back=max_days_back_for_followers,
                                                    include_rts=include_follower_rts)

    save_data(
        username=username,
        user_timeline_tweets=user_timeline_tweets,
        user_followers=user_followers,
        follower_tweet_dict=follower_tweet_dict
    )

    return user_timeline_tweets, user_followers, follower_tweet_dict



def get_tweets_from_account(username, api, max_days_back, include_rts):

    earliest_date = datetime.datetime.now() - datetime.timedelta(days=max_days_back)
    array_of_user_tweets = []
    status_count = 0

    try:
        for statuses in tweepy.Cursor(api.user_timeline, count=200, include_rts=include_rts, exclude_replies=True, screen_name=username).pages():
            for status in statuses:
                status_count = status_count + 1
                # print(format_progress_string(status_count, 0), end='')
                if (status.created_at >= earliest_date):
                    tweet = {}
                    tweet['created_at'] = status.created_at
                    tweet['id'] = status.id
                    tweet['username'] = status.user.screen_name
                    tweet['favourites_count'] = status.favorite_count
                    tweet['text'] = status.text
                    array_of_user_tweets.append(tweet)
                else:
                    return array_of_user_tweets
    except Exception as error:
        print('error with @', username, "\'s tweets")
        print(error)
        return []



if __name__ == '__main__':
    username = 'elleklinton'
    days_back_to_retrieve_for_followers = 7
    include_follower_rts = True
    max_users_to_retrieve = 10000

    api, auth = get_auth()

    # tweets = tweepy.Cursor(api.user_timeline, count=200, include_rts=True, exclude_replies=True,
    #               screen_name='realDonaldTrump').pages()
    #
    # for tweet in tweets:
    #     print(tweet)

    # user_timeline_tweets, user_followers, follower_tweet_dict = collect_data(api=api, username=username, max_days_back_for_followers=days_back_to_retrieve_for_followers, include_follower_rts=include_follower_rts, max_users=max_users_to_retrieve)

    followers = get_followers_from_account('elleklinton', api, 20000)
    user_container = make_user_container('elleklinton')
    dumpDictionary(followers, user_container, 'ellek_linton_followers.pk')

