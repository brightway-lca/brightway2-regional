# -*- coding: utf-8 -*

class UnprocessedDatabase(StandardError):
    """A ``Database`` object doesn't have a list of reference geocollections."""
    pass


class SiteGenericMethod(StandardError):
    """This ``Method`` doesn't have links to ``geocollections``, making it site-generic."""
    pass


class MissingIntersection(StandardError):
    """Missing an ``Intersection`` object and its data needed for regionalized LCA"""
    pass


class GeocollectionsMismatch(StandardError):
    pass


class MissingSpatialSourceData(StandardError):
    pass
