import configparser
from twitterdata import kafka_tweet_sender


class RunConfig:

    def __init__(self, filename):
        config = configparser.ConfigParser()
        config.read(filename)

        # Seed is required
        seed = config['SEED']
        self.seed_users = seed['SeedUsers'].split(',')
        self.seed_hashtags = seed['SeedHashtags'].split(',')

        # Controller is also required
        controller_conifg = config['CONTROLLER']
        self.refresh_period = int(controller_conifg['RefreshPeriod'])
        self.feedback_num = int(controller_conifg['FeedbackNum'])

        # Delivery is also required
        delivery = config['DELIVERY']

        # But each attribute is not - defaults to direct
        self.tweet_sender = 'Direct' if 'Sender' not in delivery else delivery['Sender']
        self.recorder = None if 'Recorder' not in delivery else delivery['Recorder']
        self.results = 'Direct' if 'Results' not in delivery else delivery['Results']

    def get_tweet_sender(self):
        if self._tweet_sender == 'Kafka':
            return kafka_tweet_sender.send_tweet
        elif  self._tweet_sender == 'Direct':
            return