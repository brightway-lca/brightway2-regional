# -*- coding: utf-8 -*
import os

data_dir = os.path.join(os.path.dirname(__file__), "data")

from .intersections import IntersectionTestCase
from .lca_mixin import RegionalizationBaseTestCase
from .loading import LoadingTestCase
from .meta import IntersectionsTestCase, LoadingsTestCase, GeocollectionsTestCase
from .one_spatial_scale import OneSpatialScaleLCATestCase
from .topography import TopographyTestCase
from .two_spatial_scales import TwoSpatialScalesLCATestCase
from .two_spatial_scales_weighting import TwoSpatialScalesWithGenericLoadingLCATestCase
from .xtables import XtablesTestCase
