import tweepy
import json
import logging
import twitterdata.tweet_sender as sender


class StreamLoader():

    def __init__(self, api):
        self.api = api
        self.usernames = []
        self.user_ids = []
        self.hashtags = []
        self._requests_paused = False
        self.stream_listener = TwitterStreamListener()
        self.stream = tweepy.Stream(auth=self.api.auth, listener=self.stream_listener, parser=tweepy.parsers.JSONParser())

    def start_batch_update(self):
        logging.log(logging.INFO, 'stream loader paused for batch update')
        self._requests_paused = True

    def finish_batch_update(self):
        logging.log(logging.INFO, 'stream loader restarting after batch update')
        self._requests_paused = False
        self._start_stream()

    def add_user(self, user):
        self.usernames.append(user)
        logging.log(logging.INFO, 'Updating users to {} {}'.format(self.user_ids, self.usernames))
        self._subscription_refresh()

    def add_hashtag(self, hashtag):
        self.hashtags.append(hashtag)
        logging.log(logging.INFO, 'Updating hashtags to {}'.format(self.hashtags))
        self._subscription_refresh()

    def _subscription_refresh(self):
        if not self._requests_paused:
            self._start_stream()

    def _start_stream(self):
        self.user_ids = [user['id_str'] for user in self.api.lookup_users(screen_names=self.usernames)]
        self.stream_listener.update_users(self.user_ids)
        self.stream_listener.update_hashtags(self.hashtags)
        self.stream.disconnect()
        self.stream.filter(follow=self.user_ids, track=self.hashtags, async=True)


class TwitterStreamListener(tweepy.StreamListener):

    def __init__(self):
        tweepy.StreamListener.__init__(self)
        self._user_ids = []
        self._hashtags = []

    def on_data(self, data):
        print("Hey I received a streamed tweet! on_data")
        print(json.loads(data))
        relevant = self._is_relevant(json.loads(data))
        
        if relevant:
            sender.send_tweet(json.loads(data))

    def on_error(self, status_code):
        logging.error('Error in streaming handler: Status code {}'.format(status_code))

        if status_code == 420: # rate limited
            logging.error('Rate limited, disconnecting stream')
            # here I need to make sure the stream doesn't get restarted and set a timer of some sort
            # before allowing it to be restarted
            return False

    def update_users(self, users):
        self._user_ids = users

    def update_hashtags(self, hashtags):
        self._hashtags = hashtags

    def _is_relevant(self, tweet):
        if tweet['user']['id'] in self._user_ids:
            return True

        for entity in tweet['entities']['hashtags']:
            hashtag = '#{}'.format(entity['text'])
            logging.log(logging.INFO, 'Tweet {} has hashtag {}'.format(tweet['id'], hashtag))
            if hashtag in self._hashtags:
                return True

        return False
