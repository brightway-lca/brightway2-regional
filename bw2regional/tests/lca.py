# -*- coding: utf-8 -*-
from __future__ import division
from ..errors import MissingIntersection, SiteGenericMethod, UnprocessedDatabase
from ..intersection import Intersection
from ..lca import TwoSpatialScalesWithGenericLoadingLCA as LCA
from ..loading import Loading
from ..meta import intersections, loadings
from .base import BW2RegionalTest
from brightway2 import Database, Method, databases, methods
import numpy as np

class TwoSpatialScalesWithGenericLoadingLCATestCase(BW2RegionalTest):
    def test_unprocessed_database_error(self):
        empty = Database("empty")
        empty.register(depends=[])

        loading = Loading("something")
        loading.register()

        method = Method(("a", "name"))
        method.register()

        with self.assertRaises(UnprocessedDatabase):
            LCA({("empty", "nothing"): 1}, method=("a", "name"), loading="something")

    def test_value_error_no_loadings(self):
        with self.assertRaises(ValueError):
            LCA({"foo": 1}, method='foo')

    def test_value_error_no_method(self):
        empty = Database("empty")
        empty.register(depends=[])

        loading = Loading("something")
        loading.register()

        with self.assertRaises(ValueError):
            LCA({("empty", "nothing"): 1}, loading='something')

    def test_site_generic_method_error(self):
        empty = Database("empty")
        empty.register(depends=[], geocollections=[])

        loading = Loading("something")
        loading.register()

        method = Method(("a", "name"))
        method.register()

        with self.assertRaises(SiteGenericMethod):
            LCA({("empty", "nothing"): 1}, method=("a", "name"), loading="something")

    def test_missing_intersection_error(self):
        empty = Database("empty")
        empty.register(depends=[], geocollections=["foo"])

        loading = Loading("something")
        loading.register()

        method = Method(("a", "name"))
        method.register(geocollections=["bar"])

        with self.assertRaises(MissingIntersection):
            lca = LCA({("empty", "nothing"): 1}, method=("a", "name"), loading="something")
            lca.needed_intersections()

    def import_data(self):
        biosphere_data = {
            ('biosphere', 'carbon'): {
                'type': 'emission',
                'exchanges': [],
            },
            ('biosphere', 'water'): {
                'type': 'emission',
                'exchanges': [],
            }
        }
        biosphere = Database("biosphere")
        biosphere.register(depends=[], geocollections=[])
        biosphere.write(biosphere_data)
        biosphere.process()

        inventory_data = {
            ('yum', 'bread'): {
                'type': 'process',
                'location': u"хлеб",
                'exchanges': [
                    {
                    'input': ('biosphere', 'carbon'),
                    'type': 'biosphere',
                    'amount': 1
                    },
                    {
                    'input': ('yum', 'milk'),
                    'type': 'technosphere',
                    'amount': 0.5
                    },
                ]
            },
            ('yum', 'milk'): {
                'type': 'process',
                'location': u"молоко",
                'exchanges': [
                    {
                    'input': ('biosphere', 'carbon'),
                    'type': 'biosphere',
                    'amount': 2
                    },
                    {
                    'input': ('biosphere', 'water'),
                    'type': 'biosphere',
                    'amount': 5
                    },
                ]
            },
        }
        inventory = Database("yum")
        inventory.register(depends=["biosphere"], geocollections=["food"])
        inventory.write(inventory_data)
        inventory.process()

        intersection_data = [
            [u"хлеб", u"Ω", 2],
            [u"хлеб", u"ß", 4],
            [u"молоко", u"Ω", 8],
            [u"молоко", u"ß", 16],
        ]
        inter = Intersection(("food", "greek"))
        inter.register()
        inter.write(intersection_data)
        inter.process()

        loading_data = [
            [1, u"Ω"],
            [2, u"ß"]
        ]
        loading = Loading("loading")
        loading.register()
        loading.write(loading_data)
        loading.process()

        method_data = [
            [('biosphere', 'carbon'), 1, u"Ω"],
            [('biosphere', 'carbon'), 3, u"ß"],
            [('biosphere', 'water'), 5, u"Ω"],
            [('biosphere', 'water'), 7, u"ß"]
        ]
        method = Method(("a", "method"))
        method.register(geocollections=['greek'])
        method.write(method_data)
        method.process()

    def test_import_data(self):
        self.import_data()
        self.assertTrue(databases.list)
        self.assertTrue(intersections.list)
        self.assertTrue(methods.list)
        self.assertTrue(loadings.list)

    def get_lca(self):
        self.import_data()
        return LCA(
            {('yum', 'bread'): 1},
            method=("a", "method"),
            loading="loading"
        )

    def test_inventory(self):
        lca = self.get_lca()
        lca.lci()
        self.assertTrue(np.allclose(
            lca.technosphere_matrix.todense(),
            np.array(((1, -0.5), (0, 1)))
        ))
        self.assertTrue(np.allclose(
            lca.biosphere_matrix.todense(),
            np.array(((2, 1), (5, 0)))
        ))
        lca.fix_dictionaries()
        self.assertEqual(
            lca.technosphere_dict,
            {('yum', 'milk'): 0, ('yum', 'bread'): 1}
        )
        self.assertEqual(
            lca.biosphere_dict,
            {('biosphere', 'carbon'): 0, ('biosphere', 'water'): 1}
        )
        self.assertTrue(np.allclose(
            lca.supply_array,
            np.array((0.5, 1))
        ))
        print lca.inventory.todense()
        self.assertTrue(np.allclose(
            lca.inventory.todense(),
            np.array(((1, 1), (2.5, 0)))
        ))

    def test_geo_transform_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        lca.fix_spatial_dictionaries()
        self.assertEqual(
            lca.inv_spatial_dict,
            {u"молоко": 0, u"хлеб": 1}
        )
        self.assertEqual(
            lca.ia_spatial_dict,
            {u"Ω": 0, u"ß": 1}
        )
        self.assertTrue(np.allclose(
            lca.geo_transform_matrix.todense(),
            np.array(((8, 16), (2, 4)))
        ))

    def test_loading_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        self.assertTrue(np.allclose(
            lca.loading_matrix.todense(),
            np.array(((1, 0), (0, 2)))
        ))

    def test_characterization_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        print lca.reg_cf_matrix.todense()
        self.assertTrue(np.allclose(
            lca.reg_cf_matrix.todense(),
            np.array(((1, 3), (5, 7)))
        ))

    def test_inv_mapping_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        self.assertTrue(np.allclose(
            lca.inv_mapping_matrix.todense(),
            np.array(((1, 0), (0, 1)))
        ))

    def test_normalization_matrix(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        self.assertTrue(np.allclose(
            lca.normalization_matrix.todense(),
            np.array(((1/8, 1/32), (1/2, 1/8)))
        ))

    def test_lca_score(self):
        lca = self.get_lca()
        lca.lci()
        lca.lcia()
        self.assertEqual(
            lca.score,
            (21 + 31/4 * 2.5 + 21 + 31/4 + 21 * 2.5 + 31/4)
        )

