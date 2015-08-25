# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from ..meta import intersections, loadings, geocollections
from .base import BW2RegionalTest


class GeocollectionsTestCase(BW2RegionalTest):
    def test_filename(self):
        self.assertEqual(geocollections.filename, "geocollections.json")

    def test_unicode(self):
        self.assertTrue(isinstance(str(geocollections), str))
        self.assertEqual(
            str(geocollections),
            u"Brightway2 geocollections metadata: 0 data sets"
        )


class IntersectionsTestCase(BW2RegionalTest):
    def test_filename(self):
        self.assertEqual(intersections.filename, "intersections.json")

    def test_unicode(self):
        self.assertTrue(isinstance(str(intersections), str))
        self.assertEqual(
            str(intersections),
            u"Brightway2 LCI/LCIA areal intersection metadata: 0 data sets"
        )


class LoadingsTestCase(BW2RegionalTest):
    def test_filename(self):
        self.assertEqual(loadings.filename, "loadings.json")

    def test_unicode(self):
        self.assertTrue(isinstance(str(loadings), str))
        self.assertEqual(
            str(loadings),
            u"Brightway2 regionalized LCIA loading metadata: 0 data sets"
        )
