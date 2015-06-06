class LRUCache(object):
    class Node(object):
        def __init__(self, key, value):
            self.key = key
            self.value = value

    def __init__(self, n):
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