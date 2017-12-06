from kafka import KafkaConsumer
import threading
import json
import logging

class KafkaResultListener(threading.Thread):

    def __init__(self, feedback_method):
        super(KafkaResultListener, self, ).__init__()
        self._consumer = KafkaConsumer(bootstrap_servers='localhost:9092', value_deserializer=self.decode_to_json)
        self._feedback_method = feedback_method


    def run(self):
        logging.log(logging.INFO, 'Tweet Recorder starting')

        self._consumer.subscribe(['top_scores', 'all_scores'])

        while True:
            for message in self._consumer:
                topic = message[0] # I hope that doesn't change

                if topic == 'top_scores':
                    self._top_scores(message)
                elif topic == 'all_scores':
                    self._all_scores(message)

                else:
                    print(message)

    def _top_scores(self, message):
        results = message[6]
        feedback = []
        for result in results:
            feedback.append(result['label'])
            print('{}. label: {} score: {} max_score_label: {} max_score: {} num_tweets: {}'.format(
                  result['rank'], result['label'], result['score'],
                  result['max_score_label'], result['max_score'], result['num_tweets']))

        self._feedback_method(feedback)

    def _all_scores(self, message):
        results = message[6]
        logging.log(logging.INFO, 'Received {} results in all_scores'.format(len(results)))

    def decode_to_json(self, value):
        return json.loads(value)