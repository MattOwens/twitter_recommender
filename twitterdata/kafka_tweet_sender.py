from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging
import sys

this = sys.modules[__name__]


def send_tweet(tweet):
    if this.P is None:
        this.P = KafkaProducer(bootstrap_servers='localhost:9092',value_serializer=serialize_tweet)
    logging.log(logging.INFO, 'Sending tweet {0}'.format(tweet['id_str']))
    future = P.send('incoming_tweets', value=tweet)
    P.flush(timeout=30)
    # Block for 'synchronous' sends (I think I did this because sending async wasn't working?)
    try:
        record_metadata = future.get(timeout=10)
    except KafkaError:
        # Decide what to do if produce request failed...
        print('There was an error')
        pass


def serialize_tweet(tweet):
    return json.dumps(tweet).encode('utf-8')


P = None
