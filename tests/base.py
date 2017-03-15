import os
from bw2regional.meta import geocollections, intersections, loadings
from bw2data.tests import BW2DataTest

data_dir = os.path.join(os.path.dirname(__file__), "data")


class BW2RegionalTest(BW2DataTest):
    def extra_setup(self):
        geocollections.__init__()
        intersections.__init__()
        loadings.__init__()

