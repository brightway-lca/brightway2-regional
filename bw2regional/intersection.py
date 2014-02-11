# -*- coding: utf-8 -*
from bw2data import geomapping, JsonWrapper
from bw2data.ia_data_store import ImpactAssessmentDataStore
from bw2data.utils import MAX_INT_32
from .validate import intersection_validator
from .meta import intersections
import numpy as np


class Intersection(ImpactAssessmentDataStore):
    """"""
    metadata = intersections
    validator = intersection_validator
    dtype_fields = [
            ('geo_inv', np.uint32),
            ('geo_ia', np.uint32),
            ('row', np.uint32),
            ('col', np.uint32),
    ]

    def add_mappings(self, data):
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
        if self.name not in self.metadata:
            self.register()
        assert isinstance(self.name, tuple) and len(self.name) == 2
        try:
            data = JsonWrapper.load_bz2(filepath)
        except:
            data = JsonWrapper.load(filepath)

        data = [((self.name[0], row[0]), (self.name[1], row[1]), row[2])
            for row in data]

        self.write(data)
        self.process()
        self.metadata[self.name]['filepath'] =  filepath
        self.metadata.flush()
