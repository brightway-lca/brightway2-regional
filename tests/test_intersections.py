from bw2regional.tests import BW2RegionalTest
from bw2data import geomapping
from bw2regional.intersection import Intersection
from voluptuous import Invalid


class IntersectionTestCase(BW2RegionalTest):
    def test_add_mappings(self):
        inter = Intersection(("foo", "bar"))
        inter.register()
        self.assertFalse(("foo", "bar") in geomapping)
        self.assertFalse("baz" in geomapping)
        inter.write([
            [("foo", "bar"), "baz", 42]
        ])
        self.assertTrue(("foo", "bar") in geomapping)
        self.assertTrue("baz" in geomapping)

    def test_validation(self):
        inter = Intersection(("foo", "bar"))
        self.assertTrue(inter.validate([]))
        self.assertTrue(inter.validate([[1, 2, 3]]))
        self.assertTrue(inter.validate([["foo", "bar", 3.]]))
        with self.assertRaises(Invalid):
            inter.validate(())
        with self.assertRaises(Invalid):
            inter.validate([[1, 2]])
        with self.assertRaises(Invalid):
            inter.validate([[1, 2, {'amount': 3.}]])
