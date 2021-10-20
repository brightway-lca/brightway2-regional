from pathlib import Path

from bw2data.serialization import CompoundJSONDict, SerializedDict

from .hashing import sha256


class Loadings(SerializedDict):
    """Metadata on regionalized LCIA weightings."""

    filename = "loadings.json"


class Intersections(CompoundJSONDict):
    """Areal intersections between the elements of two geo- or topocollections"""

    filename = "intersections.json"


class Geocollections(SerializedDict):
    """Metadata for spatial data sets."""

    filename = "geocollections.json"

    def __setitem__(self, key, value):
        from .utils import get_spatial_dataset_kind

        if "filepath" in value:
            assert Path(value["filepath"]).is_file(), "Can't find file at `{}`".format(
                value["filepath"]
            )
            value["sha256"] = sha256(value["filepath"])
            value["kind"] = get_spatial_dataset_kind(value["filepath"])
        super(Geocollections, self).__setitem__(key, value)


class Topocollections(Geocollections):
    """Mappings from geocollections to a set of topographical face ids."""

    filename = "topocollections.json"

    def __setitem__(self, key, value):
        value["empty"] = value.get("empty", True)
        if "geocollection" not in value:
            raise ValueError(
                "topocollections must be linked to exactly one geocollection"
            )
        elif value["geocollection"] not in geocollections:
            raise ValueError(
                "Linked geocollection {} does not exist".format(value["geocollection"])
            )
        super(Topocollections, self).__setitem__(key, value)


class ExtensionTables(SerializedDict):
    """Metadata for extension tables that give loadings on a third spatial scale."""

    filename = "extension-tables.json"


extension_tables = ExtensionTables()
geocollections = Geocollections()
intersections = Intersections()
loadings = Loadings()
topocollections = Topocollections()
