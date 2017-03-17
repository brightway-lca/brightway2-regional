from bw2regional.tests import BW2RegionalTest
from bw2calc import LCA
from bw2data import Database, Method, geomapping
from bw2regional.errors import MissingIntersection, SiteGenericMethod, UnprocessedDatabase
from bw2regional.lca.base_class import RegionalizationBase


class RegionalizationBaseTestCase(BW2RegionalTest):
    def test_unprocessed_database_error(self):
        empty = Database("empty")
        empty.register(depends=[])
        with self.assertRaises(UnprocessedDatabase):
            rlca = RegionalizationBase({("empty", "nothing"): 1})
            rlca.get_inventory_geocollections()

    def test_site_generic_method_error(self):
        empty = Database("empty")
        empty.register(depends=[], geocollections=[])
        method = Method(("a", "name"))
        method.register()
        with self.assertRaises(SiteGenericMethod):
            rlca = RegionalizationBase({("empty", "nothing"): 1}, method=("a", "name"))
            rlca.get_ia_geocollections()

    def test_missing_intersection_error(self):
        empty = Database("empty")
        empty.register(depends=[], geocollections=["foo"])
        method = Method(("a", "name"))
        method.register(geocollections=["bar"])
        with self.assertRaises(MissingIntersection):
            rlca = RegionalizationBase({("empty", "nothing"): 1}, method=("a", "name"))
            rlca.inventory_geocollections = rlca.get_inventory_geocollections()
            rlca.ia_geocollections = rlca.get_ia_geocollections()
            rlca.needed_intersections()

    def test_fix_spatial_dictionaries(self):
        # TODO: Fix
        return

        empty = Database("empty")
        empty.register(depends=[], geocollections=["foo"])
        method = Method(("a", "name"))
        method.register(geocollections=["foo"])
        rlca = RegionalizationBase({("empty", "nothing"): 1}, method=("a", "name"))

        # No-op - `inv_spatial_dict` not yet set...
        rlca.fix_spatial_dictionaries()
        assert not getattr(rlca, "_mapped_spatial_dict", None)
        self.assertFalse(hasattr(rlca, "inv_spatial_dict"))

        geomapping.data = {"a": 1, "b": 2}
        rlca.inv_spatial_dict = {"a": "foo"}
        # Now it does something...
        rlca.fix_spatial_dictionaries()
        self.assertFalse(hasattr(rlca, "ia_spatial_dict"))
        rlca.inv_spatial_dict = {1: "foo"}
        rlca.ia_spatial_dict = {2: "bar"}
        rlca.fix_spatial_dictionaries()
        self.assertEqual(rlca.inv_spatial_dict, {"a": "foo"})
        self.assertEqual(rlca.ia_spatial_dict, {"b": "bar"})

