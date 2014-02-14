# -*- coding: utf-8 -*-
from __future__ import division
from ..intersection import Intersection
from ..lca import TwoSpatialScalesLCA as LCA
from ..meta import intersections, loadings
from .base import BW2RegionalTest
from bw2data import Database, Method, databases, methods
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
        inter.process()

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
        method.process()

    def test_import_data(self):
        self.import_data()
        self.assertTrue(databases.list)
        self.assertTrue(intersections.list)
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

    def test_geo_transform_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        lca.fix_spatial_dictionaries()
        self.assertEqual(
            lca.inv_spatial_dict,
            {'M': 0, 'L': 1, 'O': 2, 'N': 3}
        )
        self.assertEqual(
            lca.ia_spatial_dict,
            {'A': 0, 'B': 2, 'C': 1}
        )
        self.assertTrue(np.allclose(
            lca.geo_transform_matrix.todense(),
            np.array(((2, 0, 3), (1, 0, 0), (0, 13, 0), (0, 8, 5)))
        ))

    def test_characterization_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        self.assertTrue(np.allclose(
            lca.reg_cf_matrix.todense(),
            np.array(((2, 1), (6, 5), (4, 3)))
        ))

    def test_inv_mapping_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        self.assertTrue(np.allclose(
            lca.inv_mapping_matrix.todense(),
            np.array(((0, 0, 0, 1), (0, 1, 0, 0), (1, 0, 0, 0), (0, 0, 1, 0), (0, 0, 1, 0)))
        ))

    def test_normalization_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        normalization = np.eye(4)
        normalization[1,1] = 1
        normalization[0,0] = 1/5
        normalization[3,3] = 1/13
        normalization[2,2] = 1/13
        self.assertTrue(np.allclose(
            lca.normalization_matrix.todense(),
            normalization
        ))

    def test_lca_score(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        self.assertEqual(
            lca.score,
            3
        )

