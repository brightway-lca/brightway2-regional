from bw2regional.tests import BW2RegionalTest
from bw2data import geomapping
from bw2regional.xtables import ExtensionTable
from voluptuous import Invalid


class XtablesTestCase(BW2RegionalTest):
    def test_filename(self):
        lg = ExtensionTable(u"some loading with a crazy name")
        self.assertTrue(".xtable" in lg.filename)
        self.assertFalse(".loading" in lg.filename)
