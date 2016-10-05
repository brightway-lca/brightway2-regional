# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from .meta import loadings
from .validate import loading_validator
from .utils import get_pandarus_map
from bw2data import geomapping, config
from bw2data.data_store import ProcessedDataStore
from bw2data.utils import MAX_INT_32, numpy_string
import numpy as np
import os


class Loading(ProcessedDataStore):
    """"""
    _metadata = loadings
    validator = loading_validator
    dtype_fields = [
            (numpy_string('geo'), np.uint32),
            (numpy_string('row'), np.uint32),
    ]

    def add_mappings(self, data):
        """In theory, this shouldn't do anything, as all spatial units should be in defined by the method."""
        geomapping.add({obj[1] for obj in data})

    def process_data(self, row):
        return (
            geomapping[row[1]],
            MAX_INT_32,
            ), row[0]

    @property
    def filename(self):
        return super(Loading, self).filename + u".loading"

    def write_to_map(self, method, flow, geocollection=None):
        map_obj = get_pandarus_map(method, geocollection)
        data = {x[1][1]: x[0] for x in self.load()}
        if map_obj.raster:
            self._write_raster_loadings_to_map(map_obj, data)
        else:
            self._write_vector_loadings_to_map(map_obj, data)

    def _write_raster_loadings_to_map(self, map_obj, data):
        NODATA = -9999.
        filepath = os.path.join(
            projects.output_dir,
            self.filename + ".tiff"
        )

        array = np.zeros(map_obj.file.array().shape) + NODATA
        for obj in map_obj:
            if obj['label'] in data:
                array[obj['row'], obj['col']] = data[obj['label']]

        map_obj.file.write_modified_array(filepath, array, nodata=NODATA)
        return filepath

    def _write_vector_loadings_to_map(self, map_obj, data):
        raise NotImplementedError


