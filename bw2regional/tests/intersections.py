from ..loading import Loading
from ..meta import intersections
from .base import BW2RegionalTest
from bw2data import geomapping
from voluptuous import Invalid


class IntersectionsTestCase(BW2RegionalTest):
    def test_filename(self):
        self.assertEqual(intersections.filename, "intersections.json")

    def test_unicode(self):
        self.assertTrue(isinstance(intersections.__unicode__(), unicode))
        self.assertEqual(
            unicode(intersections),
            u"Brightway2 LCI/LCIA areal intersection metadata: 0 data sets"
        )


class IntersectionTestCase(BW2RegionalTest):
    def test_add_mappings(self):
        return
        lg = Loading("some loadings")
        self.assertFalse(("foo", "bar") in geomapping)
        # lg.write([])

    def test_validation(self):
        return
        lg = Loading("some loadings")
        self.assertTrue(lg.validate([]))
        self.assertTrue(lg.validate([[1, "f"]]))
        self.assertTrue(lg.validate([[{'amount': 1}, "f"]]))
        self.assertTrue(lg.validate([[1, ("f", "b")]]))
        self.assertTrue(lg.validate([[{'amount': 1}, ("f", "b")]]))
        with self.assertRaises(Invalid):
            lg.validate(())
        # with self.assertRaises(Invalid):
        #     lg.validate([["f", 1]])

