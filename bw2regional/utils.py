# -*- coding: utf-8 -*
from .errors import SiteGenericMethod, MissingSpatialSourceData
from .meta import geocollections, intersections, loadings, extension_tables
from .intersection import Intersection
from bw2data import Method, methods
import copy


def import_regionalized_cfs(geocollection, method, flow, cf_field=None,
        overwrite=True):
    try:
        from pandarus import Map
    except:
        raise ImportError("`pandarus` is required for this function")
    if not isinstance(method, Method):
        raise TypeError("Must pass bw2data Method instance (got %s: %s" % (type(method), method))
    assert geocollection in geocollections

    metadata = copy.copy(methods[method.name])
    metadata.update(**geocollections[geocollection])

    if overwrite:
        data = []
    else:
        data = method.load()

    map_obj = Map(**metadata)

    if map_obj.vector:
        cf_field = cf_field or methods[method.name].get('cf_field')
        if not cf_field:
            raise ValueError("Method must specify ``cf_field`` field name to retrieve CF values")
        id_field = geocollections[geocollection].get('field')
        if not id_field:
            raise ValueError("Geocollection must specify ``field`` field name for unique feature ids")

    for feature in map_obj:
        if map_obj.vector:
            label = feature['properties'][id_field]
            value = float(feature['properties'][cf_field])
        else:
            label = feature['label']
            value = feature['value']
        data.append((flow, value, (geocollection, label)))

    method.write(data)
    method.process()

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
        k:v for k, v in geocollection.iteritems()
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
    metadata = {k:v for k, v in metadata.iteritems() if v is not None}
    return Map(geocollection['filepath'], **metadata)


def create_empty_intersection(name):
    """Shortcut to create Intersection object with no data"""
    inter = Intersection(name)
    inter.register()
    inter.write([])
    inter.process()
    return inter

def reset_geo_meta():
    intersections.__init__()
    loadings.__init__()
    geocollections.__init__()
    extension_tables.__init__()
