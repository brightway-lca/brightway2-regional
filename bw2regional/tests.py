from bw2regional.meta import geocollections, intersections, loadings
from bw2data import config, projects
from bw2data.tests import BW2DataTest
import wrapt


class BW2RegionalTest(BW2DataTest):
    def extra_setup(self):
        geocollections.__init__()
        intersections.__init__()
        loadings.__init__()


@wrapt.decorator
def bw2test(wrapped, instance, args, kwargs):
    config.dont_warn = True
    config.is_test = True
    config.cache = {}
    projects._use_temp_directory()
    projects.set_current("default")
    geocollections.__init__()
    intersections.__init__()
    loadings.__init__()
    return wrapped(*args, **kwargs)

