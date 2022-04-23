import numpy as np
import pytest
from bw2data import Database, Method, databases, geomapping, get_id, methods
from bw2data.tests import bw2test

from bw2regional.intersection import Intersection
from bw2regional.lca import TwoSpatialScalesLCA as LCA
from bw2regional.meta import intersections, loadings


@bw2test
def test_value_error_no_method():
    empty = Database("empty")
    empty.register(depends=[])
    empty.write({("empty", "nothing"): {}})

    with pytest.raises(ValueError):
        LCA({("empty", "nothing"): 1})


@bw2test
def import_data():
    biosphere_data = {
        ("biosphere", "F"): {
            "type": "emission",
            "exchanges": [],
        },
        ("biosphere", "G"): {
            "type": "emission",
            "exchanges": [],
        },
    }
    biosphere = Database("biosphere")
    biosphere.write(biosphere_data)

    inventory_data = {
        ("inventory", "U"): {
            "type": "process",
            "location": ("places", "L"),
            "exchanges": [
                {"input": ("biosphere", "F"), "type": "biosphere", "amount": 1},
                {"input": ("biosphere", "G"), "type": "biosphere", "amount": 1},
            ],
        },
        ("inventory", "V"): {
            "type": "process",
            "location": ("places", "M"),
            "exchanges": [],
        },
        ("inventory", "X"): {
            "type": "process",
            "location": ("places", "N"),
            "exchanges": [],
        },
        ("inventory", "Y"): {
            "type": "process",
            "location": ("places", "O"),
            "exchanges": [],
        },
        ("inventory", "Z"): {
            "type": "process",
            "location": ("places", "O"),
            "exchanges": [],
        },
    }
    inventory = Database("inventory")
    inventory.write(inventory_data)

    intersection_data = [
        [("places", "L"), ("regions", "A"), 1],
        [("places", "M"), ("regions", "A"), 2],
        [("places", "M"), ("regions", "B"), 3],
        [("places", "N"), ("regions", "B"), 5],
        [("places", "N"), ("regions", "C"), 8],
        [("places", "O"), ("regions", "C"), 13],
    ]
    inter = Intersection(("places", "regions"))
    inter.write(intersection_data)

    method_data = [
        [("biosphere", "F"), 1, ("regions", "A")],
        [("biosphere", "G"), 2, ("regions", "A")],
        [("biosphere", "F"), 3, ("regions", "B")],
        [("biosphere", "G"), 4, ("regions", "B")],
        [("biosphere", "F"), 5, ("regions", "C")],
        [("biosphere", "G"), 6, ("regions", "C")],
    ]
    method = Method(("a", "method"))
    method.write(method_data)


def test_import_data():
    import_data()
    assert list(databases)
    assert list(intersections)
    assert list(methods)
    assert not list(loadings)


def get_lca():
    import_data()
    return LCA({("inventory", "U"): 1}, method=("a", "method"))


def test_inventory():
    lca = get_lca()
    lca.lci()

    assert np.allclose(lca.technosphere_matrix.todense(), np.eye(5))

    assert lca.biosphere_matrix.sum() == 2
    assert lca.biosphere_matrix.shape == (2, 5)
    assert (
        lca.biosphere_matrix[
            lca.dicts.biosphere[get_id(("biosphere", "F"))],
            lca.dicts.activity[get_id(("inventory", "U"))],
        ]
        == 1
    )
    assert (
        lca.biosphere_matrix[
            lca.dicts.biosphere[get_id(("biosphere", "G"))],
            lca.dicts.activity[get_id(("inventory", "U"))],
        ]
        == 1
    )

    assert lca.supply_array.sum() == 1
    assert lca.supply_array.shape == (5,)
    assert lca.supply_array[lca.dicts.product[get_id(("inventory", "U"))]] == 1

    assert np.allclose(lca.inventory.todense(), lca.biosphere_matrix.todense())


def test_geo_transform_matrix():
    lca = get_lca()
    lca.lci()
    lca.lcia()

    assert lca.geo_transform_matrix.sum() == 32
    assert lca.geo_transform_matrix.shape == (4, 3)
    assert (
        lca.geo_transform_matrix[
            lca.dicts.inv_spatial[geomapping[("places", "L")]],
            lca.dicts.ia_spatial[geomapping[("regions", "A")]],
        ]
        == 1
    )
    assert (
        lca.geo_transform_matrix[
            lca.dicts.inv_spatial[geomapping[("places", "M")]],
            lca.dicts.ia_spatial[geomapping[("regions", "B")]],
        ]
        == 3
    )


def test_characterization_matrix():
    lca = get_lca()
    lca.lci()
    lca.lcia()

    assert lca.reg_cf_matrix.sum() == 21
    assert lca.reg_cf_matrix.shape == (3, 2)
    assert (
        lca.reg_cf_matrix[
            lca.dicts.ia_spatial[geomapping[("regions", "A")]],
            lca.dicts.biosphere[get_id(("biosphere", "F"))],
        ]
        == 1
    )
    assert (
        lca.reg_cf_matrix[
            lca.dicts.ia_spatial[geomapping[("regions", "B")]],
            lca.dicts.biosphere[get_id(("biosphere", "G"))],
        ]
        == 4
    )


def test_inv_mapping_matrix():
    lca = get_lca()
    lca.lci()
    lca.lcia()

    assert lca.inv_mapping_matrix.sum() == 5
    assert lca.inv_mapping_matrix.shape == (5, 4)
    assert (
        lca.inv_mapping_matrix[
            lca.dicts.activity[get_id(("inventory", "V"))],
            lca.dicts.inv_spatial[geomapping[("places", "M")]],
        ]
        == 1
    )
    assert (
        lca.inv_mapping_matrix[
            lca.dicts.activity[get_id(("inventory", "X"))],
            lca.dicts.inv_spatial[geomapping[("places", "N")]],
        ]
        == 1
    )


def test_normalization_matrix():
    lca = get_lca()
    lca.lci()
    lca.lcia()

    assert np.allclose(lca.normalization_matrix.sum(), 1 + 1 / 5 + 2 / 13)
    assert lca.normalization_matrix.shape == (4, 4)
    assert np.allclose(
        lca.normalization_matrix[
            lca.dicts.inv_spatial[geomapping[("places", "M")]],
            lca.dicts.inv_spatial[geomapping[("places", "M")]],
        ],
        1 / 5,
    )
    assert np.allclose(
        lca.normalization_matrix[
            lca.dicts.inv_spatial[geomapping[("places", "N")]],
            lca.dicts.inv_spatial[geomapping[("places", "N")]],
        ],
        1 / 13,
    )


def test_lca_score():
    lca = get_lca()
    lca.lci()
    lca.lcia()
    assert lca.score == 3
