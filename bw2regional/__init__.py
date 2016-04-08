# -*- coding: utf-8 -*
__version__ = (0, 3)

__all__ = (
    "bw2regionalsetup",
    "create_empty_intersection",
    "extension_tables",
    "ExtensionTable",
    "ExtensionTablesLCA",
    "geocollections",
    "import_lc_impact_lcia_method",
    "import_regionalized_cfs",
    "import_standard_geocollections",
    "Intersection",
    "intersections",
    "Loading",
    "loadings",
    "OneSpatialScaleLCA",
    "PandarusRemote",
    "RegionalizedGrapher",
    "remote",
    "reset_geo_meta",
    "topocollections",
    "Topography",
    "TopologicalExtensionTablesLCA",
    "TwoSpatialScalesLCA",
    "TwoSpatialScalesWithGenericLoadingLCA",
)

from .graphics import RegionalizedGrapher
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
    extension_tables,
    topocollections,
    geocollections,
    intersections,
    loadings,
)
from .topography import Topography
from .utils import (
    convert_default_ecoinvent_locations,
    create_empty_intersection,
    import_regionalized_cfs,
    reset_geo_meta,
)
from .xtables import ExtensionTable
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

from .remote import remote, PandarusRemote

# TODO: Get default list of country codes
