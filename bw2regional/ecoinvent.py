# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from . import cg
from bw2data import databases, Database, geomapping
import json
import pprint
import pyprind
import fiona


_32_FIXED_CODES = {
    "Al producing Area 2, North America": "IAI Area 2, North America",
    "IAI Area 1": "IAI Area 1, Africa",
    "IAI Area 3": "IAI Area 3, South America",
    "IAI Area 4&5 without China": "IAI Area 4&5, without China",
    "IAI Area 6A": "IAI Area 6, Europe",
    "IAI Area 8": "IAI Area 8, Gulf",
}


def fix_ecoinvent_32_codes(code):
    """Fix ecoinvent shortnames that weren't updated for 3.2 release"""
    return _32_FIXED_CODES.get(code, code)


def convert_default_ecoinvent_locations(code):
    """Convert to `ecoinvent` geocollection if necessary"""
    if len(code) == 2 or code in {"GLO", "RoW"}:
        return code
    else:
        return ("ecoinvent", fix_ecoinvent_32_codes(code))


def discretize_rest_of_world(database, warn=True):
    """Create new locations for each unique rest of the world (RoW). A RoW location is defined by the topological faces that aren't covered by a specific market.

    We define a product system by the combination of name and reference product. For each product system, we find the locations where markets are defined. In some cases, only a global market is present, or there is no RoW market because certain products are only available in certain places. However, there will be a RoW market for most product systems in ecoinvent.

    We start by creating two dictionaries:

        * ``locations``: {(``name``, ``reference product``): [list of locations]
        * ``activities``: {dataset key: (``name``, ``reference product``) if ``location`` == ``RoW``}

    Then process ``locations`` and include only location lists where ``RoW`` is present.

    Then create and label the unique set of RoW locations in another dictionary:

        * ``row_locations``: {frozenset([locations]): ``RoW-X``} where X is an counter

    We can then go through ``activities``, look up the list of locations in ``locations``, and get the specific RoW name in ``row_locations``.

    """
    assert database in databases, "Unknown database"

    database = Database(database)
    locations, activities, exceptions = {}, {}, []

    for ds in database:
        label = (ds['name'], ds['reference product'])
        locations.setdefault(label, []).append(ds['location'])
        if ds['location'] == 'RoW':
            activities[ds.key] = label

    for key, value in locations.items():
        # Check for well-defined RoW markets, i.e. yes RoW but no GLO
        if "GLO" in value:
            assert value == ["GLO"], "Market {} include GLO location".format(key)
        elif "RoW" not in value:
            exceptions.append(key)

    if exceptions and warn:
        print("Can't find `RoW` location in the following markets. This is not necessarily an error!")
        pprint.pprint(exceptions)

    locations = {
        k: tuple(sorted(v))
        for k, v in locations.items()
        if k not in exceptions
    }

    # Shouldn't be possible to have any repeated locations in a RoW exclusion list
    for k, v in locations.items():
        assert len(v) == len(set(v)), \
            "Locations repeated in market {}: {}".format(k, v)

    row_locations = {
        obj: "RoW-{}".format(index)
        for index, obj in enumerate(sorted(set(locations.values())))
    }

    # labels = {}

    # for act_key, act_location in activities.items():
    #     labels[act_key] = row_locations[frozenset(locations[act_location])]

    return activities, row_locations, locations


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


def fix_ecoinvent_database(name):
    """Fix spatial definitions in ecoinvent-like databases.

    #. Relabel Rest-of-World locations to be spatially explicit
    #. Relabel ecoinvent locations to be part of the ``ecoinvent`` geocollection.

    """
    assert name in databases, "Unknown database"
    # TODO: Test that base data is installed

    db = Database(name)
    db.make_unsearchable()

    for act in pyprind.ProgBar(db):
        act['location'] = convert_default_ecoinvent_locations(act['location'])
        act.save()

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

    db.make_searchable()
