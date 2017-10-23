import tweepy
import twitterdata.tweet_sender as sender


class StreamLoader():

    def __init__(self, api):
        self.api = api
        self.streamingUsers = []
        self.streamListener = TwitterStreamListener(self.streamingUsers)
        self.stream = tweepy.Stream(auth=self.api.auth, listener=self.streamListener)

    def update_users(self, usernames):
        self.streamingUsers = [user['id_str'] for user in self.api.lookup_users(screen_names=usernames)]
        print(self.streamingUsers)
        self._start_stream() # need to check this, since it might not work if you update users more than once

    def _start_stream(self):
        self.stream.filter(follow=self.streamingUsers, async=True)


class TwitterStreamListener(tweepy.StreamListener):

    def __init__(self, users):
        tweepy.StreamListener.__init__(self)
        self.users = users

    def on_status(self, status):
        #if status['user']['id_str'] in self.users: # hack until I can figure out how to only subscribe to what I want
        sender.send_tweet(status) # send all for now just so I can see messages flowing

    def update_users(self, users):
        self.users = users
