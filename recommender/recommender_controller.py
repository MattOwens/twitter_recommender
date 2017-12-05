from recommender import new_tweet_loader, analyzer, kafka_tweet_receiver
import logging
import time

class RecommenderController:

    def __init__(self, seed_users, seed_hashtags):
        self._loader = new_tweet_loader.NewTweetLoader()
        self._tweet_analyzer = analyzer.TweetAnalyzer(self._loader, seed_users, seed_hashtags)
        self._kafka_receiver = kafka_tweet_receiver.KafkaTweetReceiver(self._loader)

    def start(self):
        self._kafka_receiver.start()

    def update(self):
        logging.log(logging.INFO, '---------TIMER ELAPSED, TAKING SNAPSHOT----------')

        results = self._tweet_analyzer.update_analysis()
        for result in results:
            print('label: {} score: {} max_score_label: {} max_score: {} num_tweets: {}'.format(
                  result['label'], result['score'],
                  result['max_score_label'], result['max_score'], result['num_tweets']))