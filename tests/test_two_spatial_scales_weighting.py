import numpy as np
from bw2data import Database, Method, databases, geomapping, get_id, methods

from bw2regional.intersection import Intersection
from bw2regional.lca import TwoSpatialScalesWithGenericLoadingLCA as LCA
from bw2regional.loading import Loading
from bw2regional.meta import intersections, loadings
from bw2regional.tests import BW2RegionalTest


class TwoSpatialScalesWithGenericLoadingLCATestCase(BW2RegionalTest):
    def test_value_error_no_loadings(self):
        with self.assertRaises(ValueError):
            LCA({"foo": 1}, method="foo")

    def import_data(self):
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
        biosphere.register(depends=[], geocollections=[])
        biosphere.write(biosphere_data)

        inventory_data = {
            ("inventory", "U"): {
                "type": "process",
                "location": "L",
                "exchanges": [
                    {"input": ("biosphere", "F"), "type": "biosphere", "amount": 1},
                    {"input": ("biosphere", "G"), "type": "biosphere", "amount": 1},
                ],
            },
            ("inventory", "V"): {"type": "process", "location": "M", "exchanges": []},
            ("inventory", "X"): {"type": "process", "location": "N", "exchanges": []},
            ("inventory", "Y"): {"type": "process", "location": "O", "exchanges": []},
            ("inventory", "Z"): {"type": "process", "location": "O", "exchanges": []},
        }
        inventory = Database("inventory")
        inventory.register(depends=["biosphere"], geocollections=["places"])
        inventory.write(inventory_data)

        intersection_data = [
            ["L", "A", 1],
            ["M", "A", 2],
            ["M", "B", 3],
            ["N", "B", 5],
            ["N", "C", 8],
            ["O", "C", 13],
        ]
        inter = Intersection(("places", "regions"))
        inter.register()
        inter.write(intersection_data)

        loading_data = [
            [2, "A"],
            [4, "B"],
            [8, "C"],
        ]
        loading = Loading("loading")
        loading.register()
        loading.write(loading_data)

        method_data = [
            [("biosphere", "F"), 1, "A"],
            [("biosphere", "G"), 2, "A"],
            [("biosphere", "F"), 3, "B"],
            [("biosphere", "G"), 4, "B"],
            [("biosphere", "F"), 5, "C"],
            [("biosphere", "G"), 6, "C"],
        ]
        method = Method(("a", "method"))
        method.register(geocollections=["regions"])
        method.write(method_data)

    def test_import_data(self):
        self.import_data()
        assert list(databases)
        assert list(intersections)
        assert list(methods)
        assert list(loadings)

    def get_lca(self):
        self.import_data()
        return LCA({("inventory", "U"): 1}, method=("a", "method"), loading="loading")

    def test_inventory(self):
        lca = self.get_lca()
        lca.lci()
        # lca.fix_spatial_dictionaries()

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

        # assert {("inventory", o) for o in "XUVYZ"} == set(lca.dicts.activity.keys())
        # assert set(range(5)) == set(lca.dicts.activity.values())
        # assert {("biosphere", "G"), ("biosphere", "F")} == set(
        #     lca.dicts.biosphere.keys()
        # )
        # assert set(range(2)) == set(lca.dicts.biosphere.values())

        assert lca.supply_array.sum() == 1
        assert lca.supply_array.shape == (5,)
        assert lca.supply_array[lca.dicts.product[get_id(("inventory", "U"))]] == 1

        assert np.allclose(lca.inventory.todense(), lca.biosphere_matrix.todense())

    def test_geo_transform_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        # lca.fix_spatial_dictionaries()

        # assert {x for x in "MLNO"} == set(lca.dicts.inv_spatial.keys())
        # assert set(range(4)) == set(lca.dicts.inv_spatial.values())

        # assert {x for x in "ABC"} == set(lca.dicts.ia_spatial.keys())
        # assert set(range(3)) == set(lca.dicts.ia_spatial.values())

        assert lca.geo_transform_matrix.sum() == 32
        assert lca.geo_transform_matrix.shape == (4, 3)
        assert (
            lca.geo_transform_matrix[
                lca.dicts.inv_spatial[geomapping["L"]],
                lca.dicts.ia_spatial[geomapping["A"]],
            ]
            == 1
        )
        assert (
            lca.geo_transform_matrix[
                lca.dicts.inv_spatial[geomapping["M"]],
                lca.dicts.ia_spatial[geomapping["B"]],
            ]
            == 3
        )

    def test_loading_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        # lca.fix_spatial_dictionaries()

        assert lca.loading_matrix.sum() == 14
        assert lca.loading_matrix.shape == (3, 3)
        assert (
            lca.loading_matrix[
                lca.dicts.ia_spatial[geomapping["A"]],
                lca.dicts.ia_spatial[geomapping["A"]],
            ]
            == 2
        )
        assert (
            lca.loading_matrix[
                lca.dicts.ia_spatial[geomapping["B"]],
                lca.dicts.ia_spatial[geomapping["B"]],
            ]
            == 4
        )
        assert (
            lca.loading_matrix[
                lca.dicts.ia_spatial[geomapping["C"]],
                lca.dicts.ia_spatial[geomapping["C"]],
            ]
            == 8
        )

    def test_characterization_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        # lca.fix_spatial_dictionaries()

        assert lca.reg_cf_matrix.sum() == 21
        assert lca.reg_cf_matrix.shape == (3, 2)
        assert (
            lca.reg_cf_matrix[
                lca.dicts.ia_spatial[geomapping["A"]],
                lca.dicts.biosphere[get_id(("biosphere", "F"))],
            ]
            == 1
        )
        assert (
            lca.reg_cf_matrix[
                lca.dicts.ia_spatial[geomapping["B"]],
                lca.dicts.biosphere[get_id(("biosphere", "G"))],
            ]
            == 4
        )

    def test_inv_mapping_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        # lca.fix_spatial_dictionaries()

        assert lca.inv_mapping_matrix.sum() == 5
        assert lca.inv_mapping_matrix.shape == (5, 4)
        assert (
            lca.inv_mapping_matrix[
                lca.dicts.activity[get_id(("inventory", "V"))],
                lca.dicts.inv_spatial[geomapping["M"]],
            ]
            == 1
        )
        assert (
            lca.inv_mapping_matrix[
                lca.dicts.activity[get_id(("inventory", "X"))],
                lca.dicts.inv_spatial[geomapping["N"]],
            ]
            == 1
        )

    def test_normalization_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        # lca.fix_spatial_dictionaries()

        print(lca.dicts.inv_spatial)
        print(lca.normalization_matrix.todense())

        assert np.allclose(
            lca.normalization_matrix.sum(), 1 / 2 + 1 / 16 + 1 / 84 + 1 / 104
        )
        assert lca.normalization_matrix.shape == (4, 4)
        assert np.allclose(
            lca.normalization_matrix[
                lca.dicts.inv_spatial[geomapping["M"]],
                lca.dicts.inv_spatial[geomapping["M"]],
            ],
            1 / 16,
        )
        assert np.allclose(
            lca.normalization_matrix[
                lca.dicts.inv_spatial[geomapping["N"]],
                lca.dicts.inv_spatial[geomapping["N"]],
            ],
            1 / 84,
        )
        assert np.allclose(
            lca.normalization_matrix[
                lca.dicts.inv_spatial[geomapping["L"]],
                lca.dicts.inv_spatial[geomapping["L"]],
            ],
            1 / 2,
        )
        assert np.allclose(
            lca.normalization_matrix[
                lca.dicts.inv_spatial[geomapping["O"]],
                lca.dicts.inv_spatial[geomapping["O"]],
            ],
            1 / 104,
        )

    def test_lca_score(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        self.assertEqual(lca.score, 3)
