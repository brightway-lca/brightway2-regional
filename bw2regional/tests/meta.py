# -*- coding: utf-8 -*
from ..meta import intersections, loadings, geocollections
from .base import BW2RegionalTest


class GeocollectionsTestCase(BW2RegionalTest):
    def test_filename(self):
        self.assertEqual(geocollections.filename, "geocollections.json")

    def test_unicode(self):
        self.assertTrue(isinstance(geocollections.__unicode__(), unicode))
        self.assertEqual(
            unicode(geocollections),
            u"Brightway2 geocollections metadata: 0 data sets"
        )


class IntersectionsTestCase(BW2RegionalTest):
    def test_filename(self):
        self.assertEqual(intersections.filename, "intersections.json")

    def test_unicode(self):
        self.assertTrue(isinstance(intersections.__unicode__(), unicode))
        self.assertEqual(
            unicode(intersections),
            u"Brightway2 LCI/LCIA areal intersection metadata: 0 data sets"
        )


class LoadingsTestCase(BW2RegionalTest):
    def test_filename(self):
        self.assertEqual(loadings.filename, "loadings.json")

    def test_unicode(self):
        self.assertTrue(isinstance(loadings.__unicode__(), unicode))
        self.assertEqual(
            unicode(loadings),
            u"Brightway2 regionalized LCIA loading metadata: 0 data sets"
        )
