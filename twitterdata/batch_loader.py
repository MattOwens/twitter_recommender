import twitterdata.tweet_sender as sender

tweets_to_get = 100


class BatchTweetLoader:

    def __init__(self, api):
        self.api = api

    def load_tweets(self, user):
        print('Getting tweets for user', user)
        tweets = self.api.user_timeline(screen_name=user, count=tweets_to_get, include_rts=True, tweet_mode='extended')
        self._send_tweets(tweets)

    def load_hashtag_tweets(self, hashtag):
        print('Getting tweets for hashtag ', hashtag)
        tweets = self.api.search(q=hashtag, count=tweets_to_get, lang="en", tweet_mode='extended')['statuses']
        self._send_tweets(tweets)

    def _send_tweets(self, tweets):
        for tweet in tweets:
            sender.send_tweet(tweet)