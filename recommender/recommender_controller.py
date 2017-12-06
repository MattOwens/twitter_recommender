from recommender import new_tweet_loader, analyzer, kafka_tweet_receiver, result_sender
import logging
import time

class RecommenderController:

    def __init__(self, seed_users, seed_hashtags, feedback_num):
        self._feedback_num = feedback_num
        self._loader = new_tweet_loader.NewTweetLoader()
        self._tweet_analyzer = analyzer.TweetAnalyzer(self._loader, seed_users, seed_hashtags)
        self._kafka_receiver = kafka_tweet_receiver.KafkaTweetReceiver(self._loader)
        self._kafka_receiver.start()

    def start(self):
        i = 1 # here there will be a timer call

    def update(self):
        logging.log(logging.INFO, '---------TIMER ELAPSED, TAKING SNAPSHOT----------')

        results = self._tweet_analyzer.update_analysis()

        result_sender.all_scores(results)

        # Collect top results for feedback into system
        logging.log(logging.INFO, 'TOP {} RANKING'.format(self._feedback_num))
        ranking = sorted(results, key=lambda r: r['score'], reverse=True)

        top_scores = ranking[:self._feedback_num]
        for i, result in enumerate(top_scores):
            result['rank'] = i + 1

        result_sender.top_scores(top_scores)