# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from bw2data.utils import download_file
from .. import geocollections


def import_lcimpact_lcia_method():
    print(
"""WARNING!!! This LCIA method will only work for a suitably prepared LCI database.
When using ecoinvent, you must prepare the database with the following functions:
    * expand_ecoinvent_location_codes
    * label_rest_of_world

Use against LCI databases other than ecoinvent 3.1 is not tested, and not recommended.
"""
    )

    print("Downloading spatial patterns")
    geocollections['gdp-weighted-pop'] = {
        "filepath": download_file("gdpweighted.tiff", "lcimpact")
    }
    geocollections['cropland'] = {
        "filepath": download_file("cropland.tiff", "lcimpact")
    }

    print("Downloading regionalized CFs")
    geocollections['ammonia'] = {
        "filepath": "/Users/cmutel/Projects/Regionalization/SETAC Barcelona/bw2reg/ammonia.tiff"
    }
    geocollections['eut'] = {
        "filepath": "/Users/cmutel/Projects/Regionalization/SETAC Barcelona/bw2reg/eut-water.tiff"
    }
