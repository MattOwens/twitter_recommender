from kafka import KafkaConsumer
import threading


class TestTweetConsumer(threading.Thread):

    def run(self):
        print('Consumer starting')
        consumer = KafkaConsumer(bootstrap_servers='localhost:9092')

        consumer.subscribe(['incoming_tweets'])
        print('Subscribed to incoming_tweets')
        while True:
            for message in consumer:
                print('Consumed tweet')
                print(message)