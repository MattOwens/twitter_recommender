import logging
import twitterdata
import time
import sys
import configparser
from recommender import recommender_controller

from db import tweet_recorder

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print('Usage: python twitter_recommender.py config.ini')
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)

    # I want to put all the tweets I get into a database
    recorder = tweet_recorder.TweetRecorder()
    recorder.start()

    config = configparser.ConfigParser()
    config.read(sys.argv[1])
    seed = config['SEED']
    users = seed['SeedUsers'].split(',')
    hashtags = seed['SeedHashtags'].split(',')

    controller = recommender_controller.RecommenderController(users, hashtags)
    controller.start()

    twitterdata.load_config(users, hashtags)

    time.sleep(60)

    logging.log(logging.INFO, '---------TIMER ELAPSED, TAKING SNAPSHOT----------')
    controller.update()