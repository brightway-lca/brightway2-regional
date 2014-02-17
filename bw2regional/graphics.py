# -*- coding: utf-8 -*
from __future__ import division
from .utils import get_pandarus_map
from bw2data import config
import numpy as np
import os
import warnings
try:
    from pandarus import Map
except ImportError:
    Map = None


class RegionalizedGrapher(object):
    NODATA = -9999.

    def __init__(self, method, geocollection, spatial_dict, result_matrix, normalize=False, log_transform=False):
        if Map is None:
            raise ImportError("pandarus required for this function")
        assert result_matrix.shape[0] == 1, "Result matrix must only have one row"
        self.method = method
        self.spatial_dict = spatial_dict
        self.map = get_pandarus_map(method, geocollection)
        self.matrix = self.transform_data(result_matrix, normalize, log_transform)
        self.results = self.matrix_to_dict(self.matrix, spatial_dict)

    def transform_data(self, matrix, normalize, log_transform):
        matrix = matrix.tocsr()
        matrix.eliminate_zeros()  # Not available for COO sparse matrices
        matrix = matrix.tocoo()
        if (matrix.data < 0).sum() and log_transform:
            warnings.warn("Can't log-transform data with negative values")
        elif log_transform:
            matrix.data = np.log(matrix.data)
        if normalize:
            matrix.data = (matrix.data - matrix.min()) / (matrix.max() - matrix.min())
        return matrix

    def matrix_to_dict(self, matrix, spatial_dict):
        rev_ia = {v: k for k, v in spatial_dict.iteritems()}
        return {rev_ia[col][1]: val for col, val in zip(matrix.col, matrix.data)}

    def write(self, filename):
        filepath = os.path.join(config.request_dir(u"output"), filename)
        if self.map.raster:
            return self.write_raster(filepath)
        else:
            return self.write_vector(filepath)

    def write_raster(self, filepath):
        filepath = filepath + u".tiff"

        array = np.zeros(self.map.file.array().shape) + self.NODATA
        for obj in self.map:
            if obj['label'] in self.results:
                array[obj['row'], obj['col']] = self.results[obj['label']]

        self.map.file.write_modified_array(
            filepath,
            array,
            nodata=self.NODATA
        )
        return filepath

    def write_vector(self, filename):
        raise NotImplementedError
