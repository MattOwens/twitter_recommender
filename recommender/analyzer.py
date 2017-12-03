class TweetAnalyzer: # come up with better name

    def __init__(self, loader, seed_users, seed_hashtags):
        self._loader = loader
        self._seed_users = seed_users
        self._seed_hashtags = seed_hashtags

    def update_analysis(self):
        snapshot = self._loader.get_snapshot()
        all_tweets = snapshot[0]
        by_user = snapshot[1]
        by_hashtag = snapshot[2]

        # first pull out hashtags and user mentions so we know what to look at next
        users_mentioned = set()
        hashtags_used = set()

        for tweet in all_tweets:
            mentions = tweet['entities']['user_mentions']
            for mention in mentions:
                users_mentioned.add(mention['id'])
            hashtags = tweet['entities']['hashtags']

            for hashtag in hashtags:
                hashtags_used.add('#{}'.format(hashtag['text']))

        print('Users mentioned in this snapshot: ', users_mentioned)
        print('Hashtags used in this snapshot: ', hashtags_used)
