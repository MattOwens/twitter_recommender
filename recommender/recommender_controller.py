from recommender import new_tweet_loader, analyzer, kafka_tweet_receiver, kafka_result_sender
import logging
import time


class RecommenderController:

    def __init__(self, seed_users, seed_hashtags, feedback_num, result_sender):
        self._feedback_num = feedback_num
        self._loader = new_tweet_loader.NewTweetLoader()
        self._tweet_analyzer = analyzer.TweetAnalyzer(new_tweet_loader.instance, seed_users, seed_hashtags)
        self._result_sender = result_sender

    def start_kafka_receiver(self):
        self._kafka_receiver = kafka_tweet_receiver.KafkaTweetReceiver(new_tweet_loader.instance)
        self._kafka_receiver.start()

    def start(self):
        i = 1 # here there will be a timer call

    def update(self):
        logging.log(logging.INFO, '---------TIMER ELAPSED, TAKING SNAPSHOT----------')

        results = self._tweet_analyzer.update_analysis()

        self._result_sender.all_scores(results)

        # Collect top results for feedback into system
        logging.log(logging.INFO, 'TOP {} RANKING'.format(self._feedback_num))
        ranking = sorted(results, key=lambda r: r['score'], reverse=True)

        top_scores = ranking[:self._feedback_num]
        for i, result in enumerate(top_scores):
            result['rank'] = i + 1

        self._result_sender.top_scores(top_scores)