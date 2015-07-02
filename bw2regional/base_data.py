# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from bw2data.utils import download_file
from .meta import geocollections


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
    geocollections['gdp-weighted-pop-density'] = {
        'filepath': download_file("gdpweighted.tiff", "reg")
    }
    geocollections['cropland'] = {
        'filepath': download_file("cropland.tiff", "reg")
    }


def import_lc_impact_lcia_method():
    """Import the `LC IMPACT <http://www.lc-impact.eu/>`__ LCIA method"""
    pass
