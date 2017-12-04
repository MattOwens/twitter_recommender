import os
import metapy
import datetime
import time
import math

# Wed Nov 29 15:10:01 +0000 2017
date_format = '%a %b %d %H:%M:%S %z %Y'

# Tweet preparation
tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)
tok = metapy.analyzers.LowercaseFilter(tok)
tok = metapy.analyzers.ListFilter(tok, os.path.join('recommender','lemur-stopwords.txt'), metapy.analyzers.ListFilter.Type.Reject)
tok = metapy.analyzers.Porter2Filter(tok)
analyzer = metapy.analyzers.NGramWordAnalyzer(1, tok)


class TweetAnalyzer: # come up with better name

    def __init__(self, loader, seed_users, seed_hashtags):
        self._loader = loader
        self._seed_users = seed_users
        self._seed_hashtags = seed_hashtags
        self._seed_by_user = {}
        self._seed_by_hashtag = {}
        self._new_by_user = {}
        self._new_by_hashtag = {}

    def update_analysis(self):
        self._update_timestamp = time.time()
        snapshot = self._loader.get_snapshot()
        all_tweets = snapshot[0]
        by_user = snapshot[1]
        by_hashtag = snapshot[2]

        # first pull out hashtags and user mentions so we know what to look at next
        users_mentioned = set()
        hashtags_used = set()

        for tweet in all_tweets:
            mentions = tweet['entities']['user_mentions']
            for mention in mentions:
                users_mentioned.add(mention['id'])
            hashtags = tweet['entities']['hashtags']

            for hashtag in hashtags:
                hashtags_used.add('#{}'.format(hashtag['text']))

        print('Users mentioned in this snapshot: ', users_mentioned)
        print('Hashtags used in this snapshot: ', hashtags_used)

        self._update_corpus(by_user, by_hashtag)
        self._run_recommendations()

    def _update_corpus(self, by_user, by_hashtag):
        # intentionally duplicates tweets - will help with similarity when we have multiple hashtags in the same tweet
        # or when a user we care about uses a hashtag we care about
        print('updating corpus')
        for user in by_user:
            user_tweets = []

            for tweet in by_user[user]:
                text = self._prepare_tweet_text(tweet)
                label = tweet['user']['screen_name']
                timestamp = datetime.datetime.strptime(tweet['created_at'], date_format).timestamp()
                user_tweets.append({'text':text,'label':label,'timestamp':timestamp})

            self._add_user_tweets(user, user_tweets)

        for hashtag in by_hashtag:
            hashtag_tweets = []
            label = '#{}'.format(hashtag)

            for tweet in by_hashtag[hashtag]:
                text = self._prepare_tweet_text(tweet)
                timestamp = datetime.datetime.strptime(tweet['created_at'], date_format).timestamp()
                hashtag_tweets.append({'text':text,'label':label,'timestamp':timestamp})

            self._add_hashtag_tweets(label, hashtag_tweets)

    def _add_user_tweets(self, user, tweets):
        if user in self._seed_users:
            if user in self._seed_by_user:
                self._seed_by_user[user].append(tweets)
            else:
                self._seed_by_user[user] = tweets
        else:
            if user in self._new_by_user:
                self._new_by_user[user].append(tweets)
            else:
                self._new_by_user[user] = tweets

    def _add_hashtag_tweets(self, hashtag, tweets):
        if hashtag in self._seed_hashtags:
            if hashtag in self._seed_by_hashtag:
                self._seed_by_hashtag[hashtag].append(tweets)
            else:
                self._seed_by_hashtag[hashtag] = tweets
        else:
            if hashtag in self._new_by_hashtag:
                self._new_by_hashtag[hashtag].append(tweets)
            else:
                self._new_by_hashtag[hashtag] = tweets

    def _prepare_tweet_text(self, tweet):
        doc = metapy.index.Document()
        doc.content(tweet['full_text'] if 'full_text' in tweet else tweet['text'])
        return analyzer.analyze(doc)

    def _run_recommendations(self):
        print('Running recommendations')
        print(self._update_timestamp)
        scores_by_seed_user = {}
        total_scores = {}

        for user, user_tweets in self._new_by_user.items():
            total_scores[user] = 0.0
            for seed_user, seed_tweets in self._seed_by_user.items():
                score = self.score(user_tweets, seed_tweets)
                total_scores[user] += score
                scores_by_seed_user[seed_user] = score

        scores_by_seed_hashtag = {}

        for hashtag, hashtag_tweets in self._new_by_hashtag.items():
            total_scores[hashtag] = 0.0
            for seed_hashtag, seed_tweets in self._seed_by_hashtag.items():
                score = self.score(hashtag_tweets, seed_tweets)
                total_scores[hashtag] += score
                scores_by_seed_hashtag[seed_hashtag] = score

        print('Scoring results:')
        for label, score in total_scores.items():
            print('label: {} score: {}'.format(label, score))

    def score(self, new_tweets, seed_tweets):
        score = 0.0
        for new_tweet in new_tweets:
            for seed_tweet in seed_tweets:
                score += self._score_pair(new_tweet, seed_tweet)

        # I think this should normalize correctly. I'll think about it when I'm less tired
        return score/(len(new_tweets)*len(seed_tweets))

    def _score_pair(self, a, b):
        dot_product = self._dict_dot_product(a['text'], b['text'])
        time_multiplier = 1 / (math.log(self._update_timestamp - a['timestamp']) *
                               math.log(self._update_timestamp - b['timestamp']))
        return dot_product * time_multiplier

    def _dict_dot_product(self, a, b):
        total = 0.0
        for word, count in a.items():
            if word in b:
                total += count * b[word]
        return total