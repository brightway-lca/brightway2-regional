from . import viridis
from .. import geocollections
from ..errors import MissingSpatialSourceData
from .utils import normalize_array
from descartes import PolygonPatch
from PIL import Image
import fiona
import numpy as np
import rasterio


def display_geocollection(name):
    assert name in geocollections
    if 'filepath' not in geocollections[name]:
        raise MissingSpatialSourceData("Geocollection {} has no associated source data".format(name))
    if geocollections[name]['kind'] == 'raster':
        return display_raster(name)
    else:
        return display_vector(name)


def display_vector(name):
    metadata = geocollections[name]
    field = metadata['field']

    with fiona.drivers():
        with fiona.open(metadata['filepath']) as source:
            data = normalize_array(np.array([feat['properties'][field] for feat in source]))

            for feat in source:
                print(feat['geometry'])
                break


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
