# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from bw2data.utils import download_file
from .. import geocollections, ExtensionTable,
from ..utils import import_regionalized_cfs

db_warning = """WARNING!!! This LCIA method will only work for a suitably prepared LCI database.
When using ecoinvent, you must prepare the database with the following functions:
    * expand_ecoinvent_location_codes
    * label_rest_of_world

Use against LCI databases other than ecoinvent 3.1 is not tested, and not recommended.
"""


def import_lcimpact_lcia_method():
    print(db_warning)

    print("Downloading and processing spatial patterns: GDP-weighted population")
    geocollections['gdp-weighted-pop'] = {
        "filepath": download_file("gdpweighted.tiff", "lcimpact")
    }
    xt = ExtensionTable("gdp-weighted-pop")
    xt.register(geocollection="gdp-weighted-pop")
    xt.import_from_map()

    print("Downloading and processing spatial patterns: cropland")
    geocollections['cropland'] = {
        "filepath": download_file("cropland.tiff", "lcimpact")
    }
    xt = ExtensionTable("cropland")
    xt.register(geocollection="cropland")
    xt.import_from_map()

    print("Downloading regionalized CFs")
    print("\tAcidification: Ammonia")
    geocollections['ammonia'] = {
        "filepath": download_file("ammonia.tiff", "lcimpact")
    }

    intersection = Intersection(('ecoinvent-topo', "gdp-weighted-pop"))
    intersection.import_from_pandarus(download_file(, "lcimpact"))

    intersection = Intersection(('ecoinvent-topo', "cropland"))
    intersection.import_from_pandarus(download_file(, "lcimpact"))


    acidification_method = Method((u"LC IMPACT", u"acidification"))
    if acidification_method.name not in methods:
        acidification_method.register(band=1, unit="stuff")

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

    # Add global CF
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
