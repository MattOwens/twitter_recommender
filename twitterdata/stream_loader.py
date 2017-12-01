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
        self.streamListener = TwitterStreamListener(self.usernames)
        self.stream = tweepy.Stream(auth=self.api.auth, listener=self.streamListener,parser=tweepy.parsers.JSONParser())

    def add_user(self, user):
        self.usernames.append(user)
        self.user_ids = [user['id_str'] for user in self.api.lookup_users(screen_names=self.usernames)]
        logging.log(logging.INFO, 'Updating users to {} {}'.format(self.user_ids, self.usernames))
        self._start_stream()

    def add_hashtag(self, hashtag):
        hashtags = self.hashtags
        hashtags.append(hashtag)
        logging.log(logging.INFO, 'Updating hashtags to {}'.format(self.hashtags))
        self._start_stream()

    def _start_stream(self):
        self.stream.disconnect()
        self.stream.filter(follow=self.user_ids, track=self.hashtags, async=True)

    # def update_hashtags(self, hashtags):
    #     self.hashtag_stream.disconnect()
    #     self.hashtag_stream.filter(track=hashtags, async=True)


class TwitterStreamListener(tweepy.StreamListener):

    def __init__(self, users):
        tweepy.StreamListener.__init__(self)
        self.users = users

    # def on_status(self, status):
    #    #if status['user']['id_str'] in self.users: # hack until I can figure out how to only subscribe to what I want
    #    print("Hey I received a streamed tweet! on_status")
    #    print(status)
    #    sender.send_tweet(status) # send all for now just so I can see messages flowing

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
