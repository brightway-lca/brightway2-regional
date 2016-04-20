# -*- coding: utf-8 -*
from __future__ import unicode_literals
from eight import *

from .. import geocollections
import fiona
import os

def load_ecoinvent_names():
    assert 'ecoinvent' in geocollections, "Please install base data (function `bw2regionalsetup`) first"

    data = []

    try:
        assert os.path.isfile(geocollections['ecoinvent']['filepath'])
        with fiona.drivers():
            with fiona.open(geocollections['ecoinvent']['filepath']) as gpkg:
                for feat in gpkg:
                    data.append({
                        'shortname': feat['properties']['shortname'],
                        'name': feat['properties']['name'],
                        'uuid': feat['properties']['uuid']
                    })
    except:
        raise ValueError("Can't load ecoinvent geospatial definitions")

    return sorted(data, key=lambda x: x.get('name'))
