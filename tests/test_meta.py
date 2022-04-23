import os

from bw2data.tests import bw2test

from bw2regional import geocollections, intersections, loadings

data_dir = os.path.join(os.path.dirname(__file__), "data")


@bw2test
def test_geocollections_filename():
    assert geocollections.filename == "geocollections.json"


@bw2test
def test_geocollections_unicode():
    assert isinstance(str(geocollections), str)
    assert str(geocollections) == "Geocollections dictionary with 0 objects"


@bw2test
def test_geocollectoins_vector_test_data():
    geocollections["countries"] = {
        "filepath": os.path.join(data_dir, "test_countries.gpkg"),
        "field": "name",
    }


@bw2test
def test_geocollectioins_raster_test_data():
    geocollections["cfs"] = {"filepath": os.path.join(data_dir, "test_raster_cfs.tif")}


@bw2test
def test_intersectioins_filename():
    assert intersections.filename == "intersections.json"


@bw2test
def test_intersectioins_unicode():
    assert isinstance(str(intersections), str)
    assert str(intersections) == "Intersections dictionary with 0 objects"


@bw2test
def test_intersectioins_load_test_data_1():
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


@bw2test
def test_intersectioins_load_test_data_2():
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


@bw2test
def test_loadings_filename():
    assert loadings.filename == "loadings.json"


@bw2test
def test_loadings_unicode():
    assert isinstance(str(loadings), str)
    assert str(loadings) == "Loadings dictionary with 0 objects"


# TODO: Test data loading
