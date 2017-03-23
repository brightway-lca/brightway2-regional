# -*- coding: utf-8 -*
__version__ = (0, 4, 1)

__all__ = (
    "bw2regionalsetup",
    "cg",
    "create_empty_intersection",
    "extension_tables",
    "ExtensionTable",
    "ExtensionTablesLCA",
    "fix_ecoinvent_database",
    "geocollections",
    "get_spatial_dataset_kind",
    "hash_collection",
    "import_from_pandarus",
    "import_regionalized_cfs",
    "Intersection",
    "intersections",
    "Loading",
    "loadings",
    "OneSpatialScaleLCA",
    "PandarusRemote",
    "remote",
    "reset_all_geo",
    "reset_geo_meta",
    "restofworlds",
    "sha256",
    "topocollections",
    "Topography",
    "TopologicalExtensionTablesLCA",
    "TwoSpatialScalesLCA",
    "TwoSpatialScalesWithGenericLoadingLCA",
)

from constructive_geometries import ConstructiveGeometries

cg = ConstructiveGeometries()

from .hashing import sha256
from .intersection import Intersection
from .meta import (
    extension_tables,
    topocollections,
    geocollections,
    intersections,
    loadings,
    restofworlds,
)
from .lca import (
    ExtensionTablesLCA,
    OneSpatialScaleLCA,
    TopologicalExtensionTablesLCA,
    TwoSpatialScalesLCA,
    TwoSpatialScalesWithGenericLoadingLCA,
)
from .loading import Loading
from .topography import Topography
from .utils import (
    create_empty_intersection,
    get_spatial_dataset_kind,
    hash_collection,
    import_regionalized_cfs,
    reset_all_geo,
    reset_geo_meta,
)
from .xtables import ExtensionTable
from .pandarus import import_from_pandarus
from .pandarus_remote import remote, PandarusRemote
from .base_data import bw2regionalsetup
from .ecoinvent import fix_ecoinvent_database


from bw2data import config
config.metadata.extend([
    extension_tables,
    geocollections,
    topocollections,
    intersections,
    loadings,
])
