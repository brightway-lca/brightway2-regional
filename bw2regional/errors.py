# -*- coding: utf-8 -*

class UnprocessedDatabase(Exception):
    """A ``Database`` object doesn't have a list of reference geocollections."""
    pass


class SiteGenericMethod(Exception):
    """This ``Method`` doesn't have links to ``geocollections``, making it site-generic."""
    pass


class MissingIntersection(Exception):
    """Missing an ``Intersection`` object and its data needed for regionalized LCA"""
    pass


class GeocollectionsMismatch(Exception):
    pass


class MissingSpatialSourceData(Exception):
    pass
