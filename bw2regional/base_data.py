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


def bw2regionalsetup():
    """Import base data needed for regionalization.

    See :ref:`basedata` for more information."""

    # print("Downloading and creating Rest-of-the-World definitions")
    # url = "http://geography.ecoinvent.org/report/files/rows-ecoinvent.json"
    # resp = requests.get(url)
    # row_data = json.loads(resp.content.decode('utf8'))
    # restofworlds.data = {("RoW", k): tuple(v) for k, v in row_data}
    # restofworlds.flush()
    # geocollections['RoW'] = {}
    # 'filepath': download_file(
    #     "rows.gpkg",
    #     "regional",
    #     url="http://geography.ecoinvent.org/report/files/"
    # ),
    # 'field': 'name',

    if geocollections:
        print("Geocollections already present!!! No setup is needed")
        return

    print("Downloading and creating world geocollections")
    geocollections['world'] = {
        'filepath': download_file(
            "countries.gpkg",
            "regional",
            url="http://geography.ecoinvent.org/report/files/"
        ),
        'field': 'isotwolettercode',
    }
    geocollections['ecoinvent'] = {
        'filepath': download_file(
            "all-ecoinvent.gpkg",
            "regional",
            url="http://geography.ecoinvent.org/report/files/"
        ),
        'field': 'shortname',
    }
    # topocollections['RoW'] = {
    #     'geocollection': 'RoW',
    #     'filepath': cg.faces_fp,
    #     'field': 'id'
    # }
    topocollections['world'] = {
        'geocollection': 'world',
        'filepath': cg.faces_fp,
        'field': 'id'
    }
    topocollections['ecoinvent'] = {
        'geocollection': 'ecoinvent',
        'filepath': cg.faces_fp,
        'field': 'id'
    }

    # print("Adding GDP-weighted population density map")
    # geocollections['gdp-weighted-pop-density'] = {
    #     'filepath': download_file(
    #         "gdpweighted-compressed.tiff",
    #         "regional",
    #     )
    # }
    # print("Adding crop intensity maps")
    # geocollections['crops'] = {
    #     'filepath': download_file(
    #         "cropland-compressed.tiff",
    #         "regional",
    #     )
    # }

    # print("Creating GDP-weighted population density extension table")
    # xt = ExtensionTable('gdp-weighted-pop-density')
    # xt.register(geocollection='gdp-weighted-pop-density')
    # xt.import_from_map()

    print("Adding world topology")
    world_topo_data = {
        k: v
        for k, v in cg.data.items()
        if k != '__all__'
        and len(k) == 2
    }
    Topography('world').write(dict(world_topo_data))

    # print("Adding RoW topology")
    # row_topofilepath = download_file(
    #     "rows-topomapping.json",
    #     "regional",
    #     url="http://geography.ecoinvent.org/report/files/"
    # )
    # topo_data = json.load(open(row_topofilepath))
    # assert topocollections['RoW']['sha256'] == topo_data['metadata']['sha256'], \
    #     "Mismatch between topological faces and RoW mapping"
    # row_topo_data = {
    #     ("RoW", x[0]): x[1]
    #     for x in topo_data['data']
    # }
    # Topography('RoW').write(row_topo_data)

    print("Adding ecoinvent-specific topology")
    ecoinvent_topo_data = {
        ("ecoinvent", k): v
        for k, v in cg.data.items()
        if k != '__all__'
        and len(k) != 2
    }
    Topography('ecoinvent').write(ecoinvent_topo_data)

    # if remote.alive:
    #     print("Retrieving and processing intersections")
    #     remote.intersection('world', 'gdp-weighted-pop-density')
    # else:
    #     print("Skipping creation of intersections - pandarus_remote server is down")
