# -*- coding: utf-8 -*-
from __future__ import division
from ..errors import MissingIntersection, SiteGenericMethod, UnprocessedDatabase
from ..lca import RegionalizationMixin
from bw2calc import LCA
from .base import BW2RegionalTest
from bw2data import Database, Method, geomapping


class RegionalizedLCA(LCA, RegionalizationMixin):
    pass


class RegionalizedLCAMixinTestCase(BW2RegionalTest):
    def test_unprocessed_database_error(self):
        empty = Database("empty")
        empty.register(depends=[])
        with self.assertRaises(UnprocessedDatabase):
            rlca = RegionalizedLCA({("empty", "nothing"): 1})
            rlca.get_inventory_geocollections()

    def test_site_generic_method_error(self):
        empty = Database("empty")
        empty.register(depends=[], geocollections=[])
        method = Method(("a", "name"))
        method.register()
        with self.assertRaises(SiteGenericMethod):
            rlca = RegionalizedLCA({("empty", "nothing"): 1}, method=("a", "name"))
            rlca.get_ia_geocollections()

    def test_missing_intersection_error(self):
        empty = Database("empty")
        empty.register(depends=[], geocollections=["foo"])
        method = Method(("a", "name"))
        method.register(geocollections=["bar"])
        with self.assertRaises(MissingIntersection):
            rlca = RegionalizedLCA({("empty", "nothing"): 1}, method=("a", "name"))
            rlca.inventory_geocollections = rlca.get_inventory_geocollections()
            rlca.ia_geocollections = rlca.get_ia_geocollections()
            rlca.needed_intersections()

    def test_fix_spatial_dictionaries(self):
        empty = Database("empty")
        empty.register(depends=[], geocollections=["foo"])
        method = Method(("a", "name"))
        method.register(geocollections=["foo"])
        rlca = RegionalizedLCA({("empty", "nothing"): 1}, method=("a", "name"))
        rlca.fix_spatial_dictionaries()
        self.assertFalse(hasattr(rlca, "inv_spatial_dict"))
        geomapping.data = {"a": 1, "b": 2}
        rlca.inv_spatial_dict = {"a": "foo"}
        rlca.fix_spatial_dictionaries()
        self.assertFalse(hasattr(rlca, "ia_spatial_dict"))
        rlca.inv_spatial_dict = {1: "foo"}
        rlca.ia_spatial_dict = {2: "bar"}
        rlca.fix_spatial_dictionaries()
        self.assertEqual(rlca.inv_spatial_dict, {"a": "foo"})
        self.assertEqual(rlca.ia_spatial_dict, {"b": "bar"})

