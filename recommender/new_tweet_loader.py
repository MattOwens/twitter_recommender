class NewTweetLoader:

    def __init__(self):
        self._all_tweets = []
        self._tweets_by_user = {}
        self._tweets_by_hashtag = {}

    def add_tweets(self, tweets):
        for tweet in tweets:
            self.add_tweet(tweet)

    def get_snapshot(self): # there's a race condition here. I'll deal with it later
        all_tweets = self._all_tweets
        self._all_tweets = []
        by_user = self._tweets_by_user
        self._tweets_by_user = {}
        by_hashtag = self._tweets_by_hashtag
        self._tweets_by_hashtag = {}

        return [all_tweets, by_user, by_hashtag]

    def add_tweet(self, tweet):
        self._all_tweets.append(tweet)
        self._add_tweet_by_user(tweet)
        self._add_tweet_by_hashtag(tweet)

    def _add_tweet_by_user(self, tweet):
        user_id = tweet['user']['id']

        if user_id not in self._tweets_by_user:
            self._tweets_by_user[user_id] = [tweet]
        else:
            self._tweets_by_user[user_id].append(tweet)

    def _add_tweet_by_hashtag(self, tweet):
        for entity in tweet['entities']['hashtags']:
            hashtag = entity['text']

            if hashtag not in self._tweets_by_hashtag:
                self._tweets_by_hashtag[hashtag] = [tweet]
            else:
                self._tweets_by_hashtag[hashtag].append(tweet)