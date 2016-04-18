# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from . import faces
from bw2data import databases, Database, geomapping
from constructive_geometries import ConstructiveGeometries
import json
import pprint
import pyprind


def discretize_rest_of_world(database, warn=True):
    """Create new locations for each unique rest of the world (RoW). A RoW location is defined by the topological faces that aren't covered by a specific market.

    We define a product system by the combination of name and reference product. For each product system, we find the locations where markets are defined. In some cases, only a global market is present, or there is no RoW market because certain products are only available in certain places. However, there will be a RoW market for most product systems in ecoinvent.

    We start by creating two dictionaries:

        * ``locations``: {``name`` + ``reference product``: [list of locations]
        * ``activities``: {key: ``name`` + ``reference product`` if ``location`` == ``RoW``}

    Then process ``locations`` and include only location lists where ``RoW`` is present.

    Then create and label the unique set of RoW locations in another dictionary:

        * ``row_locations``: {frozenset([locations]): ``RoW-X``} where X is an counter

    We can then go through ``activities``, look up the list of locations in ``locations``, and get the specific RoW name in ``row_locations``.

    """
    assert database in databases, "Unknown database"

    database = Database(database)
    locations = {}
    activities = {}
    exceptions = []

    for ds in database:
        label = ds['name'] + ":" + ds['reference product']
        locations.setdefault(label, []).append(ds['location'])
        if ds['location'] == 'RoW':
            activities[ds.key] = label

    for key, value in locations.items():
        if "GLO" in value:
            assert value == ["GLO"], "Market {} include GLO location".format(key)
        elif "RoW" not in value:
            exceptions.append(key)

    if exceptions and warn:
        print("Can't find `RoW` location in the following markets. This is not necessarily an error!")
        pprint.pprint(exceptions)

    locations = {k: v for k, v in locations.items() if 'RoW' in v}

    for k, v in locations.items():
        assert len(v) == len(set(v)), \
            "Locations repeated in market {}: {}".format(k, v)

    row_locations = {frozenset(obj): "RoW-{}".format(index)
        for index, obj in enumerate({tuple(sorted(x)) for x in locations.values()})
    }

    labels = {}

    for act_key, act_location in activities.items():
        labels[act_key] = row_locations[frozenset(locations[act_location])]

    return labels, row_locations, locations


def fix_ecoinvent_location_names(name):
    assert name in databases, "Unknown database"
    for act in pyprind.prog_bar(Database(name)):
        try:
            act['location'] = LOCATION_CORRESPONDENCE[act['location']]
            act.save()
        except KeyError:
            pass



def prepare_ecoinvent_database(name):
    def _(obj):
        return (x for x in obj if x != "RoW")

    assert name in databases, "Unknown database"

    cg = ConstructiveGeometries()
    db = Database(name)
    searchable = db._searchable
    if searchable:
        db.make_unsearchable()

    print("Fixing ecoinvent location names")
    geomapping.add(list(LOCATION_CORRESPONDENCE.values()))
    fix_ecoinvent_location_names(name)

    print("Fixing rest of the world locations")
    labels, row_locations, locations = discretize_rest_of_world(name, False)
    geomapping.add(list(labels.values()))
    for key, place in pyprind.prog_bar(labels.items()):
        act = db.get(key[1])
        act['location'] = place
        act.save()

    print("Defining different rest of the world locations")
    row_topo = {name: cg.construct_rest_of_world(list(_(places)), geom=False) for places, name in row_locations.items()}
    faces.update({k: [('ecoinvent-topology', fid) for fid in v]
                      for k, v in row_topo.items()})
    db.process()

    if searchable:
        db.make_searchable()
