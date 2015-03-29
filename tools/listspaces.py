from mltool.descriptors import *
from mltool.spaces import *
from tools.validate import SpaceDataStore


if __name__ == '__main__':
    store = SpaceDataStore('postgresql+psycopg2://guest:guest@localhost/db')
    for space in store.get_spaces():
        scores = store.get_scores(space)
        latest, ranges = store.get_retry_info(space)
        print '%s (LENGTH: %d)' % (str(space), len(scores))
        print ''
        print scores
        print ''