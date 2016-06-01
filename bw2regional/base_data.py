# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from . import (
    cg,
    ExtensionTable,
    geocollections,
    import_regionalized_cfs,
    Intersection,
    remote,
    restofworlds,
    topocollections,
    Topography,
)
from brightway2 import config, geomapping, Method
from bw2data.utils import download_file
import json
import os
import requests
import warnings


LC_IMPACT_WARNING = """This is a preliminary implementation of LC IMPACT!
It is incomplete, and some values will change.
"""


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

    print("Adding GDP-weighted population density map")
    geocollections['gdp-weighted-pop-density'] = {
        'filepath': download_file(
            "gdpweighted-compressed.tiff",
            "regional",
        )
    }
    print("Adding crop intensity maps")
    geocollections['crops'] = {
        'filepath': download_file(
            "cropland-compressed.tiff",
            "regional",
        )
    }

    print("Creating GDP-weighted population density extension table")
    xt = ExtensionTable('gdp-weighted-pop-density')
    xt.register(geocollection='gdp-weighted-pop-density')
    xt.import_from_map()

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

    if remote.alive:
        print("Retrieving and processing intersections")
        remote.intersection('world', 'gdp-weighted-pop-density')
    else:
        print("Skipping creation of intersections - pandarus_remote server is down")


def import_lc_impact_lcia_method():
    """Import the `LC IMPACT <http://www.lc-impact.eu/>`__ LCIA method"""
    assert 'ecoinvent' in geocollections, "Please install base data (function `bw2regionalsetup`) first"

    warnings.warn(LC_IMPACT_WARNING)

    print("Downloading rice-intensity map")
    geocollections['rice'] = {
        'filepath': download_file(
            "rice-supercompressed.tiff",
            "regional",
        )
    }

    print("Adding ammonia characterization factors map")
    geocollections['ammonia'] = {
        'filepath': download_file(
            "ammonia.tiff",
            "regional"
    )}
    print("Adding water consumption - human health impacts map")
    geocollections['watersheds'] = {
        'filepath': download_file(
            "water_hh.gpkg",
            "regional"
    )}
    print("Adding air pollution CFs map")
    geocollections['air regions'] = {
        'filepath': download_file(
            "air_pollution_cfs.gpkg",
            "regional"
    )}

    if remote.alive:
        print("Retrieving and processing intersections")
        remote.intersection('world', 'crops')
        remote.intersection('world', 'rice')
        remote.intersection('gdp-weighted-pop-density', 'rice')
        remote.intersection('world', 'air regions')
        remote.intersection('rice', 'air regions')
        remote.intersection('crops', 'air regions')
        remote.intersection('gdp-weighted-pop-density', 'air regions')
    else:
        print("Skipping creation of intersections - pandarus_remote server is down")

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

    print("Creating acidification method")
    acidification_method = Method((u"LC IMPACT", u"acidification"))
    acidification_method.register(
        band=1,
        unit="Unknown",
        geocollections=['ammonia']
    )

    # Site-generic CFs
    flows = [
        (u'biosphere3', u'0f440cc0-0f74-446d-99d6-8ff0e97a2444'),
        (u'biosphere3', u'8494ed3c-0416-4aa5-b100-51a2b2bcadbd'),
        (u'biosphere3', u'2b50f643-216a-412b-a0e5-5946867aa2ed'),
        (u'biosphere3', u'87883a4e-1e3e-4c9d-90c0-f1bea36f8014'),
        (u'biosphere3', u'9990b51b-7023-4700-bca0-1a32ef921f74')
    ]
    acidification_method.write([(flow, 1.48e-10, "GLO") for flow in flows])

    # Regionalized
    import_regionalized_cfs(
        "ammonia",
        acidification_method,
        {1: flows},
        overwrite=False
    )
