from bw2regional.tests import BW2RegionalTest
from bw2regional import (
    geocollections,
    Intersection,
    intersections,
    loadings,
)
import os

data_dir = os.path.join(os.path.dirname(__file__), "data")


class GeocollectionsTestCase(BW2RegionalTest):
    def test_filename(self):
        self.assertEqual(geocollections.filename, "geocollections.json")

    def test_unicode(self):
        self.assertTrue(isinstance(str(geocollections), str))
        self.assertEqual(
            str(geocollections),
            "Geocollections dictionary with 0 objects"
        )

    def test_vector_test_data(self):
        geocollections['countries'] = {
            'filepath': os.path.join(data_dir, "test_countries.gpkg"),
            'field': 'name'
        }

    def test_raster_test_data(self):
        geocollections['cfs'] = {
            'filepath': os.path.join(data_dir, "test_raster_cfs.tif")
        }


class IntersectionsTestCase(BW2RegionalTest):
    def test_filename(self):
        self.assertEqual(intersections.filename, "intersections.json")

    def test_unicode(self):
        self.assertTrue(isinstance(str(intersections), str))
        self.assertEqual(
            str(intersections),
            "Intersections dictionary with 0 objects"
        )

    def test_load_test_data_1(self):
        pass
        # geocollections['countries'] = {
        #     'filepath': os.path.join(data_dir, "test_countries.gpkg"),
        #     'field': 'name'
        # }
        # geocollections['cfs'] = {
        #     'filepath': os.path.join(data_dir, "test_raster_cfs.tif")
        # }
        # Intersection(("countries", "cfs")).import_from_pandarus(
        #     os.path.join(data_dir, "intersect-countries-cfs.json.bz2")
        # )
        # TODO: Check some values

    def test_load_test_data_2(self):
        pass
        # geocollections['countries'] = {
        #     'filepath': os.path.join(data_dir, "test_countries.gpkg"),
        #     'field': 'name'
        # }
        # geocollections['provinces'] = {
        #     'filepath': os.path.join(data_dir, "test_provinces.gpkg"),
        #     'field': 'adm1_code'
        # }
        # Intersection(("provinces", "countries")).import_from_pandarus(
        #     os.path.join(data_dir, "intersect-provinces-countries.json.bz2")
        # )


class LoadingsTestCase(BW2RegionalTest):
    def test_filename(self):
        self.assertEqual(loadings.filename, "loadings.json")

    def test_unicode(self):
        self.assertTrue(isinstance(str(loadings), str))
        self.assertEqual(
            str(loadings),
            "Loadings dictionary with 0 objects"
        )

    # TODO: Test data loading
