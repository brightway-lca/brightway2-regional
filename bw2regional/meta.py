# -*- coding: utf-8 -*
from bw2data.serialization import SerializedDict, CompoundJSONDict


class Loadings(SerializedDict):
    """A dictionary for metadata on regionalized LCIA weightings.

    File is saved in ``loading.json``

    Metdata fields:
        *

    """
    filename = "loadings.json"

    def __unicode__(self):
        return u"Brightway2 regionalized LCIA loading metadata: %i data sets" % len(self)


class Intersections(CompoundJSONDict):
    """"""
    filename = "intersections.json"

    def __unicode__(self):
        return u"Brightway2 LCI/LCIA areal intersection metadata: %s data sets" % len(self)


class Geocollections(SerializedDict):
    """Metadata for spatial data sets."""
    filename = "geocollections.json"

    def __unicode__(self):
        return u"Brightway2 geocollections metadata: %i data sets" % len(self)


class ExtensionTables(SerializedDict):
    """Metadata for extension tables."""
    filename = "extension-tables.json"

    def __unicode__(self):
        return u"Brightway extension tables metadata: %i tables" % len(self)


loadings = Loadings()
intersections = Intersections()
geocollections = Geocollections()
extension_tables = ExtensionTables()
