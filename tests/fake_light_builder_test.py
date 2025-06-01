#!/usr/bin/env python

import unittest

from bardolph.controller import i_controller
from bardolph.fakes.fake_light_api import _Chroma, _LightBuilder, _Type

from tests import test_module


class FakeLightBuilderTest(unittest.TestCase):
    def setUp(self):
        self._name = 'the_name'
        self._group = 'the_group'
        self._location = 'the_location'
        self._spec = [self._name, self._group, self._location]

    def test_minimal(self):
        light = _LightBuilder.new_from_spec(self._spec)

        self.assertTrue(isinstance(light, i_controller.Light))
        self.assertFalse(isinstance(light, i_controller.MultizoneLight))
        self.assertFalse(isinstance(light, i_controller.MatrixLight))

        self.assertEqual(light.get_name(), self._name)
        self.assertEqual(light.get_group(), self._group)
        self.assertEqual(light.get_location(), self._location)
        self.assertEqual(light.get_height(), 1)
        self.assertEqual(light.get_width(), 1)
        self.assertTrue(light.is_color())

    def test_white(self):
        self._spec.append(_Chroma.WHITE)
        light = _LightBuilder.new_from_spec(self._spec)
        self.assertFalse(light.is_color())

    def test_multizone(self):
        width = 17
        self._spec.extend((_Type.MULTI_ZONE, width))
        light = _LightBuilder.new_from_spec(self._spec)
        self.assertTrue(isinstance(light, i_controller.MultizoneLight))
        self.assertEqual(light.get_height(), 1)
        self.assertEqual(light.get_width(), width)

    def test_matrix(self):
        height = 37
        width = 19
        self._spec.extend((_Type.MATRIX, height, width))
        light = _LightBuilder.new_from_spec(self._spec)
        self.assertTrue(isinstance(light, i_controller.MatrixLight))
        self.assertEqual(light.get_height(), 37)
        self.assertEqual(light.get_width(), 19)


if __name__ == '__main__':
    unittest.main()
