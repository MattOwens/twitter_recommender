from kafka import KafkaConsumer
import json
import threading
import logging


class KafkaTweetReceiver(threading.Thread):

    def __init__(self, loader):
        super(KafkaTweetReceiver, self).__init__()
        self._loader = loader
        self._consumer = KafkaConsumer(bootstrap_servers='localhost:9092', value_deserializer=self.decode_to_json)


    def run(self):
        logging.log(logging.INFO, 'Tweet Recorder starting')

        self._consumer.subscribe(['incoming_tweets'])

        while True:
            for message in self._consumer:
                topic = message[0] # I hope that doesn't change

                if topic == 'incoming_tweets':
                    self.load_tweet(message)
                else:
                    print(message)

    def load_tweet(self, message):
        tweet = message[6]
        self._loader.add_tweet(tweet)

    def decode_to_json(self, value):
        return json.loads(value)