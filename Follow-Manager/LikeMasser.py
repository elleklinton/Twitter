import re
from bs4 import BeautifulSoup
import requests
from collections import OrderedDict

def login_to_twitter(username, password):
    post = "https://twitter.com/sessions"
    url = "https://twitter.com"
    data = {"session[username_or_email]": username,
            "session[password]": password,
            "scribe_log": "",
            "redirect_after_login": "/",
            "remember_me": "1"}
    with requests.Session() as sess:
        r = sess.get(url)
        soup = BeautifulSoup(r.content, "lxml")
        AUTH_TOKEN = soup.select_one("input[name=authenticity_token]")["value"]
        data["authenticity_token"] = AUTH_TOKEN
        return sess

def get_likes(sess, id):
    page = sess.get('https://twitter.com/i/activity/favorited_popup?id=' + str(id))
    soup = BeautifulSoup(page.content, "lxml").decode()
    found_ids = re.findall(r'data-screen-name=\\"+\S+', soup)
    decoder = lambda s: s.split('"')[1].replace('\\', '')
    usernames = []
    for username in found_ids:
        usernames.append(decoder(username))
    usernames = list(OrderedDict.fromkeys(usernames[1:]))
    return usernames


if __name__ == '__main__':
    # stream_likes()
    # sess = login_to_twitter("_the_bitchqueen", "BitchQueenMyAss")
    # get_likes(sess, '1068310874652237825')
    0
