import twitterdata.tweet_sender as sender


class BatchTweetLoader:

    def __init__(self, api):
        self.api = api

    def load_tweets(self, user):
        print('Getting tweets for user', user)
        tweets = self.api.user_timeline(screen_name=user, include_rts=True)
        self._send_tweets(tweets)

    def _send_tweets(self, tweets):
        for tweet in tweets:
            sender.send_tweet(tweet)

    def _send_tweet(self, tweet):
        print(tweet)