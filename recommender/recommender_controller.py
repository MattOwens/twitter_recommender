from recommender import new_tweet_loader, analyzer, kafka_tweet_receiver


class RecommenderController:

    def __init__(self, seed_users, seed_hashtags):
        self._loader = new_tweet_loader.NewTweetLoader()
        self._tweet_analyzer = analyzer.TweetAnalyzer(self._loader, seed_users, seed_hashtags)
        self._kafka_receiver = kafka_tweet_receiver.KafkaTweetReceiver(self._loader)

    def start(self):
        self._kafka_receiver.start()

    def update(self):
        self._tweet_analyzer.update_analysis()