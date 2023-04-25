import copy
import warnings
import itertools

from bw2data import geomapping
from bw2data.ia_data_store import ImpactAssessmentDataStore

from .meta import intersections
from .utils import create_certain_datapackage
from .validate import intersection_validator


class Intersection(ImpactAssessmentDataStore):
    """ """

    _metadata = intersections
    validator = intersection_validator
    matrix = "intersection_matrix"

    def add_geomappings(self, data):
        """Add all geographic units in both geocollections to ``geomapping``, the master location list.

        Called automatically when data is written."""
        geomapping.add({x[0] for x in data})
        geomapping.add({x[1] for x in data})

    def create_reversed_intersection(self):
        """Create (B, A) intersection from (A, B)."""
        new_name = (self.name[1], self.name[0])
        new_data = [(line[1], line[0], line[2]) for line in self.load()]

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            new_obj = Intersection(new_name)
            new_obj.register(**copy.deepcopy(self.metadata))
            new_obj.write(new_data)

        return new_obj

    def process(self, **extra_metadata):
        data = self.load()
        create_certain_datapackage(
            [(geomapping[line[0]], geomapping[line[1]]) for line in data],
            [line[2] for line in data],
            self,
            **extra_metadata
        )


def calculate_needed_intersections(functional_unit, lcia_method, xtable=None, engine='geopandas'):
    from . import extension_tables
    from .gis_tasks import calculate_intersection
    from .lca.base_class import RegionalizationBase

    RB = RegionalizationBase(demand=functional_unit)
    RB.method = lcia_method
    inv_geocollections = RB.get_inventory_geocollections()
    ia_geocollections = RB.get_ia_geocollections()

    if xtable is None:
        for (x, y) in itertools.product(inv_geocollections, ia_geocollections):
            if (x, y) not in intersections:
                calculate_intersection(x, y, engine=engine)
    else:
        xt_geocollections = [extension_tables[xtable]['geocollection']]
        for (x, y) in itertools.product(inv_geocollections, xt_geocollections):
            if (x, y) not in intersections:
                calculate_intersection(x, y, engine=engine)
        for (x, y) in itertools.product(xt_geocollections, ia_geocollections):
            if (x, y) not in intersections:
                calculate_intersection(x, y, engine=engine)
