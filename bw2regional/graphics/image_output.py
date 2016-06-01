from . import viridis
from .. import geocollections
from ..errors import MissingSpatialSourceData
from .utils import normalize_array
from descartes import PolygonPatch
from PIL import Image
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry import shape
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
        return display_raster(name)
    else:
        return display_vector(name, field)


def display_vector(name, field=None):
    metadata = geocollections[name]
    field = field or metadata['field']
    figure = plt.figure(figsize=(10, 8))
    axis = plt.axes([0,0,1,1], frameon=False)
    axis.set_axis_off()

    with fiona.drivers():
        with fiona.open(metadata['filepath']) as source:
            data = normalize_array(np.array([feat['properties'][field] for feat in source]))
            for feat, value in zip(source, data):
                add_geom(shape(feat['geometry']), axis, viridis(value))

    plt.axis('scaled')
    return figure


def add_geom(geom, axis, color):
    if isinstance(geom, MultiPolygon):
        for poly in geom:
            add_geom(poly, axis, color)
    else:
        patch = PolygonPatch(geom, fc=color, ec=color, lw=0)
        axis.add_patch(patch)


def display_raster(name):
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
