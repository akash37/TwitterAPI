from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from elasticsearch import Elasticsearch
import configparser
import json

config = configparser.ConfigParser()
config.read('config')
query = config.get('Keywords','query').split(',')

ckey = "IbvazkmPp2f4OjjdJP1C9Huwb"
csecret = "rj5Bk2evAbZcuVNBtQnmJMJ8DplGv9NRhL5lfFogA9V5RrBoNA"
atoken = "1006242129058791426-NbchJNxxhZSwcgsD9zKAKxcp1Sfk4F"
asecret = "jrI7jWGwWWckIpVMoRTStkcwrNLpgvYiKoILljS26WgcD"

keyword = ""
es = Elasticsearch()
class listener(StreamListener):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.limit = 10000

    def on_data(self, data):
        all_data = json.loads(data)
        tweet_text = all_data["text"]
        timestamp = all_data["created_at"]
        #print(tweet_text)
        #es.create(index = keyword,doc_type = "Tweets", body = tweet_text,id = self.counter)
        es.index(index = keyword, doc_type = "Tweets", body = {"date":timestamp,"Text":tweet_text})
        self.counter += 1
        if self.counter < self.limit:
             return True
        else:
             self.counter = 0
             twitterStream.disconnect()
        return data

    def on_error(self, status):
        print(status)

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream = Stream(auth, listener())
for i in range(0,len(query)):
        keyword = query[i]
        twitterStream.filter(track=[query[i]])

