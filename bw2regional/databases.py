import warnings

import pyprind
from bw2data import Database, databases

from . import Topography, geocollections, topocollections
from .base_data import COUNTRIES


def label_activity_geocollections(name):
    """Add geocollections to activity ``location`` fields.

    ``name`` is the name of an existing LCI database."""
    assert name in databases, "{} not found".format(name)
    assert "world" in geocollections, "Please run `create_world_collections` first"

    ecoinvent = (
        {x[1] for x in Topography("ecoinvent").load()}
        if "ecoinvent" in topocollections
        else set()
    )
    RoWs = (
        {x[1] for x in Topography("RoW").load()} if "RoW" in topocollections else set()
    )

    db = Database(name)
    searchable = db.metadata.get("searchable")
    if searchable:
        db.make_unsearchable()

    found_geocollections = set()

    locations = {x["location"] for x in db}
    assert "RoW" not in locations, "`RoW` found; use `rower` to label Rest-of-Worlds"

    for act in pyprind.prog_bar(db):
        if isinstance(act["location"], tuple):
            found_geocollections.add(act["location"][0])
        elif act["location"] in COUNTRIES:
            found_geocollections.add("world")
        elif act["location"] == "GLO":
            found_geocollections.add("world")
        elif act["location"] in RoWs:
            act["location"] = ("RoW", act["location"])
            act.save()
            found_geocollections.add("RoW")
        elif act["location"] in ecoinvent:
            act["location"] = ("ecoinvent", act["location"])
            act.save()
            found_geocollections.add("ecoinvent")
        else:
            warnings.warn(
                (
                    "Location {} in {} not understood; please add geocollection"
                    " manually, and add to databases[name]['geocollections']"
                ).format(act["location"], act.key)
            )

    if searchable:
        db.make_searchable()
    db.process()

    db.metadata["regionalized"] = True
    db.metadata["geocollections"] = sorted(found_geocollections)
    databases.flush()
