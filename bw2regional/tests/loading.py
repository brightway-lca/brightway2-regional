from ..loading import Loading
from ..meta import loadings
from .base import BW2RegionalTest
from bw2data import geomapping
from voluptuous import Invalid


class LoadingsTestCase(BW2RegionalTest):
    def test_filename(self):
        self.assertEqual(loadings.filename, "loadings.json")

    def test_unicode(self):
        self.assertTrue(isinstance(loadings.__unicode__(), unicode))
        self.assertEqual(
            unicode(loadings),
            u"Brightway2 regionalized LCIA loading metadata: 0 data sets"
        )


class LoadingTestCase(BW2RegionalTest):
    def test_add_mappings(self):
        lg = Loading("some loadings")
        self.assertFalse(("foo", "bar") in geomapping)
        # lg.write([])

    def test_validation(self):
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

