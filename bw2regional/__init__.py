# -*- coding: utf-8 -*
__version__ = (0, 2)

from .base_data import import_base_reg_data, import_lc_impact_lcia_method
from .graphics import RegionalizedGrapher
from .intersection import Intersection
from .lca import TwoSpatialScalesWithGenericLoadingLCA, TwoSpatialScalesLCA, OneSpatialScaleLCA, ExtensionTablesLCA
from .loading import Loading
from .meta import loadings, intersections, geocollections, extension_tables
from .utils import import_regionalized_cfs, create_empty_intersection, reset_geo_meta
from .xtables import ExtensionTable

from bw2data import config
config.metadata.extend([
    extension_tables,
    geocollections,
    intersections,
    loadings,
])
