from recommender import new_tweet_loader

def send_tweet(tweet):
    new_tweet_loader.instance.add_tweet(tweet)