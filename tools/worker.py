import celery
import os
import hashlib

from datetime import datetime
from numpy.random import RandomState
from sklearn.cross_validation import StratifiedKFold

from mltool.input.sample import Sample
from cache import Cache, FileCache


def get_queue_url():
    """
    Returns a URL to the message broker server. The URL is configured via 
    QUEUE_URL environment variable. In absence of such variable returns a fixed 
    URL.
    """
    return os.environ.get('QUEUE_URL', 'amqp://guest@localhost//')


def get_splits(xls, random_state):
    """
    Generates multiple training/test group partitioning.
    :param xls: XlsFile containing data.
    :param random_state: RandomState object used to create random partitioning.
    :returns: List of tuples (s, t) where s is a list of training indices and t
    is a list of test indices.
    """
    r = RandomState()
    r.set_state(random_state.get_state())
    sample = Sample.from_file(xls)
    folds = StratifiedKFold(sample.categories, n_folds=10, shuffle=True, random_state=r)
    return [(train.tolist(), test.tolist()) for train, test in folds]


def file_checksum(filepath):
    """
    Returns a MD5 checksum of file contents.
    """
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def get_scores(clf, training_sample, test_sample):
    """
    Calculates classification quality metrics.
    :param clf: Classifier instance.
    :param training_sample: Sample instance containing data used for training.
    :param test_sample: Sample instance containing data used for classifier 
    evaluation.
    :returns: A tuple (s, p, f) where s is sensitivity, p is precision and f
    is F1 measure.
    """
    clf.fit(training_sample.attributes, training_sample.categories)
    prediction = clf.predict(test_sample.attributes)
    truth = test_sample.categories

    tp, tn, fp, fn = 0, 0, 0, 0
    for i in xrange(len(truth)):
        tp += truth[i] and prediction[i]
        fp += not truth[i] and prediction[i]
        fn += truth[i] and not prediction[i]

    precision = float(tp) / (tp + fp)
    sensivity = float(tp) / (tp + fn)
    f1 = 2.0*tp / (2.0*tp + fp + fn)

    return [sensivity, precision, f1]


file_cache = FileCache()
sample_cache = Cache(100)
app = celery.Celery('tasks')
app.conf.update(BROKER_URL=get_queue_url(),
                CELERY_RESULT_BACKEND=get_queue_url(),
                CELERY_ACCEPT_CONTENT=['pickle'],
                #CELERY_TASK_SERIALIZER='json',
                CELERY_TRACK_STARTED=True,
                CELERYD_PREFETCH_MULTIPLIER=1,
                BROKER_POOL_LIMIT=50)

@app.task
def evaluate(filepath, random_state, pairs):
    """
    Read a given file, evaluate multiple preprocessing/classification algorithms 
    and return aggregated evaluation results.
    :param filepath: Data file path.
    :param random_state: RandomState used for training/test partitioning.
    :param pairs: List of DescriptorPairs describing preprocessing and
    classification.
    :returns: List of tuples (s, p, f). See get_scores().
    """
    dt_started = datetime.now()
    print 'Work started'

    checksum = file_checksum(filepath)
    xls = file_cache.get(filepath)

    scores = []
    splits = get_splits(xls, random_state)
    for pair in pairs:
        pd = pair.preprocessing_descriptor
        for split in splits:
            if not sample_cache.contains(checksum, split, pd):
                training, test = split

                # Training
                training_sample = Sample.from_file(xls, training)
                imputer = pd.impute(training_sample)
                training_sample.impute_nan(imputer)
                training_sample.remove_columns(pd.removed_columns)
                normalizer = training_sample.get_normalizer()
                training_sample.normalize(normalizer, pd.normalized_columns)
                clusterer = pd.cluster(training_sample)
                training_sample.merge(clusterer)

                # Test
                test_sample = Sample.from_file(xls, test)
                test_sample.impute_nan(imputer)
                test_sample.remove_columns(pd.removed_columns)
                test_sample.normalize(normalizer, pd.normalized_columns)
                test_sample.merge(clusterer)

                sample_cache.set(checksum, split, pd, (training_sample, test_sample))
            else:
                training_sample, test_sample = sample_cache.get(checksum, split, pd)

            clf = pair.classification_descriptor.create_classifier(training_sample)
            scores.append(get_scores(clf, training_sample, test_sample))

    print 'Work finished (%d)' % (datetime.now() - dt_started).total_seconds()
    return scores
