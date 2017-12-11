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
        self._seed_tweets = {}
        self._new_tweets = {}

    def update_analysis(self):
        self._update_timestamp = time.time()
        snapshot = self._loader.get_snapshot()
        all_tweets = snapshot[0]

        self._update_corpus(all_tweets)
        return self._run_recommendations()

    def _update_corpus(self, tweets):
        # intentionally duplicates tweets - will help with similarity when we have multiple hashtags in the same tweet
        # or when a user we care about uses a hashtag we care about

        for tweet in tweets:
            user = tweet['user']['screen_name'].lower()
            timestamp = datetime.datetime.strptime(tweet['created_at'], date_format).timestamp()
            text = self._prepare_tweet_text(tweet)
            self._add_tweet({'text':text, 'label':user, 'timestamp':timestamp})

            for entity in tweet['entities']['hashtags']:
                hashtag = entity['text'].lower()
                self._add_tweet({'text':text, 'label':'#{}'.format(hashtag), 'timestamp':timestamp})

    def _add_tweet(self, tweet):
        label = tweet['label']

        if label in self._seed_users or label in self._seed_hashtags:
            if label not in self._seed_tweets:
                self._seed_tweets[label] = []
            self._seed_tweets[label].append(tweet)
        else:
            if label not in self._new_tweets:
                self._new_tweets[label] = []
            self._new_tweets[label].append(tweet)

    def _prepare_tweet_text(self, tweet):
        doc = metapy.index.Document()
        doc.content(tweet['full_text'] if 'full_text' in tweet else tweet['text'])

        return analyzer.analyze(doc)

    def _run_recommendations(self):
        scores_by_new_label_and_seed_label = {}

        total_scores = {}
        max_scores = {}
        num_tweets = {}

        for label, new_tweets in self._new_tweets.items():
            scores_by_new_label_and_seed_label[label] = {}

            total_score = 0.0
            num_tweets[label] = len(new_tweets)
            max_score = -1
            max_label = ''

            for seed_label, seed_tweets in self._seed_tweets.items():
                score = self.score(new_tweets, seed_tweets)
                total_score += score
                scores_by_new_label_and_seed_label[label][seed_label] = score

                if score > max_score:
                    max_score = score
                    max_label = seed_label

            total_scores[label] = total_score
            max_scores[label] = {'label':max_label, 'score':max_score}

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

        # Make it so low tweet numbers aren't completely buried, but there's some value in having many
        # tweets for a label. Labels with 1 tweet are divided by 1.
        return score/math.log(len(new_tweets) - 1 + math.e)

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