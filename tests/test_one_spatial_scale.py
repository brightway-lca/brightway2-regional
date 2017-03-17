from bw2regional.tests import BW2RegionalTest
from bw2data import Database, Method, databases, methods, geomapping
from bw2regional.errors import GeocollectionsMismatch
from bw2regional.lca import OneSpatialScaleLCA as LCA
from bw2regional.meta import intersections, loadings
import numpy as np


class OneSpatialScaleLCATestCase(BW2RegionalTest):
    def test_value_error_no_method(self):
        empty = Database("empty")
        empty.register(depends=[])

        with self.assertRaises(ValueError):
            LCA({("empty", "nothing"): 1})

    def test_geocollections_mismatch(self):
        inventory = Database("inventory")
        inventory.register(geocollections=["places"])
        method = Method(("a", "method"))
        method.register(geocollections=['regions'])

        with self.assertRaises(GeocollectionsMismatch):
            LCA({("inventory", "foo"): 1}, method=("a", "method"))

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

        method_data = [
            [('biosphere', 'F'), 1, "L"],
            [('biosphere', 'G'), 2, "L"],
        ]
        method = Method(("a", "method"))
        method.register(geocollections=['places'])
        method.write(method_data)

    def test_import_data(self):
        self.import_data()
        assert list(databases)
        assert not list(intersections)
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

    def test_characterization_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        matrix = np.zeros((4, 2))
        matrix[1, 1] = 1
        matrix[1, 0] = 2
        assert lca.reg_cf_matrix.sum() == 3
        assert lca.reg_cf_matrix.shape == (4, 2)
        assert lca.reg_cf_matrix[
            lca.inv_spatial_dict[geomapping['L']],
            lca.biosphere_dict[('biosphere', 'F')]
        ] == 1
        assert lca.reg_cf_matrix[
            lca.inv_spatial_dict[geomapping['L']],
            lca.biosphere_dict[('biosphere', 'G')]
        ] == 2

    def test_lca_score(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        assert lca.score == 3

