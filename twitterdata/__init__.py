import tweepy
from twitterdata import keys, batch_loader, stream_loader

auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.access_token, keys.access_secret)

api = tweepy.API(auth)


if __name__ == "__main__":
    batch = batch_loader.BatchTweetLoader(api)
    batch.load_tweets("SenToomey")
    batch.load_tweets("daylinleach")

    stream = stream_loader.StreamLoader(api)
    stream.update_users(['POTUS', 'SenToomey', 'realDonaldTrump', 'ESPNCFB'])