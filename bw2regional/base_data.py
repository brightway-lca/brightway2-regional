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
    topocollections,
    Topography,
)
from .hashing import sha256
from bw2data.utils import download_file
import bz2
import json
import os
import requests
import rower
import warnings


COUNTRIES = {
    "AD","AE","AF","AG","AI","AL","AM","AO","AQ","AR","AS","AT","AU","AW","AX",
    "AZ","BA","BB","BD","BE","BF","BG","BH","BI","BJ","BL","BM","BN","BO","BR",
    "BS","BT","BW","BY","BZ","CA","CD","CF","CG","CH","CI","CK","CL","CM","CN",
    "CO","CR","CU","CV","CW","CY","CZ","DE","DJ","DK","DM","DO","DZ","EC","EE",
    "EG","EH","ER","ES","ET","FI","FJ","FK","FM","FO","FR","GA","GB","GD","GE",
    "GG","GH","GI","GL","GM","GN","GQ","GR","GS","GT","GU","GW","GY","HK","HM",
    "HN","HR","HT","HU","ID","IE","IL","IM","IN","IO","IQ","IR","IS","IT","JE",
    "JM","JO","JP","KE","KG","KH","KI","KM","KN","KP","KR","KW","KY","KZ","LA",
    "LB","LC","LI","LK","LR","LS","LT","LU","LV","LY","MA","MC","MD","ME","MF",
    "MG","MH","MK","ML","MM","MN","MO","MP","MR","MS","MT","MU","MV","MW","MX",
    "MY","MZ","NA","NC","NE","NF","NG","NI","NL","NO","NP","NR","NU","NZ","OM",
    "PA","PE","PF","PG","PH","PK","PL","PM","PN","PR","PS","PT","PW","PY","QA",
    "RO","RS","RU","RW","SA","SB","SC","SD","SE","SG","SH","SI","SK","SL","SM",
    "SN","SO","SR","SS","ST","SV","SX","SY","SZ","TC","TD","TF","TG","TH","TJ",
    "TL","TM","TN","TO","TR","TT","TV","TW","TZ","UA","UG","UM","US","UY","UZ",
    "VA","VC","VE","VG","VI","VN","VU","WF","WS","XK","YE","ZA","ZM","ZW"
}


def create_world():
    print("Downloading and creating 'world' geocollection with countries")
    geocollections['world'] = {
        'filepath': download_file(
            "countries.gpkg",
            "regional",
            url="https://geography.ecoinvent.org/files/"
        ),
        'field': "isotwolettercode"
    }
    topocollections['world'] = {
        'geocollection': 'world',
        'filepath': cg.faces_fp,
        'field': 'id'
    }
    topo_data = {
        k: v for k, v in cg.data.items()
        if k in COUNTRIES
    }
    Topography('world').write(topo_data)


def create_ecoinvent():
    print("Downloading and creating 'ecoinvent' geocollection with ecoinvent-specific locations")
    geocollections['ecoinvent'] = {
        'filepath': download_file(
            "all-ecoinvent.gpkg",
            "regional",
            url="https://geography.ecoinvent.org/files/"
        ),
        'field': 'shortname'
    }
    topocollections['ecoinvent'] = {
        'geocollection': 'ecoinvent',
        'filepath': cg.faces_fp,
        'field': 'id'
    }
    topo_data = {
        ("ecoinvent", k): v for k, v in cg.data.items()
        if k != '__all__' and "RoW" not in k and k not in COUNTRIES
    }
    Topography('ecoinvent').write(topo_data)


def create_RoW():
    filepath = os.path.join(rower.DATAPATH, "ecoinvent generic", "rows-topomapping.json.bz2")
    with bz2.BZ2File(filepath) as f:
        rower_data = json.load(f)

    if sha256(cg.faces_fp) != rower_data['metadata']['sha256']:
        warnings.warn("Inconsistent `rower` and `constructive_geometries` packages. Skipping 'RoW' creation")
        return

    print("Creating `rower` 'RoW' geo/topocollections")
    geocollections['RoW'] = {}
    topocollections['RoW'] = {
        'geocollection': 'RoW',
        'filepath': cg.faces_fp,
        'field': 'id'
    }
    topo_data = {("RoW", k): v for k, v in rower_data['data']}
    Topography('RoW').write(topo_data)


def bw2regionalsetup(*args, overwrite=False):
    """Import base data needed for regionalization.

    Inputs (``args``) are geocollections to install, given individually. Default is ``ecoinvent``, ``RoW``, and ``world``.

    ``overwrite`` controls whether existing geocollections will be replaced."""
    available_geocollections = {'ecoinvent', 'world', 'RoW'}
    mapping = {
        'world': create_world,
        'ecoinvent': create_ecoinvent,
        'RoW': create_RoW,
    }
    for gc in args or available_geocollections:
        try:
            func = mapping[gc]
            if gc not in geocollections or overwrite:
                func()
        except KeyError:
            raise ValueError("{} not recognized geocollection".format(gc))
