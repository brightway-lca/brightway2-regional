from .base import data_dir, BW2RegionalTest
from bw2regional import (
    geocollections,
    Intersection,
    intersections,
    loadings,
)
import os


class GeocollectionsTestCase(BW2RegionalTest):
    def test_filename(self):
        self.assertEqual(geocollections.filename, "geocollections.json")

    def test_unicode(self):
        self.assertTrue(isinstance(str(geocollections), str))
        self.assertEqual(
            str(geocollections),
            "Brightway2 serialized dictionary with 0 entries"
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
            "Brightway2 serialized dictionary with 0 entries"
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
            "Brightway2 serialized dictionary with 0 entries"
        )

    # TODO: Test data loading
