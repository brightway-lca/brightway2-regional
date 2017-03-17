from bw2regional.tests import BW2RegionalTest
from bw2data import geomapping
from bw2regional.loading import Loading
from voluptuous import Invalid
import hashlib


class LoadingTestCase(BW2RegionalTest):
    def test_add_mappings(self):
        lg = Loading("some loadings")
        lg.register()
        self.assertFalse(("foo", "bar") in geomapping)
        lg.write([[1, ("foo", "bar")]])
        self.assertTrue(("foo", "bar") in geomapping)

    def test_validation(self):
        lg = Loading("some loadings")
        self.assertTrue(lg.validate([]))
        self.assertTrue(lg.validate([[1, "f"]]))
        self.assertTrue(lg.validate([[{'amount': 1}, "f"]]))
        self.assertTrue(lg.validate([[1, ("f", "b")]]))
        self.assertTrue(lg.validate([[{'amount': 1}, ("f", "b")]]))
        with self.assertRaises(Invalid):
            lg.validate(())
        with self.assertRaises(Invalid):
            lg.validate([["f", 1]])

    def test_filename(self):
        s = "some loading with a crazy name"
        r = s.replace(" ", "-") + "." + hashlib.md5(s.encode('utf-8')).hexdigest() + ".loading"
        lg = Loading("some loading with a crazy name")
        self.assertEqual(lg.filename, r)

    def test_allow_zero_loadings(self):
        lg = Loading("some loadings")
        self.assertTrue(lg.validate([[0.0, "f"]]))
