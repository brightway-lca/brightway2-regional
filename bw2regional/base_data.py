# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from . import (
    cg,
    ExtensionTable,
    geocollections,
    import_regionalized_cfs,
    Intersection,
    intersections,
    remote,
    restofworlds,
    topocollections,
    Topography,
)
from brightway2 import config, geomapping, Method, Database
from bw2data.utils import download_file
import json
import os
import requests
import warnings


def bw2regionalsetup(*args, overwrite=False):
    """Import base data needed for regionalization.

    Inputs (``args``) are geocollections to install, given individually. Default is ``ecoinvent`` and ``world``.

    ``overwrite`` controls whether existing geocollections will be replaced."""
    # TODO: add RoWs to available_geocollections
    available_geocollections = {'ecoinvent', 'world'}
    if not args:
        args = available_geocollections
    for gc in args:
        if (gc == 'world') and ('world' not in geocollections or overwrite):
            create_world()
        elif (gc == 'ecoinvent') and ('ecoinvent' not in geocollections or overwrite):
            create_ecoinvent()
        else:
            raise ValueError("{} not recognized geocollection".format(gc))


def create_world():
    print("Downloading and creating ``world`` geocollection with countries")
    geocollections['world'] = {
        'filepath': download_file(
            "countries.gpkg",
            "regional",
            url="https://geography.ecoinvent.org/files/"
        ),
        'field': "isotwolettercode"
    }
    print("Downloading and creating ``world`` topocollection")
    topocollections['world'] = {
        'geocollection': 'world',
        'filepath': cg.faces_fp,
        'field': 'id'
    }
    print("Adding world topology")
    world_topo_data = {
        k: v for k, v in cg.data.items()
        if k != '__all__' and len(k) == 2
    }
    Topography('world').write(dict(world_topo_data))


def create_ecoinvent():
    print("Downloading and creating ``ecoinvent`` geocollection with ecoinvent-specific locations")
    geocollections['ecoinvent'] = {
        'filepath': download_file(
            "all-ecoinvent.gpkg",
            "regional",
            url="https://geography.ecoinvent.org/files/"
        ),
        'field': 'shortname'
    }
    print("Downloading and creating ``ecoinvent`` topocollection")
    topocollections['world'] = {
        'geocollection': 'ecoinvent',
        'filepath': cg.faces_fp,
        'field': 'id'
    }
    print("Adding ecoinvent-specific topology")
    ecoinvent_topo_data = {
        ("ecoinvent", k): v for k, v in cg.data.items()
        if k != '__all__' and len(k) != 2
    }
    Topography('ecoinvent').write(ecoinvent_topo_data)




# if remote.alive:
#     print("Retrieving and processing intersections")
#     remote.intersection('world', 'gdp-weighted-pop-density')
# else:
#     print("Skipping creation of intersections - pandarus_remote server is down")
