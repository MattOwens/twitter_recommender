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
        self.streamListener = TwitterStreamListener(self.usernames)
        self.stream = tweepy.Stream(auth=self.api.auth, listener=self.streamListener,parser=tweepy.parsers.JSONParser())

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
        self.stream.disconnect()
        self.stream.filter(follow=self.user_ids, track=self.hashtags, async=True)


class TwitterStreamListener(tweepy.StreamListener):

    def __init__(self, users):
        tweepy.StreamListener.__init__(self)
        self.users = users

    def on_data(self, data):
        #if status['user']['id_str'] in self.users: # hack until I can figure out how to only subscribe to what I want
        print("Hey I received a streamed tweet! on_data")
        print(json.loads(data))
        sender.send_tweet(json.loads(data)) # send all for now just so I can see messages flowing

    def on_error(self, status_code):
        logging.error('Error in streaming handler: Status code {}'.format(status_code))

        if status_code == 420: # rate limited
            logging.error('Rate limited, disconnecting stream')
            # here I need to make sure the stream doesn't get restarted and set a timer of some sort
            # before allowing it to be restarted
            return False

    def update_users(self, users):
        self.users = users
