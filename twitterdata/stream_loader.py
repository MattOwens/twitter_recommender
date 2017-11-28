import tweepy
import json
import twitterdata.tweet_sender as sender


class StreamLoader():

    def __init__(self, api):
        self.api = api
        self.streamingUsers = []
        self.hashtags = []
        self.streamListener = TwitterStreamListener(self.streamingUsers)
        self.stream = tweepy.Stream(auth=self.api.auth, listener=self.streamListener,parser=tweepy.parsers.JSONParser())
        self.hashtag_stream = tweepy.Stream(auth=self.api.auth, listener=self.streamListener,parser=tweepy.parsers.JSONParser()) #two streams at once?

    def add_user(self, user):
        users = self.streamingUsers
        users.append(user)
        self.update_users(users)

    def update_users(self, usernames):
        self.streamingUsers = [user['id_str'] for user in self.api.lookup_users(screen_names=usernames)]
        self.stream.disconnect() #need a better way to do this, but it'll do for now
        self._start_stream() # need to check this, since it might not work if you update users more than once

    def _start_stream(self):
        self.stream.filter(follow=self.streamingUsers, async=True)

    def add_hashtag(self, hashtag):
        hashtags = self.hashtags
        hashtags.append(hashtag)
        self.update_hashtags(hashtags)

    def update_hashtags(self, hashtags):
        self.hashtag_stream.disconnect()
        self.hashtag_stream.filter(track=hashtags, async=True)


class TwitterStreamListener(tweepy.StreamListener):

    def __init__(self, users):
        tweepy.StreamListener.__init__(self)
        self.users = users

    def on_status(self, status):
        #if status['user']['id_str'] in self.users: # hack until I can figure out how to only subscribe to what I want
        print("Hey I received a streamed tweet! on_status")
        print(status)
        sender.send_tweet(status) # send all for now just so I can see messages flowing

    def on_data(self, data):
        #if status['user']['id_str'] in self.users: # hack until I can figure out how to only subscribe to what I want
        print("Hey I received a streamed tweet! on_data")
        print(json.loads(data))
        sender.send_tweet(json.loads(data)) # send all for now just so I can see messages flowing

    def update_users(self, users):
        self.users = users
