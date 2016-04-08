# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from .errors import SiteGenericMethod, MissingSpatialSourceData
from .meta import geocollections, intersections, loadings, extension_tables
from .intersection import Intersection
from bw2data import Method, methods
import copy
import hashlib


def import_regionalized_cfs(geocollection, method, mapping, cf_field=None,
        overwrite=True):
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

    """
    try:
        from pandarus import Map
    except:
        raise ImportError("`pandarus` is required for this function")
    if not isinstance(method, Method):
        raise TypeError("Must pass bw2data Method instance (got %s: %s" % (type(method), method))
    assert geocollection in geocollections

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
                        flow,                                             # Biosphere flow
                        float(feature['properties'][field]),              # CF value
                        (geocollection, feature['properties'][id_field])  # Spatial unit
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
                        feature['value'],
                        # Spatial unit
                        (geocollection, feature['label'])
                    ))


            # if map_obj.vector:
            #     label =
            #     value =
            # else:
            #     label = feature['label']
            #     value = feature['value']

    method.write(data)

    if overwrite:
        methods[method.name]['geocollections'] = [geocollection]
        if cf_field:
            methods[method.name]['cf_field'] = cf_field
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


def sha256(filepath, blocksize=65536):
    """Generate SHA 256 hash for file at `filepath`"""
    hasher = hashlib.sha256()
    fo = open(filepath, 'rb')
    buf = fo.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fo.read(blocksize)
    return hasher.hexdigest()


def create_empty_intersection(name):
    """Shortcut to create Intersection object with no data"""
    inter = Intersection(name)
    inter.register()
    inter.write([])
    return inter


def convert_default_ecoinvent_locations(string):
    if len(string) == 2 or string == "GLO":
        return string
    else:
        return ("ecoinvent", string)


def reset_geo_meta():
    intersections.__init__()
    loadings.__init__()
    geocollections.__init__()
    topocollections.__init__()
    extension_tables.__init__()
