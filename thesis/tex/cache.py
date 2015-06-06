class Cache(object):
    def __init__(self, n):
        self._cache = LRUCache(n)

    def contains(self, checksum, split, pd):
        return not self.get(checksum, split, pd) is None

    def set(self, checksum, split, pd, value):
        key = (str(checksum), str(split), str(pd))
        self._cache.add(key, value)

    def get(self, checksum, split, pd):
        key = (str(checksum), str(split), str(pd))
        return self._cache.get(key)