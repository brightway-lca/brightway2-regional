class BW2RegionalizationError(Exception):
    """Base class for BW2 regionalization errors"""

    pass


class UnprocessedDatabase(BW2RegionalizationError):
    """A ``Database`` object doesn't have a list of reference geocollections."""

    pass


class SiteGenericMethod(BW2RegionalizationError):
    """This ``Method`` doesn't have links to ``geocollections``, making it site-generic."""

    pass


class MissingIntersection(BW2RegionalizationError):
    """Missing an ``Intersection`` object and its data needed for regionalized LCA"""

    pass


class GeocollectionsMismatch(BW2RegionalizationError):
    pass


class MissingSpatialSourceData(BW2RegionalizationError):
    pass


class TopologyError(BW2RegionalizationError):
    """Inventory includes locations for which no topology data is available"""

    pass


class IncompleteSpatialDefinition(BW2RegionalizationError):
    """Given metadata is not enough to understand a spatial data source"""

    pass


class WindowsPathCharacterLimit(BW2RegionalizationError):
    """Windows has an absolute limit of 255 characters in a filepath"""

    pass
