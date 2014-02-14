# -*- coding: utf-8 -*-
from ..lca import OneSpatialScaleLCA as LCA
from ..meta import intersections, loadings
from .base import BW2RegionalTest
from bw2data import Database, Method, databases, methods
import numpy as np
from ..errors import GeocollectionsMismatch


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
        biosphere.process()

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
        inventory.process()

        method_data = [
            [('biosphere', 'F'), 1, "L"],
            [('biosphere', 'G'), 2, "L"],
        ]
        method = Method(("a", "method"))
        method.register(geocollections=['places'])
        method.write(method_data)
        method.process()

    def test_import_data(self):
        self.import_data()
        self.assertTrue(databases.list)
        self.assertFalse(intersections.list)
        self.assertTrue(methods.list)
        self.assertFalse(loadings.list)

    def get_lca(self):
        self.import_data()
        return LCA(
            {('inventory', 'U'): 1},
            method=("a", "method")
        )

    def test_inventory(self):
        lca = self.get_lca()
        lca.lci()
        self.assertTrue(np.allclose(
            lca.technosphere_matrix.todense(),
            np.eye(5)
        ))
        lca.fix_dictionaries()
        self.assertTrue(np.allclose(
            lca.biosphere_matrix.todense(),
            np.array(((0, 1, 0, 0, 0), (0, 1, 0, 0, 0)))
        ))
        lca.fix_dictionaries()
        self.assertEqual(
            lca.technosphere_dict,
            {
                ('inventory', 'X'): 0,
                ('inventory', 'U'): 1,
                ('inventory', 'V'): 2,
                ('inventory', 'Y'): 3,
                ('inventory', 'Z'): 4
            }
        )
        self.assertEqual(
            lca.biosphere_dict,
            {('biosphere', 'G'): 0, ('biosphere', 'F'): 1}
        )
        self.assertTrue(np.allclose(
            lca.supply_array,
            np.array((0, 1, 0, 0, 0))
        ))
        self.assertTrue(np.allclose(
            lca.inventory.todense(),
            lca.biosphere_matrix.todense()
        ))

    def test_characterization_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        matrix = np.zeros((4, 2))
        matrix[1, 1] = 1
        matrix[1, 0] = 2
        self.assertTrue(np.allclose(
            lca.reg_cf_matrix.todense(),
            matrix
        ))

    def test_lca_score(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        self.assertEqual(
            lca.score,
            3
        )

