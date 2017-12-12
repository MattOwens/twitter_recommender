import tweepy
import sys
from twitterdata import hidden_keys, batch_loader, stream_loader, kafka_tweet_sender, direct_tweet_sender

auth = tweepy.OAuthHandler(hidden_keys.consumer_key, hidden_keys.consumer_secret)
auth.set_access_token(hidden_keys.access_token, hidden_keys.access_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True,
                 parser = tweepy.parsers.JSONParser())

batch = None
stream = None

this = sys.modules[__name__]


def load_config(seed_users, seed_hashtags, send_tweet_name):
    send_tweet = direct_tweet_sender.send_tweet
    if send_tweet_name == 'Kafka':
        send_tweet = kafka_tweet_sender.send_tweet
    this.batch = batch_loader.BatchTweetLoader(api, send_tweet)
    this.stream = stream_loader.StreamLoader(api, send_tweet)

    stream.start_batch_update()

    for user in seed_users:
        subscribe_user(user)

    for hashtag in seed_hashtags:
        subscribe_hashtag(hashtag)

    stream.finish_batch_update()


def subscribe_user(user):
    batch.load_tweets(user)
    stream.add_user(user)


def subscribe_hashtag(hashtag):
    batch.load_hashtag_tweets(hashtag)
    stream.add_hashtag(hashtag)


def give_feedback(feedback):
    print('Given feedback')
    stream.start_batch_update()
    for label in feedback:
        if label.startswith('#') and label not in stream.hashtags:
            print('subscribing to hashtag ', label)
            subscribe_hashtag(label)
        elif label not in stream.usernames:
            print('Subscribing to user ', label)
            subscribe_user(label)

    stream.finish_batch_update()