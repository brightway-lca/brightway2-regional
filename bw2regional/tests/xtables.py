# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from ..xtables import ExtensionTable
from .base import BW2RegionalTest
from bw2data import geomapping
from voluptuous import Invalid


class XtablesTestCase(BW2RegionalTest):
    def test_filename(self):
        lg = ExtensionTable(u"some loading with a crazy name")
        self.assertTrue(".xtable" in lg.filename)
        self.assertFalse(".loading" in lg.filename)
