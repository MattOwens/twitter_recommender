import logging
import twitterdata
def all_scores(results):
    logging.log(logging.INFO, 'Received {} results in all_scores'.format(len(results)))

def top_scores(results):
    feedback = []
    for result in results:
        feedback.append(result['label'])
        print('{}. label: {} score: {} max_score_label: {} max_score: {} num_tweets: {}'.format(
            result['rank'], result['label'], result['score'], result['max_score_label'],
            result['max_score'],result['num_tweets']))
