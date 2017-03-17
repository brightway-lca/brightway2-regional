from bw2regional.tests import BW2RegionalTest, bw2test
from bw2regional import geocollections, topocollections
from bw2regional.pandarus import (
    import_from_pandarus,
    relabel,
)
from bw2regional.topography import Topography
import json
import os

data_dir = os.path.join(os.path.dirname(__file__), "data")


def test_relabel():
    data = [(1, 2, 3)]
    relabeled = relabel(data, "foo", "bar")
    assert relabeled == [(("foo", 1), ("bar", 2), 3)]

@bw2test
def test_import_topo_intersection_without_error():
    def _(fn):
        return os.path.join(data_dir, fn)

    geocollections['countries'] = {
        'filepath': _("test_countries.gpkg"),
        'field': 'name'
    }
    geocollections['cfs'] = {
        'filepath': _("test_raster_cfs.tif"),
        'field': 'name'
    }
    topocollections['countries'] = {
        'geocollection': 'countries',
        'filepath': _("test_provinces.gpkg"),
        'field': 'OBJECTID_1'
    }
    topo = Topography('countries')
    topo.write(dict(json.load(open(_("test_topo_mapping.json")))))
    import_from_pandarus(_("intersect-topo-cfs.json.bz2"))

@bw2test
def test_import_intersection_without_error():
    def _(fn):
        return os.path.join(data_dir, fn)

    geocollections['countries'] = {
        'filepath': _("test_countries.gpkg"),
        'field': 'name'
    }
    geocollections['cfs'] = {
        'filepath': _("test_raster_cfs.tif"),
        'field': 'name'
    }
    import_from_pandarus(_("intersect-countries-cfs.json.bz2"))
