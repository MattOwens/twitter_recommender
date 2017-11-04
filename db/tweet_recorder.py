from kafka import KafkaConsumer
from pymongo import MongoClient
import threading
import json


class TweetRecorder(threading.Thread):

    def __init__(self):
        super(TweetRecorder, self).__init__()
        self._consumer = KafkaConsumer(bootstrap_servers='localhost:9092', value_deserializer=self.decode_to_json)
        self._client = MongoClient('localhost', 27017)
        self._db = self._client.twitter_recommender

    def run(self):
        print('Tweet Recorder starting')

        self._consumer.subscribe(['incoming_tweets'])
        print('Subscribed to incoming_tweets')
        while True:
            for message in self._consumer:
                print('TweetRecorder consuming tweet')
                topic = message[0] # I hope that doesn't change

                if topic == 'incoming_tweets':
                    self.write_incoming_tweet(message)
                else:
                    print(message)

    def write_incoming_tweet(self, message):
        tweet = message[6]
        doc = {"tweet_id":tweet['id'],
               "timestamp":tweet['created_at'],
               "user_id":tweet['user']['id'],
               "user_screen_name":tweet['user']['screen_name'],
               "text":tweet['text'],
               "hashtags":tweet['entities']['hashtags'],
               "user_mentions":tweet['entities']['user_mentions']}

        doc_id = self._db.incoming_tweets.insert_one(doc).inserted_id
        print('Inserted doc', doc_id)

    def decode_to_json(self, value):
        return json.loads(value)
