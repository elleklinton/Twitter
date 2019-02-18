import tweepy
import time
import webbrowser
from Login import *
import datetime
import numpy as np
from CustomModel import TrainedModel
from UserObject import UserObject
import tensorflow as tf
import LikeMasser
import smtplib
import dependencies

# dependencies.install_all()
email = smtplib.SMTP('smtp.gmail.com', 587)

consumer_key = 'XXX'
consumer_secret = 'XXX'

people_followed = ['berkeleybaddie']
people_to_follow = []


def get_most_recent_tweet(api, account_name):
    tweet = api.user_timeline(include_rts=False, exclude_replies=True, screen_name=account_name, count=4)[0]
    return tweet




def get_list_of_retweeters(api, account_name, count):
    assert count <= 100

    print('getting list of retweeters')

    tweet = get_most_recent_tweet(api, account_name)
    retweeters = api.retweets(tweet.id, count=count)
    return retweeters




def follow_user(api, person_to_follow):
    global people_followed

    user = person_to_follow.user

    try:
        friendship = api.create_friendship(user.id)
        print('followed', user.screen_name)
        people_followed.append(user)
        return 'success'
    except Exception as err:
        print('error following', user, err, friendship)
        sendsms('error following {}, {}'.format(user, str(err)))
        return 'error'


def sec_between_follow(daily_limit=950, secs_in_day=60*60*24):
    return secs_in_day / daily_limit

def get_recently_followed():
    all_followed = load_user_objects()
    last_day_deadline = datetime.datetime.now() - datetime.timedelta(days=1)
    followed_in_last_day = [u for u, o in all_followed.items() if o.follow_date >= last_day_deadline]
    return len(followed_in_last_day)

def check_daily_limit(daily_limit=950):
    recently_followed = get_recently_followed()
    if recently_followed >= daily_limit:
        return False
    else:
        return True


def convert_userlist_to_userobjects(api, users):
    user_objects = []
    for user in users:
        if isinstance(user, str):
            user_objects.append(UserObject(api, user))
        else:
            user_objects.append(UserObject(api, user.user))
    save_user_objects(user_objects)
    return user_objects

def save_user_objects(user_objects):
    file_name = 'live_training_data/' + authenticated_user + '_user_object_dict.dl'
    existing = load_dill(file_name)
    if not existing:
        existing = {}
    for obj in user_objects:
        if obj.username not in existing.keys():
            existing[obj.username] = obj
    save_dill(existing, file_name)

def load_user_objects():
    return load_dill('live_training_data/' + authenticated_user + '_user_object_dict.dl')



def get_retweeters(api, account, count):
    users = get_list_of_retweeters(api, account, count)
    users = convert_userlist_to_userobjects(api,users)
    # [print(u.screen_name) for u in users]
    return users

def get_likers(api, account_name, how_many):
    tweet = get_most_recent_tweet(api, account_name)
    usernames = LikeMasser.get_likes(sess, tweet.id)[:how_many]
    users = convert_userlist_to_userobjects(api, usernames)
    return users


def check_if_should_follow(user, use_ml_model):

    # model = load_saved_model('/models/v4model.json', '/models/v4model_weights.h5')
    # prediction = predict_single_result(model, user.data)
    #['followers', 'following', 'favourites_count', 'statuses_count', 'output']

    #user is UserObject
    user_data = user.export_user_data(model.input_labels)
    prediction = model.make_prediction_on_abnormal_data(user_data)
    if user.username in people_followed or check_daily_limit() == False:
        return False
    else:
        if prediction == 0 and use_ml_model:
            print('model says not to follow', user.username)
            return False
        else:
            return True

import datetime
last_follow = datetime.datetime.now()


def follow_username(api, username):
    global last_follow
    try:
        friendship = api.create_friendship(screen_name=username)
        today = datetime.date.today().strftime("%B %d, %Y")
        print('followed', username, '(', get_recently_followed() , ')')
        print('time since last:', datetime.datetime.now() - last_follow)
        last_follow = datetime.datetime.now()
        people_followed.append(username)
        return 'success'
    except Exception as err:
        print('error following', username, err)
        sendsms('error following {}, {}'.format(username, str(err)))
        return 'error'


def get_all_following(api):
    following = []
    for friend in tweepy.Cursor(api.friends, count=200, screen_name=api.me().screen_name).items():
        following.append(friend)
    return following

def filter_following(api, following, never_unfollow=[], secs_between_unfollow=30):
    to_unfollow = []
    for user in following:
        if user not in never_unfollow:
            to_unfollow.append(user)
    return to_unfollow


def check_if_usera_follows_userb(api, user_a, user_b):
    try:
        friendship = api.show_friendship(source_screen_name=user_a, target_screen_name=user_b)
        return friendship[0].following
    except Exception as err:
        print('error checking following', err)
        sendsms('error checking following {} {}, {}'.format(user_a, user_b, str(err)),)
        return True


def unfollow_users(api, unfollow_list, delay):
    for user in unfollow_list:
        time.sleep(delay)
        followed_back = check_if_usera_follows_userb(api, user, api.me().screen_name)
        if not followed_back:
            try:
                print('unfollowing', user)
                api.destroy_friendship(screen_name=user)
            except Exception as err:
                sendsms('error unfollowing {}, {}'.format(user, str(err)))
                print('error unfollowing', user, ':', err)
        else:
            print('skipping', user, '(followed back)')


def unmass(api, never_unfollow, secs_between_unfollow):
    to_unfollow = load_user_objects().keys()
    to_unfollow = filter_following(api, to_unfollow, never_unfollow)
    unfollow_users(api, to_unfollow, secs_between_unfollow)


def wait_until_tomorrow():
    print('hit daily limit. Waiting until tomorrow morning!')
    now = datetime.datetime.now()
    tomorrow = (now + datetime.timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    print('resuming at,', tomorrow)
    remaining_seconds = (tomorrow - now).total_seconds()
    print('(sleeping for', remaining_seconds, 'seconds)')
    time.sleep(remaining_seconds)


def start_loop(api, never_unfollow, account_to_lob_off='berkeleybaddie',
               secs_between_follow=50, mass_from_likes=False,
               how_many_retweets=4, use_ml_model=True, already_followed_count=0, should_unmass=True):

    global people_followed
    # day_tracker[datetime.date.today().strftime("%B %d, %Y")] = already_followed_count

    follow_limit_safe = check_daily_limit()

    if datetime.datetime.now().weekday() == 6 and should_unmass:
        try:
            print('unfollow day!')
            unmass(api, never_unfollow, int(secs_between_follow/2))
            people_followed = [api.me().screen_name]
        except: print('error with unfollowing')
        wait_until_tomorrow()
    else:
        if not mass_from_likes and follow_limit_safe:
            try: users = get_retweeters(api, account_to_lob_off, how_many_retweets)
            except Exception as err: print('error getting retweeters', err), sendsms('error getting retweeters'); users = []
        elif mass_from_likes and follow_limit_safe:
            try: users = get_likers(api, account_to_lob_off, how_many_retweets)
            except: print('error getting likers'); users = []
        if follow_limit_safe:
            for user in users:
                try:
                    should_follow = check_if_should_follow(user, use_ml_model)
                    if should_follow:
                        follow_username(api, user.username)
                        time.sleep(secs_between_follow)
                except:
                    print('error following user:', user.username)
                    sendsms('error following ' + user.username)
        else:
            print('max people followed:', get_recently_followed())
            time.sleep(secs_between_follow)

        time.sleep(secs_between_follow / 2)

    start_loop(api=api, never_unfollow=never_unfollow, account_to_lob_off=account_to_lob_off,
               secs_between_follow=secs_between_follow, mass_from_likes=mass_from_likes,
               how_many_retweets=how_many_retweets, use_ml_model=use_ml_model, already_followed_count=already_followed_count,
               should_unmass=should_unmass)


def sendsms(text):
    global email
    try:
        print('sending text')
        text = '(@{}) '.format(authenticated_user) + text
        email.sendmail('EMAIL_TO_SEND_FROM@gmail.com', 'EMAIL_TO_SEND_TO@gmail.com', text)
    except Exception as err:
        print('text failed to send')
        print('error sending text,', err)
        try:
            email = smtplib.SMTP('smtp.gmail.com', 587)
            email.starttls()
            email.login('GMAIL_USERNAME', 'GMAIL_PASSWORD')
        except: print('error logging into text')

# if __name__ == '__main__':


email.starttls()
email.login('GMAIL_USERNAME', 'GMAIL_PASSWORD')


model = load_dill('models/v1.dl')
never_unfollow = ['connorhannigan4','juannisaac','persianthotz_',
                  '702Austin','ArabMuIa','Trendingjoey','_BlaineB',
                  'heyitsmeep','JaIenSkutt','ChaseDickson_',
                  'alexdransfeldt','AshleyGriffo_',
                  'NoelSznn','MOONEMOTlCON',
                  'ShineMyGold','lowkeylean2',
                  'lowkeyclutch','amberlarogers',
                  'jackjensen_6','rihodd','CoreyKeyz',
                  'souljaboy', 'amanda_quon', '_bbol']


api = login('berkeleybaddie')
authenticated_user = api.me().screen_name
# sess = LikeMasser.login_to_twitter("TWITTER_USERNAME", "TWITTER_PASSWORD")

# start_loop(api=api, account_to_lob_off='berkeleybaddie', secs_between_follow=45,
#            never_unfollow=never_unfollow, mass_from_likes=False,
#            how_many_retweets=10, use_ml_model=True)

