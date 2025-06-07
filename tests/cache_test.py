#!/usr/bin/env python

import unittest

from bardolph.lib.cache import Cache

class CacheTest(unittest.TestCase):
    def test_hits(self):
        cache = Cache(3)

        obj0 = "obj0"
        obj1 = "obj1"
        obj2 = "obj2"
        obj3 = "obj3"

        cache.put(hash(obj0), obj0)
        cache.put(hash(obj1), obj1)
        cache.put(hash(obj2), obj2)

        self.assertEqual(cache.get(hash(obj0)), obj0)
        self.assertEqual(cache.get(hash(obj1)), obj1)
        self.assertEqual(cache.get(hash(obj2)), obj2)
        self.assertIsNone(cache.get(hash(obj3)))

    def test_lru_eviction(self):
        cache = Cache(3)

        obj0 = "obj0"
        obj1 = "obj1"
        obj2 = "obj2"
        obj3 = "obj3"

        cache.put(hash(obj0), obj0)
        cache.put(hash(obj1), obj1)
        cache.put(hash(obj2), obj2)

        self.assertEqual(cache.get(hash(obj0)), obj0)
        self.assertEqual(cache.get(hash(obj1)), obj1)
        self.assertEqual(cache.get(hash(obj2)), obj2)

        self.assertEqual(cache.get(hash(obj0)), obj0)
        self.assertEqual(cache.get(hash(obj1)), obj1)
        # Don't get ob2, making it LRU.

        cache.put(hash(obj3), obj3)
        self.assertEqual(cache.get(hash(obj3)), obj3)
        self.assertIsNone(cache.get(hash(obj2)))


if __name__ == '__main__':
    unittest.main()
