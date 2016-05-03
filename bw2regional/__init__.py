# -*- coding: utf-8 -*
__version__ = (0, 3)

__all__ = (
    "bw2regionalsetup",
    "cg",
    "create_empty_intersection",
    "extension_tables",
    "ExtensionTable",
    "ExtensionTablesLCA",
    "geocollections",
    "get_spatial_dataset_kind",
    "hash_collection",
    # "import_lc_impact_lcia_method",
    "import_from_pandarus",
    "import_regionalized_cfs",
    "Intersection",
    "intersections",
    "Loading",
    "loadings",
    "OneSpatialScaleLCA",
    "PandarusRemote",
    "RegionalizedGrapher",
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
from .graphics import RegionalizedGrapher
from .area import Area
from .intersection import Intersection
from .lca import (
    ExtensionTablesLCA,
    OneSpatialScaleLCA,
    TopologicalExtensionTablesLCA,
    TwoSpatialScalesLCA,
    TwoSpatialScalesWithGenericLoadingLCA,
)
from .loading import Loading
from .meta import (
    areas,
    extension_tables,
    topocollections,
    geocollections,
    intersections,
    loadings,
    restofworlds,
)
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
from .base_data import (
    bw2regionalsetup,
    import_lc_impact_lcia_method,
)

from bw2data import config
config.metadata.extend([
    extension_tables,
    geocollections,
    topocollections,
    intersections,
    loadings,
])
