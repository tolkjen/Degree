class LRUCache(object):

    class Node(object):
        def __init__(self, key, value):
            self.key = key
            self.value = value

    def __init__(self, n):
        """
        Creates a cache object implementing Least Recently Used algorithm
        :param n: Maximum number of items in cache
        """
        self._n = n
        self._queue = []
        self._hash = {}

    def get(self, key):
        node = self._hash.get(key, None)
        if node:
            self._queue.remove(node)
            self._queue.insert(0, node)
            return node.value
        return None

    def add(self, key, value):
        if not key in self._hash:
            node = LRUCache.Node(key, value)
            self._queue.insert(0, node)
            self._hash[key] = node

            if len(self._queue) > self._n:
                removed_node = self._queue.pop()
                self._hash.pop(removed_node.key, None)


class DummyCache(object):
    def get(self, datafile, preprocessing_descr):
        return None

    def add(self, datafile, preprocessing_descr, sample):
        pass


class SampleCache(object):
    def __init__(self, n=20):
        self._cache_per_file = {}
        self._n = n

    def get(self, datafile, descr):
        cache = self._cache_per_file.get(datafile, None)
        if cache:
            return cache.get(descr)
        return None

    def add(self, datafile, descr, sample):
        cache = self._cache_per_file.get(datafile, None)
        if not cache:
            self._cache_per_file[datafile] = LRUCache(self._n)
            cache = self._cache_per_file[datafile]
        cache.add(descr, sample)
