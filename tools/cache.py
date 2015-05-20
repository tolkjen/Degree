from mltool.input.xlsfile import XlsFile

class LRUCache(object):
    """
    Least Recently Used algorithm.
    """
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


class Cache(object):
    def __init__(self, n):
        self._cache = LRUCache(n)

    def contains(self, checksum, splits, pd):
        return not self.get(checksum, splits, pd) is None

    def set(self, checksum, splits, pd, value):
        key = (str(checksum), str(splits), str(pd))
        self._cache.add(key, value)

    def get(self, checksum, splits, pd):
        key = (str(checksum), str(splits), str(pd))
        return self._cache.get(key)


class FileCache(object):
    def __init__(self):
        self._cache = {}
    
    def get(self, filepath):
        if not filepath in self._cache:
            xls = XlsFile(filepath)
            xls.read()
            self._cache[filepath] = xls
            return xls
        return self._cache[filepath]
