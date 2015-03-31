import argparse
import scipy.stats
import numpy as np
import sys

from mltool.descriptors import *
from mltool.spaces import *
from tools.validate import SpaceDataStore


class Parser(object):
    def __init__(self):
        self._parser = argparse.ArgumentParser()
        self._parser.add_argument("-p", "--propability", help="Propability", default=0.05, dest="propability")
        self._parser.add_argument("-o", "--orderby", help="Ordering scheme (r/p/r+p/f1)", default='r', dest="orderby")
        self._parser.add_argument('-d', '--detailed', help='Detailed view', action='store_true', dest='detailed')
        self._parser.add_argument("-c", "--count", help="Number of results printed", default=10**6, dest="count")

    def parse(self, arguments):
        args = self._parser.parse_args(arguments)
        args.propability = float(args.propability)
        args.count = int(args.count)
        return args


class MethodInfo(object):
    def __init__(self, scores):
        self.scores = np.array(scores)
        self.mean = self.scores.mean()
        self.better_than = []
        self.rank = 0


class ScoreInfo(object):
    def __init__(self, id, space, scores):
        self.id = id
        self.space = space
        self.recall = MethodInfo([score[0] for score in scores])
        self.precision = MethodInfo([score[1] for score in scores])
        self.f1 = MethodInfo([score[2] for score in scores])


def load_scores(store):
    spaces = store.get_spaces()
    return [ScoreInfo(store.get_id(space), space, store.get_scores(space)) for space in spaces]


def calculate_method_ranks(space_information, method_selector):
    def comparer(a, b):
        m_a = method_selector(a)
        m_b = method_selector(b)
        return len(m_b.better_than) - len(m_a.better_than)

    for i in xrange(len(space_information)):
        for j in xrange(i + 1, len(space_information)):
            info_a = space_information[i]
            info_b = space_information[j]
            method_a = method_selector(info_a)
            method_b = method_selector(info_b)

            z, p_val = scipy.stats.ranksums(method_a.scores, method_b.scores)
            if p_val < p:
                if method_a.mean > method_b.mean:
                    method_a.better_than.append(info_b)
                else:
                    method_b.better_than.append(info_a)

    space_information = sorted(space_information, comparer)

    for i in xrange(len(space_information)):
        info = space_information[i]
        method = method_selector(info)
        method.rank = i


def get_rank_comparer(ordering):
    def rank_compare(a, b):
        return {
            'r': lambda x, y: x.recall.rank - y.recall.rank,
            'p': lambda x, y: x.precision.rank - y.precision.rank,
            'r+p': lambda x, y: x.recall.rank+x.precision.rank - y.recall.rank-y.precision.rank,
            'f1': lambda x, y: x.f1.rank - y.f1.rank
        }[ordering](a, b)
    return rank_compare


if __name__ == '__main__':
    parser = Parser()
    arguments = parser.parse(sys.argv[1:])
    p = arguments.propability

    store = SpaceDataStore('postgresql+psycopg2://guest:guest@localhost/db')

    print 'Loading scores from database...'
    space_information = load_scores(store)
    print 'Done. Comparing results...'

    if space_information:
        calculate_method_ranks(space_information, lambda info: info.recall)
        calculate_method_ranks(space_information, lambda info: info.precision)
        calculate_method_ranks(space_information, lambda info: info.f1)

        space_information = sorted(space_information, get_rank_comparer(arguments.orderby))

        for info in space_information[:arguments.count]:
            r, p, f1 = info.recall.rank, info.precision.rank, info.f1.rank
            rp = r + p

            print '\nId: %d' % store.get_id(info.space)
            print info.space
            print 'Ranks: %d (recall) %d (precision) %d (r+p) %d (f1)' % (r, p, rp, f1)
            if arguments.detailed:
                print 'Mean: %0.4f (recall) %0.4f (precision) %0.4f (f1)' % (
                    info.recall.mean, info.precision.mean, info.f1.mean)
                print 'Better than:'
                print '  - recall:', ','.join([str(x.id) for x in info.recall.better_than])
                print '  - precision:', ','.join([str(x.id) for x in info.precision.better_than])
                print '  - f1:', ','.join([str(x.id) for x in info.f1.better_than])