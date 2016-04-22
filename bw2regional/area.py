# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from .meta import areas
from .validate import area_validator
from bw2data import geomapping
from bw2data.utils import MAX_INT_32, numpy_string
import numpy as np
from bw2data.data_store import ProcessedDataStore


class Area(ProcessedDataStore):
    """"""
    _metadata = areas
    dtype_fields = [
            (numpy_string('geo'), np.uint32),
            (numpy_string('row'), np.uint32),
            (numpy_string('col'), np.uint32),
    ]

    def add_mappings(self, data):
        """Add all geographic units in both geocollections to ``geomapping``, the master location list.

        Called automatically when data is written."""
        geomapping.add({x[0] for x in data})

    def process_data(self, row):
        return (
            geomapping[row[0]],
            MAX_INT_32,
            ), row[1]
