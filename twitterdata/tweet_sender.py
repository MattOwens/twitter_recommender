from kafka import KafkaProducer
from kafka.errors import KafkaError
import json


def send_tweet(tweet):
    print('Sending a tweet...')
    future = P.send('incoming_tweets', value=tweet)
    P.flush(timeout=30)
    # Block for 'synchronous' sends
    try:
        record_metadata = future.get(timeout=10)
    except KafkaError:
        # Decide what to do if produce request failed...
        print('There was an error')
        pass


def serialize_tweet(tweet):
    print('Serializing tweet')
    return json.dumps(tweet).encode('utf-8')


P = KafkaProducer(bootstrap_servers='localhost:9092',value_serializer=serialize_tweet)
print('Hey you imported tweet_sender')