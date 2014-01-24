# -*- coding: utf-8 -*
from .meta import loadings
from .validate import loading_validator
from bw2data import config, JsonWrapper, mapping, geomapping
from bw2data.errors import UnknownObject
from bw2data.method import Method
from bw2data.utils import MAX_INT_32
import bz2
import numpy as np
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle


class Loading(Method):
    """"""
    metadata = loadings
    validator = loading_validator
    dtype_fields = [
            ('geo', np.uint32),
            ('row', np.uint32),
    ]

    def add_mappings(self, data):
        geomapping.add({obj[0] for obj in data})

    def process_data(self, row):
        return (
            geomapping[row[1]],
            MAX_INT_32,
            ), row[0]

    @property
    def filename(self):
        return super(Loading, self).filename + u".loading"
