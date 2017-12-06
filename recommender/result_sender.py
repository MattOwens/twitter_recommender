from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging


def all_scores(results):
    _send_results('all_scores', results)

def top_scores(results):
    _send_results('top_scores', results)


def _send_results(topic, results):
    logging.log(logging.INFO, 'Sending result set on {0}'.format(topic))
    future = P.send(topic, value=results)
    P.flush(timeout=30)
    # Block for 'synchronous' sends (I think I did this because sending async wasn't working?)
    try:
        record_metadata = future.get(timeout=10)
    except KafkaError:
        # Decide what to do if produce request failed...
        print('There was an error')
        pass


P = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda x:json.dumps(x).encode('UTF-8'))