import tweepy


class StreamLoader():

    def __init__(self, api):
        self.api = api
        self.streamingUsers = []
        self.streamListener = TwitterStreamListener(self.streamingUsers)
        self.stream = tweepy.Stream(auth=self.api.auth, listener=self.streamListener)
        self._start_stream()

    def update_users(self, usernames):
        self.streamingUsers = [user.id_str for user in self.api.lookup_users(screen_names=usernames)]
        self.streamListener
        print(self.streamingUsers)
        self._start_stream()

    def _start_stream(self):
        self.stream.filter(follow=self.streamingUsers, async=True)


class TwitterStreamListener(tweepy.StreamListener):

    def __init__(self, users):
        tweepy.StreamListener.__init__(self)
        self.users = users

    def on_status(self, status):
        if status.user.id_str in self.users: # hack until I can figure out how to only subscribe to what I want
            self._send_tweet(status)

    def update_users(self, users):
        self.users = users

    def _send_tweet(self, status):
        print('Streamed tweet received:')
        print('\t', status)