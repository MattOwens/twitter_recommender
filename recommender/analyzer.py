import os
import metapy
import datetime
import time
import math

# Wed Nov 29 15:10:01 +0000 2017
date_format = '%a %b %d %H:%M:%S %z %Y'

# Tweet preparation
with open(os.path.join('recommender','lemur-stopwords.txt')) as f:
    stopwords = [x for x in f]

tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)
tok = metapy.analyzers.LowercaseFilter(tok)
tok = metapy.analyzers.ListFilter(tok, os.path.join('recommender','lemur-stopwords.txt'), metapy.analyzers.ListFilter.Type.Reject)
tok = metapy.analyzers.Porter2Filter(tok)
analyzer = metapy.analyzers.NGramWordAnalyzer(1, tok)


class TweetAnalyzer: # come up with better name

    def __init__(self, loader, seed_users, seed_hashtags):
        self._loader = loader
        self._seed_users = [x.lower() for x in seed_users]
        self._seed_hashtags = [x.lower() for x in seed_hashtags]
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
        return self._run_recommendations()

    def _update_corpus(self, by_user, by_hashtag):
        # intentionally duplicates tweets - will help with similarity when we have multiple hashtags in the same tweet
        # or when a user we care about uses a hashtag we care about
        
        for user, tweets in by_user.items():
            user = user.lower() # important
            user_tweets = []

            for tweet in tweets:
                text = self._prepare_tweet_text(tweet)
                label = user
                timestamp = datetime.datetime.strptime(tweet['created_at'], date_format).timestamp()
                user_tweets.append({'text':text,'label':label,'timestamp':timestamp})

            self._add_user_tweets(user, user_tweets)

        for hashtag, tweets in by_hashtag.items():
            hashtag = hashtag.lower()
            hashtag_tweets = []
            label = '#{}'.format(hashtag)

            for tweet in tweets:
                text = self._prepare_tweet_text(tweet)
                timestamp = datetime.datetime.strptime(tweet['created_at'], date_format).timestamp()
                hashtag_tweets.append({'text':text,'label':label,'timestamp':timestamp})

            self._add_hashtag_tweets(label, hashtag_tweets)

    def _add_user_tweets(self, user, tweets):
        if user in self._seed_users:
            if user in self._seed_by_user:
                self._seed_by_user[user] = self._seed_by_user[user] + tweets
            else:
                self._seed_by_user[user] = tweets
        else:
            if user in self._new_by_user:
                self._new_by_user[user] = self._new_by_user[user] + tweets
            else:
                self._new_by_user[user] = tweets

    def _add_hashtag_tweets(self, hashtag, tweets):
        if hashtag in self._seed_hashtags:
            if hashtag in self._seed_by_hashtag:
                self._seed_by_hashtag[hashtag] = self._seed_by_hashtag[hashtag] + tweets
            else:
                self._seed_by_hashtag[hashtag] = tweets
        else:
            if hashtag in self._new_by_hashtag:
                self._new_by_hashtag[hashtag] = self._new_by_hashtag[hashtag] + tweets
            else:
                self._new_by_hashtag[hashtag] = tweets

    def _prepare_tweet_text(self, tweet):
        doc = metapy.index.Document()
        doc.content(tweet['full_text'] if 'full_text' in tweet else tweet['text'])
        # tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)
        # tok = metapy.analyzers.LowercaseFilter(tok)
        # tok = metapy.analyzers.ListFilter(tok, os.path.join('recommender','lemur-stopwords.txt'), # hopefully this doesn't reread every time
        #                                   metapy.analyzers.ListFilter.Type.Reject)
        # tok = metapy.analyzers.Porter2Filter(tok)
        # analyzer = metapy.analyzers.NGramWordAnalyzer(1, tok)
        return analyzer.analyze(doc)


    def _run_recommendations(self):
        scores_by_new_label_and_seed_label = {}

        total_scores = {}
        max_scores = {}
        num_tweets = {}

        for user, user_tweets in self._new_by_user.items():
            scores_by_new_label_and_seed_label[user] = {}

            total_score = 0.0
            num_tweets[user] = len(user_tweets)
            max_score = -1
            max_label = ''

            for seed_user, seed_tweets in self._seed_by_user.items():
                score = self.score(user_tweets, seed_tweets)
                total_score += score
                scores_by_new_label_and_seed_label[user][seed_user] = score

                if score > max_score:
                    max_score = score
                    max_label = seed_user

            for seed_hashtag, seed_tweets in self._seed_by_hashtag.items():
                score = self.score(user_tweets, seed_tweets)
                total_score += score
                scores_by_new_label_and_seed_label[user][seed_hashtag] = score

                if score > max_score:
                    max_score = score
                    max_label = seed_hashtag

            total_scores[user] = total_score
            max_scores[user] = {'label':max_label, 'score':max_score}

        for hashtag, hashtag_tweets in self._new_by_hashtag.items():
            scores_by_new_label_and_seed_label[hashtag] = {}

            total_score = 0.0
            num_tweets[hashtag] = len(hashtag_tweets)
            max_score = -1
            max_label = ''

            for seed_user, seed_tweets in self._seed_by_user.items():
                score = self.score(hashtag_tweets, seed_tweets)
                total_score += score
                scores_by_new_label_and_seed_label[hashtag][seed_user] = score

                if score > max_score:
                    max_score = score
                    max_label = seed_user

            for seed_hashtag, seed_tweets in self._seed_by_hashtag.items():
                score = self.score(hashtag_tweets, seed_tweets)
                total_score += score
                scores_by_new_label_and_seed_label[hashtag][seed_hashtag] = score

                if score > max_score:
                    max_score = score
                    max_label = seed_hashtag

            total_scores[hashtag] = total_score
            max_scores[hashtag] = {'label':max_label, 'score':max_score}

        results = []
        for label, score in total_scores.items():
            max_score = max_scores[label]
            tweet_num = num_tweets[label]
            results.append({'label': label, 'score': score, 'max_score_label' : max_score['label'],
                            'max_score' : max_score['score'], 'num_tweets': tweet_num})
        return results

    def score(self, new_tweets, seed_tweets):
        score = 0.0
        for new_tweet in new_tweets:
            for seed_tweet in seed_tweets:
                score += self._score_pair(new_tweet, seed_tweet)

        return score/len(new_tweets)

    def _score_pair(self, a, b):
        similarity = self._cosine_similarity(a['text'], b['text'])
        time_multiplier = 1 / (math.log(self._update_timestamp - a['timestamp']) *
                               math.log(self._update_timestamp - b['timestamp']))
        return similarity * time_multiplier

    def _cosine_similarity(self, a, b):
        return self._dict_dot_product(a, b)/ (self._dict_norm(a) * self._dict_norm(b))

    def _dict_dot_product(self, a, b):
        total = 0.0
        for word, count in a.items():
            if word in b:
                total += count * b[word]
        return total

    def _dict_norm(self, a):
        total = 0
        for term, value in a.items():
            total += value*value
        return math.sqrt(total)