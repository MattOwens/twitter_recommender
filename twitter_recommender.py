import logging
import twitterdata
import time
import sys
import configparser
from recommender import recommender_controller
from result_handlers import kafka_result_listener

from db import tweet_recorder

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print('Usage: python twitter_recommender.py config.ini')
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)

    # I want to put all the tweets I get into a database
    tweet_rec = tweet_recorder.TweetRecorder()
    tweet_rec.start()

    result_rec = kafka_result_listener.KafkaResultListener(twitterdata.give_feedback)
    result_rec.start()

    config = configparser.ConfigParser()
    config.read(sys.argv[1])
    seed = config['SEED']
    users = seed['SeedUsers'].split(',')
    hashtags = seed['SeedHashtags'].split(',')

    controller_conifg = config['CONTROLLER']
    refresh_period = int(controller_conifg['RefreshPeriod'])
    feedback_num = int(controller_conifg['FeedbackNum'])

    controller = recommender_controller.RecommenderController(users, hashtags, feedback_num)
    controller.start()

    twitterdata.load_config(users, hashtags)

    while True:
        time.sleep(refresh_period)
        controller.update()