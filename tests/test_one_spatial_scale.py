import numpy as np
import pytest
from bw2data import Database, Method, databases, geomapping, get_activity, methods
from bw2data.tests import bw2test

from bw2regional.errors import GeocollectionsMismatch
from bw2regional.lca import OneSpatialScaleLCA as LCA
from bw2regional.meta import intersections, loadings


@bw2test
def test_value_error_no_method():
    empty = Database("empty")
    empty.write({("empty", "nothing"): {}})

    with pytest.raises(ValueError):
        LCA({("empty", "nothing"): 1})


@bw2test
def test_geocollections_mismatch():
    inventory = Database("inventory")
    inventory.write({("inventory", "foo"): {"location": ("places", "somewhere")}})

    method = Method(("a", "method"))
    method.write([])
    method.metadata["geocollections"] = ["regions"]

    with pytest.raises(GeocollectionsMismatch):
        LCA({("inventory", "foo"): 1}, method=("a", "method"))


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

    method_data = [
        [("biosphere", "F"), 1, ("places", "L")],
        [("biosphere", "G"), 2, ("places", "L")],
    ]
    method = Method(("a", "method"))
    method.register(geocollections=["places"])
    method.write(method_data)


def test_import_data():
    import_data()
    assert list(databases)
    assert not list(intersections)
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
            lca.dicts.biosphere[get_activity(("biosphere", "F")).id],
            lca.dicts.activity[get_activity(("inventory", "U")).id],
        ]
        == 1
    )
    assert (
        lca.biosphere_matrix[
            lca.dicts.biosphere[get_activity(("biosphere", "G")).id],
            lca.dicts.activity[get_activity(("inventory", "U")).id],
        ]
        == 1
    )

    # assert {("inventory", o) for o in "XUVYZ"} == set(lca.activity_dict.keys())
    # assert set(range(5)) == set(lca.activity_dict.values())
    # assert {("biosphere", "G"), ("biosphere", "F")} == set(
    #     lca.biosphere_dict.keys()
    # )
    # assert set(range(2)) == set(lca.biosphere_dict.values())

    assert lca.supply_array.sum() == 1
    assert lca.supply_array.shape == (5,)
    assert lca.supply_array[lca.dicts.product[get_activity(("inventory", "U")).id]] == 1


def test_characterization_matrix():
    lca = get_lca()
    lca.lci()
    lca.lcia()

    print(list(lca.dicts.inv_spatial.items()))
    print(list(lca.dicts.biosphere.items()))
    print(list(geomapping.items()))
    for x in Database("biosphere"):
        print(x.id, x["code"])

    matrix = np.zeros((4, 2))
    matrix[1, 1] = 1
    matrix[1, 0] = 2
    print(lca.reg_cf_matrix.toarray())
    assert lca.reg_cf_matrix.sum() == 3
    assert lca.reg_cf_matrix.shape == (4, 2)
    assert (
        lca.reg_cf_matrix[
            lca.dicts.inv_spatial[geomapping[("places", "L")]],
            lca.dicts.biosphere[get_activity(("biosphere", "F")).id],
        ]
        == 1
    )
    assert (
        lca.reg_cf_matrix[
            lca.dicts.inv_spatial[geomapping[("places", "L")]],
            lca.dicts.biosphere[get_activity(("biosphere", "G")).id],
        ]
        == 2
    )


def test_lca_score():
    lca = get_lca()
    lca.lci()
    lca.lcia()
    assert lca.score == 3
