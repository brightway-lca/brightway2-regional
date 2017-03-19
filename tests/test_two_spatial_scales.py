from bw2regional.tests import BW2RegionalTest
from bw2data import Database, Method, databases, methods, geomapping
from bw2regional.intersection import Intersection
from bw2regional.lca import TwoSpatialScalesLCA as LCA
from bw2regional.meta import intersections, loadings
import numpy as np


class TwoSpatialScalesLCATestCase(BW2RegionalTest):
    def test_value_error_no_method(self):
        empty = Database("empty")
        empty.register(depends=[])

        with self.assertRaises(ValueError):
            LCA({("empty", "nothing"): 1})

    def import_data(self):
        biosphere_data = {
            ('biosphere', 'F'): {
                'type': 'emission',
                'exchanges': [],
            },
            ('biosphere', 'G'): {
                'type': 'emission',
                'exchanges': [],
            }
        }
        biosphere = Database("biosphere")
        biosphere.register(depends=[], geocollections=[])
        biosphere.write(biosphere_data)

        inventory_data = {
            ('inventory', 'U'): {
                'type': 'process',
                'location': "L",
                'exchanges': [
                    {
                    'input': ('biosphere', 'F'),
                    'type': 'biosphere',
                    'amount': 1
                    },
                    {
                    'input': ('biosphere', 'G'),
                    'type': 'biosphere',
                    'amount': 1
                    },
                ]
            },
            ('inventory', 'V'): {
                'type': 'process',
                'location': "M",
                'exchanges': []
            },
            ('inventory', 'X'): {
                'type': 'process',
                'location': "N",
                'exchanges': []
            },
            ('inventory', 'Y'): {
                'type': 'process',
                'location': "O",
                'exchanges': []
            },
            ('inventory', 'Z'): {
                'type': 'process',
                'location': "O",
                'exchanges': []
            }
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

        method_data = [
            [('biosphere', 'F'), 1, "A"],
            [('biosphere', 'G'), 2, "A"],
            [('biosphere', 'F'), 3, "B"],
            [('biosphere', 'G'), 4, "B"],
            [('biosphere', 'F'), 5, "C"],
            [('biosphere', 'G'), 6, "C"],
        ]
        method = Method(("a", "method"))
        method.register(geocollections=['regions'])
        method.write(method_data)

    def test_import_data(self):
        self.import_data()
        assert list(databases)
        assert list(intersections)
        assert list(methods)
        assert not list(loadings)

    def get_lca(self):
        self.import_data()
        return LCA(
            {('inventory', 'U'): 1},
            method=("a", "method")
        )

    def test_inventory(self):
        lca = self.get_lca()
        lca.lci()
        lca.fix_spatial_dictionaries()

        assert np.allclose(lca.technosphere_matrix.todense(), np.eye(5))

        assert lca.biosphere_matrix.sum() == 2
        assert lca.biosphere_matrix.shape == (2, 5)
        assert lca.biosphere_matrix[
            lca.biosphere_dict[('biosphere', 'F')],
            lca.activity_dict[('inventory', 'U')]
        ] == 1
        assert lca.biosphere_matrix[
            lca.biosphere_dict[('biosphere', 'G')],
            lca.activity_dict[('inventory', 'U')]
        ] == 1

        assert {('inventory', o) for o in 'XUVYZ'} == set(lca.activity_dict.keys())
        assert set(range(5)) == set(lca.activity_dict.values())
        assert {('biosphere', 'G'), ('biosphere', 'F')} == set(lca.biosphere_dict.keys())
        assert set(range(2)) == set(lca.biosphere_dict.values())

        assert lca.supply_array.sum() == 1
        assert lca.supply_array.shape == (5,)
        assert lca.supply_array[lca.product_dict[('inventory', 'U')]] == 1

        assert np.allclose(lca.inventory.todense(), lca.biosphere_matrix.todense())

    def test_geo_transform_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        lca.fix_spatial_dictionaries()

        assert {x for x in 'MLNO'} == set(lca.inv_spatial_dict.keys())
        assert set(range(4)) == set(lca.inv_spatial_dict.values())

        assert {x for x in 'ABC'} == set(lca.ia_spatial_dict.keys())
        assert set(range(3)) == set(lca.ia_spatial_dict.values())

        assert lca.geo_transform_matrix.sum() == 32
        assert lca.geo_transform_matrix.shape == (4, 3)
        assert lca.geo_transform_matrix[
            lca.inv_spatial_dict['L'],
            lca.ia_spatial_dict['A']
        ] == 1
        assert lca.geo_transform_matrix[
            lca.inv_spatial_dict['M'],
            lca.ia_spatial_dict['B']
        ] == 3

    def test_characterization_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        lca.fix_spatial_dictionaries()

        assert lca.reg_cf_matrix.sum() == 21
        assert lca.reg_cf_matrix.shape == (3, 2)
        assert lca.reg_cf_matrix[
            lca.ia_spatial_dict['A'],
            lca.biosphere_dict[('biosphere', 'F')]
        ] == 1
        assert lca.reg_cf_matrix[
            lca.ia_spatial_dict['B'],
            lca.biosphere_dict[('biosphere', 'G')]
        ] == 4

    def test_inv_mapping_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        lca.fix_spatial_dictionaries()

        assert lca.inv_mapping_matrix.sum() == 5
        assert lca.inv_mapping_matrix.shape == (5, 4)
        assert lca.inv_mapping_matrix[
            lca.activity_dict[('inventory', 'V')],
            lca.inv_spatial_dict['M']
        ] == 1
        assert lca.inv_mapping_matrix[
            lca.activity_dict[('inventory', 'X')],
            lca.inv_spatial_dict['N']
        ] == 1

    def test_normalization_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        lca.fix_spatial_dictionaries()

        assert np.allclose(lca.normalization_matrix.sum(), 1 + 1/5 + 2/13)
        assert lca.normalization_matrix.shape == (4, 4)
        assert np.allclose(lca.normalization_matrix[
            lca.inv_spatial_dict['M'],
            lca.inv_spatial_dict['M']
        ], 1/5)
        assert np.allclose(lca.normalization_matrix[
            lca.inv_spatial_dict['N'],
            lca.inv_spatial_dict['N']
        ], 1/13)

    def test_lca_score(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        self.assertEqual(
            lca.score,
            3
        )

