import logging
import twitterdata
import time
import sys
from recommender import recommender_controller, kafka_result_sender, direct_result_sender
from result_handlers import kafka_result_listener
from run_config import RunConfig

from db import tweet_recorder

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print('Usage: python twitter_recommender.py kafka_config.ini')
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)

    config = RunConfig(sys.argv[1])
    users = config.seed_users
    hashtags = config.seed_hashtags

    refresh_period = config.refresh_period
    feedback_num = config.feedback_num

    if config.recorder == 'Mongo':
        tweet_rec = tweet_recorder.TweetRecorder()
        tweet_rec.start()

    result_sender = direct_result_sender
    if config.results == 'Kafka':
        result_rec = kafka_result_listener.KafkaResultListener(twitterdata.give_feedback)
        result_rec.start()
        result_sender = kafka_result_sender

    controller = recommender_controller.RecommenderController(users, hashtags, feedback_num, result_sender)

    if config.tweet_sender == 'Kafka':
        controller.start_kafka_receiver()

    controller.start()

    twitterdata.load_config(users, hashtags, config.tweet_sender)

    while True:
        time.sleep(refresh_period)
        controller.update()