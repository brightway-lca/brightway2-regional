from . import viridis
from .. import geocollections
from ..errors import MissingSpatialSourceData, IncompleteSpatialDefinition
from .utils import normalize_array
from descartes import PolygonPatch
from pandarus import Map
from PIL import Image
from shapely.geometry import shape
from shapely.geometry.multipolygon import MultiPolygon
import fiona
import matplotlib.pyplot as plt
import numpy as np
import pyprind
import rasterio


def display_geocollection(name, field=None):
    assert name in geocollections
    if 'filepath' not in geocollections[name]:
        raise MissingSpatialSourceData("Geocollection {} has no associated source data".format(name))

    if geocollections[name]['kind'] == 'raster':
        return display_geocollection_raster(name)
    else:
        filepath = geocollections[name]['filepath']
        field = field or geocollections[name].get('field')
        if not field:
            raise IncompleteSpatialDefinition(
                "Geocollection {} metadata missing `field`".format(name)
            )
        values = normalize_array(get_vector_values(filepath, field))
        return display_vector_and_values(filepath, field)


def get_vector_values(filepath, field):
    with fiona.drivers():
        with fiona.open(filepath) as source:
            data = np.array([feat['properties'][field] for feat in source])
    return data


def setup_vector_figure(figsize=(10, 8)):
    figure = plt.figure(figsize=figsize)
    axis = plt.axes([0,0,1,1], frameon=False)
    axis.set_axis_off()
    return figure, axis


def display_vector_and_values(filepath, values, field=None):
    figure, axis = setup_vector_figure()

    with fiona.drivers():
        with fiona.open(filepath) as source:
            for feat, value in zip(source, values):
                add_geom_to_axis(shape(feat['geometry']), axis, viridis(value))

    plt.axis('scaled')
    return figure


def add_geom_to_axis(geom, axis, color):
    if isinstance(geom, MultiPolygon):
        for poly in geom:
            add_geom_to_axis(poly, axis, color)
    else:
        patch = PolygonPatch(geom, fc=color, ec=color, lw=0)
        axis.add_patch(patch)


def display_geocollection_raster(name):
    # Some code from
    # http://stackoverflow.com/questions/10965417/how-to-convert-numpy-array-to-pil-image-applying-matplotlib-colormap
    metadata = geocollections[name]
    # Adjust band index from GDAL (1-indexed) to Python (0-indexed)
    band = metadata.get('band', 1) - 1
    with rasterio.open(metadata['filepath']) as source:
        nodata = source.profile.get('nodata', None)
        array = source.read()[band]
    array = normalize_array(array, nodata)
    if nodata is not None:
        array = np.ma.masked_array(array, array == nodata)
    return Image.fromarray(viridis(array, bytes=True))


def display_result(matrix, spatial_dict, geocollection):
    """Display results from a regionalized LCA calculation.

    ``matrix`` is a Scipy sparse matrix with shape ``(1, len(spatial_dict))``.

    ``spatial_dict`` has the form ``{feature label: row index}``.

    ``geocollection`` is the name of a valid geocollection.

    Returns a matplotlib (vector) or pillow (raster) object.

    """
    if geocollections[geocollection]['kind'] == 'raster':
        return display_raster_result(matrix, spatial_dict, geocollection)
    else:
        return display_vector_result(matrix, spatial_dict, geocollection)


def eliminate_zeros(matrix):
    matrix = matrix.tocsr()
    matrix.eliminate_zeros()
    return matrix


def display_vector_result(matrix, spatial_dict, name):
    field = geocollections[name].get('field')
    filepath = geocollections[name]['filepath']
    if not field:
        raise IncompleteSpatialDefinition(
            "Geocollection {} metadata missing `field`".format(name)
        )

    matrix = eliminate_zeros(matrix)
    matrix.data = normalize_array(matrix.data)
    figure, axis = setup_vector_figure()

    with fiona.drivers():
        with fiona.open(filepath) as source:
            for feat in source:
                label = feat['properties'][field]
                if (name, label) in spatial_dict:
                    col = spatial_dict[(name, label)]
                elif label in spatial_dict:
                    col = spatial_dict[label]
                else:
                    continue
                if matrix[0, col] == 0:
                    continue
                add_geom_to_axis(shape(feat['geometry']), axis, viridis(matrix[0, col]))

    plt.axis('scaled')
    return figure


def crop(array):
    nonzero_cols = np.nonzero(array.sum(axis=0))[0]
    nonzero_cols.sort()
    nonzero_rows = np.nonzero(array.sum(axis=1))[0]
    nonzero_rows.sort()
    return array[nonzero_rows[0]:nonzero_rows[-1] + 1, nonzero_cols[0]:nonzero_cols[-1] + 1]


def display_raster_result(matrix, spatial_dict, name):
    map_obj = Map(geocollections[name]['filepath'],
               band=geocollections[name].get('band', 1))
    matrix = eliminate_zeros(matrix)
    matrix.data = normalize_array(matrix.data)
    array = np.zeros(map_obj.file.array().shape)
    for obj in map_obj:
        if obj['label'] in spatial_dict:
            array[obj['row'], obj['col']] = matrix[0, spatial_dict[0, obj['label']]]
        elif (name, obj['label']) in spatial_dict:
            array[obj['row'], obj['col']] = matrix[0, spatial_dict[(name, obj['label'])]]

    array = crop(array)
    array = np.ma.masked_array(array, array == 0)
    return Image.fromarray(viridis(array, bytes=True))
