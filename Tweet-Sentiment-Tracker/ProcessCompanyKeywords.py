from Classify_Tweets import *

class Company:

    def __init__(self, name='', keywords=[], active=True):
        self.name = name
        self.keywords = keywords
        self.active = active


class Tweet:

    def __init__(self, tweet_object):
        #tweet text, username, time, fave count, linked URL?, tweet_id
        self.text = tweet_object.text
        self.username = tweet_object.user.screen_name
        self.time = tweet_object.created_at
        self.tweet_id = tweet_object.id
        self.user_followers = tweet_object.user.followers_count
        self.user_following = tweet_object.user.friends_count
        self.user_status_count = tweet_object.user.statuses_count
        self.user_location = tweet_object.user.location
        self.sentiment_analysis_of_tweet()
        
    
    def sentiment_analysis_of_tweet(self):
        classification, polarity, subjectivity  = get_tweet_sentiment(self.text)
        self.classification = classification
        self.polarity = polarity
        self.subjectivity = subjectivity


    def __repr__(self):
        str_to_show = '['

        for obj_key in self.__dict__.keys():
            str_to_show += obj_key + ':' + str(self.__dict__[obj_key]) + ', '

        return str_to_show[:len(str_to_show) - 2] + ']'





def import_text_file(filename):
    return open(filename, 'r').read()




def format_text_to_company_objects(text):
    companies = text.split('\n\n')
    company_list = []

    for company in companies:
        split_company = company.split(':')
        name = split_company[0]
        keyword_string = split_company[1]
        keywords = keyword_string.split(',')

        company_object = Company(name=name, keywords=keywords, active=True)
        company_list.append(company_object)

    return company_list




def find_company(company_name):
    list_of_companies = load_companies_from_file('keywords.txt')

    for company in list_of_companies:
        if company_name.lower() in company.name.lower():
            return company
        elif company.name.lower() in company_name.lower():
            return company

    return None




def load_companies_from_file(filename):
    text = import_text_file(filename)
    list_of_companies = format_text_to_company_objects(text)

    return list_of_companies




if __name__ == '__main__':
    list_of_companies = load_companies_from_file('keywords.txt')

    # for comp in list_of_companies:
    #     print(comp.keywords)
