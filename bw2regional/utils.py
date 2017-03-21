# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from .errors import SiteGenericMethod, MissingSpatialSourceData
from .hashing import sha256
from .intersection import Intersection
from .meta import (
    extension_tables,
    geocollections,
    intersections,
    loadings,
    restofworlds,
    topocollections,
)
from bw2data import Method, methods, projects
from scipy import sparse
import copy
import fiona
import numpy as np
import os
import rasterio
import shutil


def import_regionalized_cfs(geocollection, method, mapping, overwrite=True,
                            global_cfs=None, scaling_factor=1):
    """Import data from a geospatial dataset (i.e. raster or vector data) into a ``Method``.

    A ``Method`` can have both site-generic and regionalized characterization factors.

    The ``mapping`` defines which field (vector) or band (raster) maps to which biosphere flows. Some geocollections may only define regionalized chracterization factors for a single biosphere flow, but it is much more common to have each field or band map to multiple biosphere flows. Therefore, mapping should be defined as:

    .. code-block:: python

        {
            field name (str) or raster band (int): [list of biosphere flows (tuples)]
        }

    Args:
        * *geocollection*: A ``geocollection`` name.
        * *method*: A ``Method`` instance (not the identifying tuple).
        * *mapping*: Mapping from fields or bands to biosphere flows. See above.
        * *overwrite*: Boolean. Overwrite existing characterization factors. Default is ``True``. Set to ``False`` if ``method`` already has site-generic characterization factors.
        * *global_cfs*: An optional list of CFs to add when writing the method.
        * *scaling_factor*: Optional. Rescale the values in the spatial data source.

    """
    try:
        from pandarus import Map
    except:
        raise ImportError("`pandarus` is required for this function")
    if not isinstance(method, Method):
        raise TypeError("Must pass bw2data Method instance (got %s: %s" % (type(method), method))
    assert geocollection in geocollections

    if global_cfs is None:
        global_cfs = []

    metadata = copy.deepcopy(method.metadata)
    metadata.update(geocollections[geocollection])

    if overwrite:
        data = []
    else:
        data = method.load()

    map_obj = Map(**metadata)

    if map_obj.vector:
        id_field = geocollections[geocollection].get('field')
        if not id_field:
            raise ValueError("Geocollection must specify ``field`` field name for unique feature ids")

        for feature in map_obj:
            for field in mapping:
                for flow in mapping[field]:
                    data.append((
                        flow,                                                 # Biosphere flow
                        float(feature['properties'][field]) * scaling_factor, # CF value
                        (geocollection, feature['properties'][id_field])      # Spatial unit
                    ))

    else:
        # TODO: Does this respect raster band in mapping?
        for feature in map_obj:
            for band_index in mapping:
                for flow in mapping[band_index]:
                    data.append((
                        # Biosphere flow
                        flow,
                        # CF value
                        feature['value'] * scaling_factor,
                        # Spatial unit
                        (geocollection, feature['label'])
                    ))

    method.write(data + global_cfs)

    if overwrite:
        methods[method.name]['geocollections'] = [geocollection]
        methods.flush()


def get_pandarus_map(geocollection):
    try:
        from pandarus import Map
    except:
        raise ImportError("`pandarus` is required for this function")
    if geocollection not in geocollections:
        raise ValueError("Geocollection %s not registered" % geocollection)
    geocollection = geocollections[geocollection]
    if not geocollection.get(u'filepath'):
        raise MissingSpatialSourceData("No filepath given for geocollection")
    metadata = {
        k:v for k, v in geocollection.items()
        if v is not None
        and k != u'filepath'
    }
    return Map(geocollection['filepath'], **metadata)


def get_pandarus_map_for_method(method, geocollection=None):
    try:
        from pandarus import Map
    except:
        raise ImportError("`pandarus` is required for this function")
    if not methods[method].get('geocollections', []):
        raise SiteGenericMethod
    elif len(methods[method]['geocollections']) > 1 and geocollection is None:
        raise ValueError("Must specify geocollection for this LCIA method")
    assert method in methods, "Unknown LCIA method"
    method_data = methods[method]
    geocollection = geocollections[
        geocollection or methods[method]['geocollections'][0]
    ]
    if not geocollection.get('filepath'):
        raise MissingSpatialSourceData("No filepath given for geocollection")
    metadata = {
        'band': method_data.get('band'),
        'layer': geocollection.get('layer'),
        'field': geocollection.get('field'),
        'vfs': geocollection.get('vfs'),
        'encoding': geocollection.get('encoding'),
    }
    metadata = {k:v for k, v in metadata.items() if v is not None}
    return Map(geocollection['filepath'], **metadata)


def hash_collection(name):
    """Return SHA256 hash for a topo- or geocollection.

    Prefers topocollection if available.
    """
    if name in topocollections:
        if 'sha256' in topocollections[name]:
            return topocollections[name]['sha256']
        try:
            assert os.path.isfile(topocollections[name]['filepath'])
            return sha256(topocollections[name]['filepath'])
        except KeyError:
            pass
    if name in geocollections:
        if 'sha256' in geocollections[name]:
            return geocollections[name]['sha256']
        try:
            assert os.path.isfile(geocollections[name]['filepath'])
            return sha256(geocollections[name]['filepath'])
        except KeyError:
            pass
    return False


def create_empty_intersection(name):
    """Shortcut to create Intersection object with no data"""
    inter = Intersection(name)
    inter.register()
    inter.write([])
    return inter


def get_spatial_dataset_kind(filepath):
    """Get kind of spatial dataset at `filepath`.

    Returns one of "vector", "raster", None.

    """
    with fiona.drivers():
        try:
            with fiona.open(filepath) as source:
                assert source.meta
                return "vector"
        except:
            pass
    with rasterio.drivers():
        try:
            with rasterio.open(filepath) as source:
                assert source.meta
                return "raster"
        except:
            pass
    return None


def reset_all_geo():
    """Reset all bw2regional data and metadata"""
    all_meta = (
        extension_tables,
        geocollections,
        intersections,
        loadings,
        restofworlds,
        topocollections,
    )
    shutil.rmtree(projects.request_directory("regional"))
    projects.request_directory("regional")
    for meta in all_meta:
        meta.data = {}
        meta.flush()


def reset_geo_meta():
    intersections.__init__()
    loadings.__init__()
    restofworlds.__init__()
    geocollections.__init__()
    topocollections.__init__()
    extension_tables.__init__()


def filter_rows(matrix, row_indices, exclude=True):
    """Filter a sparse matrix, either excluding or taking only the rows in ``row_indices``.

    * ``matrix``: A Scipy sparse matrix.
    * ``row_indices``: An iterable of integer row indices
    * ``exclude``: Boolean. If true, exclude rows in ``row_indices``. Otherwise, include only rows in ``row_indices``.

    Returns a sparse matrix.
    """
    matrix = matrix.tocoo()
    indices = np.array(row_indices)
    row_mask = np.in1d(matrix.row, indices, invert=exclude)
    return sparse.coo_matrix((
            matrix.data[row_mask],
            (matrix.row[row_mask], matrix.col[row_mask])
        ), matrix.shape).tocsr()


def filter_columns(matrix, col_indices, exclude=True):
    """Filter a sparse matrix, either excluding or taking only the columns in ``col_indices``.

    * ``matrix``: A Scipy sparse matrix.
    * ``col_indices``: An iterable of integer column indices
    * ``exclude``: Boolean. If true, exclude rows in ``row_indices``. Otherwise, include only rows in ``row_indices``.

    Returns a sparse matrix.
    """
    matrix = matrix.tocoo()
    indices = np.array(col_indices)
    col_mask = np.in1d(matrix.col, indices, invert=exclude)
    return sparse.coo_matrix((
            matrix.data[col_mask],
            (matrix.row[col_mask], matrix.col[col_mask])
        ), matrix.shape).tocsr()
