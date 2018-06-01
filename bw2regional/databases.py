# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from . import geocollections, Topography, topocollections
from .base_data import COUNTRIES
from bw2data import databases, Database
import pyprind
import warnings


def label_activity_geocollections(name):
    """Add geocollections to activity ``location`` fields.

    ``name`` is the name of an existing LCI database."""
    assert name in databases, "{} not found".format(name)
    assert 'world' in geocollections, "Please run `bw2regionalsetup` before this function"

    ecoinvent = ({x[1] for x in Topography('ecoinvent').load()}
                 if 'ecoinvent' in topocollections else set())
    RoWs = ({x[1] for x in Topography('RoW').load()}
            if 'RoW' in topocollections else set())

    db = Database(name)
    searchable = db.metadata.get('searchable')
    if searchable:
        db.make_unsearchable()

    locations = {x['location'] for x in db}
    assert 'RoW' not in locations, "`RoW` found; use `rower` to label Rest-of-Worlds"

    for act in pyprind.prog_bar(db):
        if isinstance(act['location'], tuple):
            continue
        elif act['location'] in COUNTRIES:
            continue
        elif act['location'] == 'GLO':
            continue
        elif act['location'] in RoWs:
            act['location'] = ("RoW", act['location'])
            act.save()
        elif act['location'] in ecoinvent:
            act['location'] = ("ecoinvent", act['location'])
            act.save()
        else:
            warnings.warn(
                ("Location {} in {} not understood; please add geocollection"
                 " manually").format(act['location'], act.key)
            )

    if searchable:
        db.make_searchable()
    db.process()
