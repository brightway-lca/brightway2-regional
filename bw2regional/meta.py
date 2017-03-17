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


@python_2_unicode_compatible
class Intersections(CompoundJSONDict):
    """Areal intersections between the elements of two geo- or topocollections"""
    filename = "intersections.json"


@python_2_unicode_compatible
class RestOfWorlds(CompoundJSONDict):
    """Definitions of Rest-of-World locations by what they exclude.

    Exclusions are a list of codes, but should be treated as a set."""
    filename = "restofworlds.json"


@python_2_unicode_compatible
class Geocollections(SerializedDict):
    """Metadata for spatial data sets."""
    filename = "geocollections.json"

    def __setitem__(self, key, value):
        from .utils import get_spatial_dataset_kind

        if 'filepath' in value:
            assert os.path.isfile(value['filepath']), \
                "Can't find file at `{}`".format(value['filepath'])
            value['sha256'] = sha256(value['filepath'])
            value['kind'] = get_spatial_dataset_kind(value['filepath'])
        super(Geocollections, self).__setitem__(key, value)


@python_2_unicode_compatible
class Topocollections(Geocollections):
    """Mappings from geocollections to a set of topographical face ids."""
    filename = "topocollections.json"

    def __setitem__(self, key, value):
        value['empty'] = value.get('empty', True)
        if 'geocollection' not in value:
            raise ValueError("topocollections must be linked to exactly one geocollection")
        elif value['geocollection'] not in geocollections:
            raise ValueError("Linked geocollection {} does not exist".format(
                value['geocollection']))
        super(Topocollections, self).__setitem__(key, value)


@python_2_unicode_compatible
class ExtensionTables(SerializedDict):
    """Metadata for extension tables that give loadings on a third spatial scale."""
    filename = "extension-tables.json"


extension_tables = ExtensionTables()
geocollections = Geocollections()
intersections = Intersections()
loadings = Loadings()
restofworlds = RestOfWorlds()
topocollections = Topocollections()
