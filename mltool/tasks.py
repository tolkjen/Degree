import celery
import os
from datetime import datetime

from crossvalidation import CrossValidator
from input.xlsfile import XlsFile
from cache import SampleCache

class FileCache(object):

    _cache = {}
     
    @staticmethod
    def get(filepath):
        if not filepath in FileCache._cache:
            xls = XlsFile(filepath)
            xls.read()
            FileCache._cache[filepath] = xls
            return xls
        return FileCache._cache[filepath]

def get_queue_url():
    url = os.environ.get('QUEUE_URL', None)
    if not url:
        return os.environ.get('RABBITMQ_BIGWIG_URL', 'amqp://guest@localhost//')
    return url

sample_cache = SampleCache(5)

app = celery.Celery('tasks')
app.conf.update(BROKER_URL=get_queue_url(),
                CELERY_RESULT_BACKEND=get_queue_url(),
                CELERY_ACCEPT_CONTENT=['pickle'],
                #CELERY_TASK_SERIALIZER='json',
                CELERY_TRACK_STARTED=True,
                CELERYD_PREFETCH_MULTIPLIER=1,
                BROKER_POOL_LIMIT=50)

@app.task
def validate(filepath, random_state, test_ratio, pairs):
    dt_started = datetime.now()
    print 'Work started'

    xls = FileCache.get(filepath)
    cross_validator = CrossValidator(random_state, iterations=1)

    best_score = 0
    best_pair = None

    for pair in pairs:
        sample = pair.preprocessing_descriptor.generate_sample(xls, sample_cache)
        evaluation_sample, test_sample = sample.split(random_state, test_ratio=test_ratio)

        classifier = pair.classification_descriptor.create_classifier(evaluation_sample)
        score = cross_validator.validate(evaluation_sample, classifier)

        if score > best_score:
            best_score = score
            best_pair = pair.copy()

    print 'Work finished (%d)' % (datetime.now() - dt_started).total_seconds()

    return (best_score, best_pair)
