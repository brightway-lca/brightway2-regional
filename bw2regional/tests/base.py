# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from bw2data.tests import BW2DataTest
from ..meta import geocollections, intersections, loadings


class BW2RegionalTest(BW2DataTest):
    def extra_setup(self):
        geocollections.__init__()
        intersections.__init__()
        loadings.__init__()

