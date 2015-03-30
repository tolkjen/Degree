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
    def __init__(self):
        self._parser = argparse.ArgumentParser()
        self._parser.add_argument("-a", "--action", help="Action (list/plot)", default="list", dest="action")
        self._parser.add_argument("-id", "--id", help="Space ID", default=-1, dest="id")
        self._parser.add_argument("-m", "--metric", help="Metric (recall/precision/f1)", default='recall', dest="metric")

    def parse(self, arguments):
        args = self._parser.parse_args(arguments)
        args.id = int(args.id)
        return args


def list_objects():
    store = SpaceDataStore('postgresql+psycopg2://guest:guest@localhost/db')
    for space in store.get_spaces():
        print 'Id: %d' % store.get_id(space)
        print 'Space: %s' % str(space)
        print 'Length: %d' % len(store.get_scores(space))
        print ''


def plot_distribution(id, metric):
    if id == -1:
        print 'Specify Id.'
    else:
        index = {
            'recall': 0, 
            'sensivity': 0,
            'precission': 1, 
            'f1': 2
        }[metric]

        store = SpaceDataStore('postgresql+psycopg2://guest:guest@localhost/db')
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
        'list': lambda: list_objects(),
        'plot': lambda: plot_distribution(args.id, args.metric)
    }
    if not args.action in operations.keys():
        print 'Incorrect action'
    else:
        operations[args.action]()


if __name__ == '__main__':
    parser = Parser()
    args = parser.parse(sys.argv[1:])
    run(args)
