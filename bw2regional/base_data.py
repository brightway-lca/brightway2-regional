# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from . import (
    ExtensionTable,
    geocollections,
    import_regionalized_cfs,
)
from bw2data.utils import download_file
import warnings
import os
from brightway2 import config
import json

LC_IMPACT_WARNING = """"This is a preliminary implementation of LC IMPACT!

It is incomplete, and some values will change.
As such, it should not be used for scientific results."""


def import_base_reg_data():
    """Import base data needed for regionalization.

    Currently, this is the topology used for ecoinvent 3.1."""
    try:
        from constructive_geometries import ConstructiveGeometries
    except ImportError:
        raise ImportError("Please install the ``constructive_geometries`` library.")
    cg = ConstructiveGeometries()
    cg.check_data()
    geocollections['ecoinvent-topology'] = {
        'filepath': cg.faces_fp,
        'field': 'id',
    }

    # Create special geomapping from ecoinvent location names
    # to topological face ids

    fp = os.path.join(
        projects.dir,
        "processed",
        "eitopo.geomapping"
    )
    gl = config.global_location
    face_data = dict(json.load(open(cg.data_fp)))

    # names=[Database(x).filename + u".geomapping"
    #     for x in self.databases
    # ],

    geocollections['gdp-weighted-pop-density'] = {
        'filepath': download_file("gdpweighted.tiff", "reg")
    }
    xt = ExtensionTable('gdp-weighted-pop-density')
    xt.register(geocollection='gdp-weighted-pop-density')
    xt.import_from_map()
    intersection = Intersection(('ecoinvent-topology', "gdp-weighted-pop-density"))
    intersection.import_from_pandarus(download_file("", "reg"))

    # geocollections['cropland'] = {
    #     'filepath': download_file("cropland.tiff", "reg")
    # }
    # xt = ExtensionTable("cropland")
    # xt.register(geocollection="cropland")
    # xt.import_from_map()
    # intersection = Intersection(('ecoinvent-topology', "cropland"))
    # intersection.import_from_pandarus(download_file("", "reg"))

def import_lc_impact_lcia_method():
    """Import the `LC IMPACT <http://www.lc-impact.eu/>`__ LCIA method"""
    assert 'ecoinvent-topology' in geocollections, "Please install base data (`import_base_reg_data`) first"

    warnings.warn(LC_IMPACT_WARNING)

    # intersection = Intersection(("ammonia", "cropland"))
    # intersection.import_from_pandarus("/Users/cmutel/Projects/Regionalization/SETAC Barcelona/bw2reg/ammonia-cropland.json.bz2")

    intersection = Intersection(("ammonia", "gdp-weighted-pop"))
    intersection.import_from_pandarus("/Users/cmutel/Projects/Regionalization/SETAC Barcelona/bw2reg/ammonia-gdpweighted.json.bz2")

    # intersection = Intersection(("eut", "gdp-weighted-pop"))
    # intersection.import_from_pandarus("/Users/cmutel/Projects/Regionalization/SETAC Barcelona/bw2reg/eut-gdp.json.bz2")

    # intersection = Intersection(("eut", "cropland"))
    # intersection.import_from_pandarus("/Users/cmutel/Projects/Regionalization/SETAC Barcelona/bw2reg/eut-cropland.json.bz2")

    # eutrophication_method = Method(("LC IMPACT", "eutrophication"))
    # eutrophication_method.register(band=1, unit="unknown")

    # import_regionalized_cfs(
    #     "eut",
    #     eutrophication_method,
    #     {1: [
    #             (u'biosphere3', u'b1fca66f-8e83-469a-a7b5-018e14d5d545'),
    #             (u'biosphere3', u'b2631209-8374-431e-b7d5-56c96c6b6d79'),
    #             (u'biosphere3', u'2d4b8ec1-8d53-4e62-8a11-ebc45909b02e'),
    #             (u'biosphere3', u'62f3d964-9b53-4d01-9ee0-04112dcfc6d2'),
    #             (u'biosphere3', u'76b09afe-52b9-4ecc-b97a-00b49ad8ed1a'),
    #         ]
    #     }
    # )

    acidification_method = Method((u"LC IMPACT", u"acidification"))
    acidification_method.register(band=1, unit="Unknown")

    import_regionalized_cfs(
        "ammonia",
        acidification_method,
        {1: [
                (u'biosphere3', u'0f440cc0-0f74-446d-99d6-8ff0e97a2444'),
                (u'biosphere3', u'8494ed3c-0416-4aa5-b100-51a2b2bcadbd'),
                (u'biosphere3', u'2b50f643-216a-412b-a0e5-5946867aa2ed'),
                (u'biosphere3', u'87883a4e-1e3e-4c9d-90c0-f1bea36f8014'),
                (u'biosphere3', u'9990b51b-7023-4700-bca0-1a32ef921f74')
            ]
        }
    )
    acid_cf_data = acidification_method.load()
    flows = [
        (u'biosphere3', u'0f440cc0-0f74-446d-99d6-8ff0e97a2444'),
        (u'biosphere3', u'8494ed3c-0416-4aa5-b100-51a2b2bcadbd'),
        (u'biosphere3', u'2b50f643-216a-412b-a0e5-5946867aa2ed'),
        (u'biosphere3', u'87883a4e-1e3e-4c9d-90c0-f1bea36f8014'),
        (u'biosphere3', u'9990b51b-7023-4700-bca0-1a32ef921f74')
    ]
    for flow in flows:
        acid_cf_data.append((flow, 1.48e-10, "GLO"))
    acidification_method.write(acid_cf_data)
