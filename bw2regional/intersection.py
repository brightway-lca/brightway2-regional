# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from .meta import intersections
from .validate import intersection_validator
from bw2data import geomapping, JsonWrapper
from bw2data.ia_data_store import ImpactAssessmentDataStore
from bw2data.utils import MAX_INT_32, numpy_string
import copy
import numpy as np
import warnings


class Intersection(ImpactAssessmentDataStore):
    """"""
    _metadata = intersections
    validator = intersection_validator
    dtype_fields = [
            (numpy_string('geo_inv'), np.uint32),
            (numpy_string('geo_ia'), np.uint32),
            (numpy_string('row'), np.uint32),
            (numpy_string('col'), np.uint32),
    ]

    def add_mappings(self, data):
        """Add all geographic units in both geocollections to ``geomapping``, the master location list.

        Called automatically when data is written."""
        geomapping.add({x[0] for x in data})
        geomapping.add({x[1] for x in data})

    def process_data(self, row):
        return (
            geomapping[row[0]],
            geomapping[row[1]],
            MAX_INT_32,
            MAX_INT_32,
            ), row[2]

    def import_from_pandarus(self, filepath):
        """Import a `pandarus` output file.

        The order of geocollections in the output file must be the same as in this intersection. This can't be checked automatically, so it is up to the user to make sure it is correct.

        Also creates the reversed intersection, e.g. if this intersection is `(A,B)`, this method also creates `(B,A)`.

        """
        if not self.registered:
            self.register()
        assert isinstance(self.name, tuple) and len(self.name) == 2
        try:
            data = JsonWrapper.load_bz2(filepath)
        except:
            data = JsonWrapper.load(filepath)

        data = [((self.name[0], row[0]), (self.name[1], row[1]), row[2])
            for row in data]

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.write(data)
            self.metadata['filepath'] =  filepath

        self.create_reversed_intersection()

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
