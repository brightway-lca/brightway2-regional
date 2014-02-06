# -*- coding: utf-8 -*
from .meta import loadings
from .validate import loading_validator
from bw2data import geomapping
from bw2data.data_store import DataStore
from bw2data.utils import MAX_INT_32
import numpy as np


class Loading(DataStore):
    """"""
    metadata = loadings
    validator = loading_validator
    dtype_fields = [
            ('geo', np.uint32),
            ('row', np.uint32),
    ]

    def add_mappings(self, data):
        """In theory, this shouldn't do anything, as all spatial units should be in defined by the method."""
        geomapping.add({obj[0] for obj in data})

    def process_data(self, row):
        return (
            geomapping[row[1]],
            MAX_INT_32,
            ), row[0]

    @property
    def filename(self):
        return super(Loading, self).filename + u".loading"
