import os
import sys
import argparse
import matplotlib.pyplot as plt
import numpy as np

from pylab import savefig
from scipy.stats import norm

from mltool.descriptors import *
from mltool.spaces import *
from tools.validate import SpaceDataStore


class Parser(object):
    class SplitAction(argparse.Action):
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            super(Parser.SplitAction, self).__init__(option_strings, dest, nargs, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, values.split(","))

    def __init__(self):
        self._parser = argparse.ArgumentParser()
        self._parser.add_argument("-a", "--action", help="Action (list/plot)", default="list", dest="action")
        self._parser.add_argument("-ids", "--identifiers", help="Space IDs", default=[], dest="ids", action=Parser.SplitAction)
        self._parser.add_argument("-m", "--metric", help="Metric (recall/precision/f1)", default='recall', dest="metric")

    def parse(self, arguments):
        args = self._parser.parse_args(arguments)
        args.ids = [int(x) for x in args.ids]
        return args


def list_objects(requested_ids):
    store = SpaceDataStore('postgresql+psycopg2://guest:guest@localhost/db')
    for space in store.get_spaces():
        id = store.get_id(space)
        if not requested_ids or id in requested_ids:
            scores = store.get_scores(space)
            recall_mean = np.array([score[0] for score in scores]).mean()
            precision_mean = np.array([score[1] for score in scores]).mean()
            f1_mean = np.array([score[2] for score in scores]).mean()

            print 'Id: %d' % store.get_id(space)
            print 'Space: %s' % str(space)
            print 'Length: %d' % len(store.get_scores(space))
            print 'Mean: %0.4f (recall) %0.4f (precision) %0.4f (f1)\n' % (recall_mean, precision_mean, f1_mean)


def plot_distribution(requested_ids, metric):
    if not requested_ids:
        print 'Specify Ids.'
    else:
        index = {
            'recall': 0, 
            'sensivity': 0,
            'precision': 1, 
            'f1': 2
        }[metric]

        store = SpaceDataStore('postgresql+psycopg2://guest:guest@localhost/db')

        for id in requested_ids:
            scores = np.array([score[index] for score in store.get_scores(id=id)])
            scores_n = len(scores)
            mean = scores.mean()
            std = scores.std()

            bins = 50
            if scores_n < 200:
                bins = 10
            elif scores_n < 500:
                bins = 20
            elif scores_n < 2000:
                bins = 30

            n, bins, patches = plt.hist(scores, bins=bins, normed=1, histtype='stepfilled')
            normal_y = norm.pdf(bins, loc=mean, scale=std)
            plt.plot(bins, normal_y, 'r--', linewidth=1.5)
            plt.title('Metric: %s, $\mu=%0.4f,\ \sigma=%0.4f$' % (metric, mean, std))

            if not os.path.exists('plots'):
                os.makedirs('plots')
            savefig('plots/%d-%s.png' % (id, metric), bbox_inches='tight')

            plt.show()


def run(args):
    operations = {
        'list': lambda: list_objects(args.ids),
        'plot': lambda: plot_distribution(args.ids, args.metric)
    }
    if not args.action in operations.keys():
        print 'Incorrect action'
    else:
        operations[args.action]()


if __name__ == '__main__':
    parser = Parser()
    args = parser.parse(sys.argv[1:])
    run(args)
