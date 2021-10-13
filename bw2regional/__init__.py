# -*- coding: utf-8 -*
__version__ = (0, 5, 2)

__all__ = (
    "bw2regionalsetup",
    "cg",
    "create_empty_intersection",
    "divide_by_area",
    "extension_tables",
    "ExtensionTable",
    "ExtensionTablesLCA",
    "geocollections",
    "get_spatial_dataset_kind",
    "hash_collection",
    "import_from_pandarus",
    "import_regionalized_cfs",
    "Intersection",
    "intersections",
    "label_activity_geocollections",
    "Loading",
    "loadings",
    "OneSpatialScaleLCA",
    "PandarusRemote",
    "remote",
    "reset_all_geo",
    "reset_geo_meta",
    "sha256",
    "topocollections",
    "Topography",
    "TopologicalExtensionTablesLCA",
    "TwoSpatialScalesLCA",
    "TwoSpatialScalesWithGenericLoadingLCA",
)

from constructive_geometries import ConstructiveGeometries

cg = ConstructiveGeometries()

from bw2data import config

from .base_data import bw2regionalsetup
from .databases import label_activity_geocollections
from .density import divide_by_area
from .hashing import sha256
from .intersection import Intersection
from .lca import (ExtensionTablesLCA, OneSpatialScaleLCA,
                  TopologicalExtensionTablesLCA, TwoSpatialScalesLCA,
                  TwoSpatialScalesWithGenericLoadingLCA)
from .loading import Loading
from .meta import (extension_tables, geocollections, intersections, loadings,
                   topocollections)
from .pandarus import import_from_pandarus
from .pandarus_remote import PandarusRemote, remote
from .topography import Topography
from .utils import (create_empty_intersection, get_spatial_dataset_kind,
                    hash_collection, import_regionalized_cfs, reset_all_geo,
                    reset_geo_meta)
from .xtables import ExtensionTable

config.metadata.extend(
    [extension_tables, geocollections, topocollections, intersections, loadings]
)
