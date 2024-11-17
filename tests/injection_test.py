#!/usr/bin/env python

import unittest

from bardolph.lib import injection


class Interface: pass

class Impl1:
    def f(self): return 1

class Impl2:
    def f(self): return 2

class ImplN:
    def __init__(self, n):
        self.n = n

    def f(self):
        return self.n


@injection.inject(Interface)
def call_impl(intf):
    return intf.f()


def call_impl_provided():
    intf = injection.provide(Interface)
    return intf.f()


class InjectionTest(unittest.TestCase):
    def test_simple(self):
        injection.configure()
        injection.bind(Impl1).to(Interface)
        self.assertEqual(1, call_impl())

        injection.configure()
        injection.bind(Impl2).to(Interface)
        self.assertEqual(2, call_impl())

    def test_object(self):
        injection.configure()
        injection.bind_instance(ImplN(5)).to(Interface)
        self.assertEqual(5, call_impl())

    def test_provide(self):
        injection.configure()
        injection.bind(Impl1).to(Interface)
        self.assertEqual(1, call_impl_provided())

    def test_injected_default(self):
        self.assertRaises(
            injection.UnboundException, lambda: injection.injected.f(None))


if __name__ == '__main__':
    unittest.main()
