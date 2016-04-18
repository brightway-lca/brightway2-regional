# -*- coding: utf-8 -*
from __future__ import unicode_literals
from eight import *

from .. import geocollections
import fiona
import os


def check_uuids(xml_filepath=None):
    """Check UUIDs and names with ecoinvent master data"""
    # assert os.path.isfile(xml_filepath)
    data = load_ecoinvent_names()


def load_ecoinvent_names():
    assert 'ecoinvent' in geocollections, "Please install base data (function `bw2regionalsetup`) first"

    data = []

    with fiona.drivers():
        with fiona.open(geocollections['ecoinvent']['filepath']) as gpkg:
            for feat in gpkg:
                data.append({
                    'shortname': feat['properties']['shortname'],
                    'name': feat['properties']['name'],
                    'uuid': feat['properties']['uuid']
                })

    return sorted(data, key=lambda x: x.get('name'))
