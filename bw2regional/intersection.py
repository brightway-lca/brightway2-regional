import copy
import warnings

import geopandas as gp
from bw2data import geomapping
from bw2data.ia_data_store import ImpactAssessmentDataStore

from .meta import geocollections, intersections
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


def write_intersection(first, second, overwrite=False):
    """Calculate and write areal intersections between two vector geocollections"""
    if (first, second) in intersections and not overwrite:
        raise ValueError("Intersection already exists")

    for gc in (first, second):
        assert (
            gc in geocollections
            and geocollections[gc].get("kind") == "vector"
            and "field" in geocollections[gc]
        )
    assert geocollections[first]["filepath"] != geocollections[second]["filepath"]

    df1 = gp.read_file(geocollections[first]["filepath"])
    df2 = gp.read_file(geocollections[second]["filepath"])
    id1 = geocollections[first]["field"]
    id2 = geocollections[second]["field"]

    assert id1 != id2, "Conflicting ID labels"

    intersection = gp.overlay(df1, df2)
    areas = intersection.to_crs("esri:54009").area  # World Mollweidge in square meters

    data = []
    for index, feature in intersection.iterrows():
        data.append(((first, feature[id1]), (second, feature[id2]), areas[index]))

    obj = Intersection((first, second))
    obj.write(data)
    obj.create_reversed_intersection()
