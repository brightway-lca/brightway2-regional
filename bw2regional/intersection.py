import copy
import warnings

from bw2data import geomapping
from bw2data.ia_data_store import ImpactAssessmentDataStore

from .meta import intersections
from .validate import intersection_validator
from .utils import create_certain_datapackage


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
        create_certain_datapackage([(geomapping[line[0]], geomapping[line[1]]) for line in data], [line[2] for line in data], self, **extra_metadata)
