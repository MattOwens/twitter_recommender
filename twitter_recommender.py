import logging
import twitterdata
from db import tweet_recorder

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # I want to put all the tweets I get into a database
    recorder = tweet_recorder.TweetRecorder()
    recorder.start()

    twitterdata.stream.start_batch_update()
    twitterdata.subscribe_user("SenToomey")
    twitterdata.subscribe_user("daylinLeach")
    twitterdata.subscribe_user("POTUS")
    twitterdata.subscribe_user("realDonaldTrump")

    twitterdata.subscribe_hashtag("#netneutrality")
    twitterdata.subscribe_hashtag("#savetheinternet")
    twitterdata.stream.finish_batch_update()