import os

data_directory = os.path.join(os.path.dirname(__file__), 'tweet_data')
tweet_path = os.path.join(data_directory, 'tweet_data.dat')
metadata_path = os.path.join(data_directory, 'metadata.dat')

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

        self._update_corpus(by_user, by_hashtag)

    def _update_corpus(self, by_user, by_hashtag):
        # intentionally duplicates tweets - will help with similarity when we have multiple hashtags in the same tweet
        # or when a user we care about uses a hashtag we care about
        with open(tweet_path, 'a+') as tweet_data, \
                open(metadata_path, 'a+') as metadata:
            for user in by_user:
                for tweet in by_user[user]:
                    text = tweet['full_text'] if 'full_text' in tweet else tweet['text']
                    tweet_data.write(text.replace('\n', ' ') + '\n')
                    metadata.write('{}\t{}\n'.format(tweet['user']['id_str'], tweet['created_at']))
            for hashtag in by_hashtag:
                for tweet in by_hashtag[hashtag]:
                    text = tweet['full_text'] if 'full_text' in tweet else tweet['text']
                    tweet_data.write(text.replace('\n', ' ') + '\n')
                    metadata.write('{}\t{}\n'.format(hashtag, tweet['created_at']))

