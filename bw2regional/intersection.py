from .meta import intersections
from .validate import intersection_validator
from bw2data import geomapping
from bw2data.ia_data_store import ImpactAssessmentDataStore
from bw2data.utils import MAX_INT_32
import copy
import numpy as np
import warnings


class Intersection(ImpactAssessmentDataStore):
    """ """

    _metadata = intersections
    validator = intersection_validator
    dtype_fields = [
        ("geo_inv", np.uint32),
        ("geo_ia", np.uint32),
        ("row", np.uint32),
        ("col", np.uint32),
    ]

    def add_mappings(self, data):
        """Add all geographic units in both geocollections to ``geomapping``, the master location list.

        Called automatically when data is written."""
        geomapping.add({x[0] for x in data})
        geomapping.add({x[1] for x in data})

    def process_data(self, row):
        return (geomapping[row[0]], geomapping[row[1]], MAX_INT_32, MAX_INT_32), row[2]

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
