import pytest
from bw2data import Database, Method, databases, methods
from bw2data.tests import bw2test

from bw2regional.errors import MissingIntersection, SiteGenericMethod
from bw2regional.lca.base_class import RegionalizationBase


@bw2test
def test_site_generic_method_error():
    empty = Database("empty")
    empty.register(depends=[], geocollections=[])
    empty.write({("empty", "nothing"): {}})
    method = Method(("a", "name"))
    method.register()
    method.write([])
    with pytest.raises(SiteGenericMethod):
        rlca = RegionalizationBase({("empty", "nothing"): 1}, method=("a", "name"))
        rlca.get_ia_geocollections()


@bw2test
def test_missing_intersection_error():
    empty = Database("empty")
    empty.write({("empty", "nothing"): {}})
    databases["empty"]["geocollections"] = ["foo"]
    method = Method(("a", "name"))
    method.write([])
    methods[("a", "name")]["geocollections"] = ["bar"]
    with pytest.raises(MissingIntersection):
        rlca = RegionalizationBase({("empty", "nothing"): 1}, method=("a", "name"))
        rlca.inventory_geocollections = rlca.get_inventory_geocollections()
        rlca.ia_geocollections = rlca.get_ia_geocollections()
        rlca.needed_intersections()
