# -*- coding: utf-8 -*
__version__ = (0, 2)

from .graphics import RegionalizedGrapher
from .intersection import Intersection
from .lca import TwoSpatialScalesWithGenericLoadingLCA, TwoSpatialScalesLCA, OneSpatialScaleLCA, ExtensionTablesLCA
from .loading import Loading
from .meta import loadings, intersections, geocollections, extension_tables
from .utils import import_regionalized_cfs, create_empty_intersection, reset_geo_meta
from .xtables import ExtensionTable
from .base_data import import_base_reg_data, import_lc_impact_lcia_method
from .ecoinvent import fix_ecoinvent_location_names, discretize_rest_of_world

from bw2data import config
config.metadata.extend([
    extension_tables,
    geocollections,
    intersections,
    loadings,
])
