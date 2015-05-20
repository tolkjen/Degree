from ..cache import LRUCache, Cache
from mltool.descriptors import PreprocessingDescriptor

def test_lru_add():
    cache = LRUCache(5)
    for i in xrange(10):
        cache.add(i, i)

    for i in xrange(0, 5):
        assert cache.get(i) == None
    for i in xrange(5, 10):
        assert cache.get(i) == i

def test_lru_multiple_add():
    cache = LRUCache(5)
    for i in xrange(5):
        cache.add(i, i)
    cache.add(0, 0)

    for i in xrange(0, 5):
        assert cache.get(i) == i

def test_cache():
    cache = Cache(10)
    pd = PreprocessingDescriptor()
    checksum = "!@#"
    splits = [[], []]

    assert not cache.contains(checksum, splits, pd)
    cache.set(checksum, splits, pd, "cat")
    assert cache.get(checksum, splits, pd) == "cat"
