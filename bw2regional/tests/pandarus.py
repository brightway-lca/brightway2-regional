# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from . import data_dir
from .. import geocollections, topocollections
from ..pandarus import (
    import_from_pandarus,
    merge,
    relabel,
    switch_order,
)
from ..topography import Topography
from .base import BW2RegionalTest
import json
import os


class PandarusTestCase(BW2RegionalTest):
    def test_relabel(self):
        data = [(1, 2, 3)]
        relabeled = relabel(data, "foo", "bar")
        assert relabeled == [(("foo", 1), ("bar", 2), 3)]

    def test_merge(self):
        mapping = {
            "foo": [1, 2, 3],
            "bar": [3, 4, 5]
        }
        intersection = [
            [1, "up", 1],
            [3, "up", 2],
            [3, "down", 4],
            [4, "down", 8],
        ]
        expected = [
            ('bar', 'down', 12),
            ('bar', 'up', 2),
            ('foo', 'down', 4),
            ('foo', 'up', 3)
        ]
        assert expected == sorted(merge(intersection, mapping))

    def test_switch_order(self):
        assert switch_order([(1, 2, 3)]) == [(2, 1, 3)]

    def test_import_topo_intersection_without_error(self):
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

    def test_import_intersection_without_error(self):
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

    # def test_import_errors_1(self):
    #     topo = Topography('foo')
    #     # Fails because no geocollection for topo
    #     with self.assertRaises(UnknownObject):
    #         topo.import_from_pandarus(None, None)
    #     geocollections['green'] = {}
    #     topo.register(geocollection = 'green')
    #     # Fails because to target_geocollection
    #     with self.assertRaises(AssertionError):
    #         topo.import_from_pandarus(None, 'missing')

    # def test_import_errors_2(self):
    #     geocollections['green'] = {}
    #     geocollections['blue'] = {}
    #     topo = Topography('foo')
    #     topo.metadata['geocollection'] = 'green'
    #     geocollections['blue'] = {}
    #     topo.write(dict(json.load(open(
    #         os.path.join(data_dir, "test_topo_mapping.json")
    #     ))))


    #         LCA({("empty", "nothing"): 1})
