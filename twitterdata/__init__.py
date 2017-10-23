import tweepy
import logging
from twitterdata import keys, batch_loader, stream_loader, test_tweet_consumer

auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.access_token, keys.access_secret)

api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    consumer = test_tweet_consumer.TestTweetConsumer()
    consumer.start()

    batch = batch_loader.BatchTweetLoader(api)
    batch.load_tweets("SenToomey")
    batch.load_tweets("daylinleach")

    stream = stream_loader.StreamLoader(api)
    stream.update_users(['POTUS', 'SenToomey', 'realDonaldTrump', 'ESPNCFB'])