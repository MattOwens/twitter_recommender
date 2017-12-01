import tweepy
import logging
from twitterdata import keys, batch_loader, stream_loader, test_tweet_consumer

auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.access_token, keys.access_secret)

auth2 = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)

api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

batch = batch_loader.BatchTweetLoader(api)
stream = stream_loader.StreamLoader(api)


def subscribe_user(user):
    batch.load_tweets(user)
    stream.add_user(user)


def subscribe_hashtag(hashtag):
    batch.load_hashtag_tweets(hashtag)
    stream.add_hashtag(hashtag)
