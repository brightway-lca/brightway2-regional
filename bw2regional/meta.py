# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *
from future.utils import python_2_unicode_compatible

from bw2data.serialization import (
    CompoundJSONDict,
    PickledDict,
    SerializedDict,
)
from .hashing import sha256
import os


@python_2_unicode_compatible
class Loadings(SerializedDict):
    """Metadata on regionalized LCIA weightings."""
    filename = "loadings.json"

    def __str__(self):
        return ("Brightway2 regionalized LCIA loading metadata: {} data sets"
                ).format(len(self))


@python_2_unicode_compatible
class Intersections(CompoundJSONDict):
    """Areal intersections between the elements of two geo- or topocollections"""
    filename = "intersections.json"

    def __str__(self):
        return ("Brightway2 LCI/LCIA areal intersection metadata: {} data sets"
                ).format(len(self))


@python_2_unicode_compatible
class Geocollections(SerializedDict):
    """Metadata for spatial data sets."""
    filename = "geocollections.json"

    def __str__(self):
        return "Brightway2 geocollections metadata: {} data sets".format(len(self))

    def __setitem__(self, key, value):
        if 'filepath' in value:
            assert os.path.isfile(value['filepath']), \
                "Can't find file at `{}`".format(value['filepath'])
            value['sha256'] = sha256(value['filepath'])
        super(Geocollections, self).__setitem__(key, value)


@python_2_unicode_compatible
class Topocollections(Geocollections):
    """Mappings from geocollections to a set of topographical face ids."""
    filename = "topocollections.json"

    def __str__(self):
        return "Brightway2 topocollections metadata: {} data sets".format(len(self))


@python_2_unicode_compatible
class ExtensionTables(SerializedDict):
    """Metadata for extension tables that give loadings on a third spatial scale."""
    filename = "extension-tables.json"

    def __str__(self):
        return "Brightway extension tables metadata: {} tables".format(len(self))


loadings = Loadings()
intersections = Intersections()
geocollections = Geocollections()
topocollections = Topocollections()
extension_tables = ExtensionTables()
