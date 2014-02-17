# -*- coding: utf-8 -*
from .errors import SiteGenericMethod, MissingSpatialSourceData
from .meta import geocollections
from bw2data import Method, methods
import copy


def import_regionalized_cfs(geocollection, method, flow):
    try:
        from pandarus import Map
    except:
        raise ImportError("`pandarus` is required for this function")
    metadata = copy.copy(methods[method.name])
    metadata.update(**geocollections[geocollection])
    assert geocollection in geocollections
    if not isinstance(method, Method):
        raise TypeError("Must pass bw2data Method instance (got %s: %s" % (type(method), method))

    data = []
    map_obj = Map(**metadata)

    if map_obj.vector:
        assert False
        # TODO: For vector files
        # mapping = map_obj.get_fieldnames_dictionary()
    for feature in map_obj:
        label = feature['label']
        value = feature['value']
        data.append((flow, value, (geocollection, label)))

    method.write(data)
    method.process()

    methods[method.name]['geocollections'] = [geocollection]
    methods.flush()


def get_pandarus_map(method, geocollection=None):
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
        'field': method_data.get('fieldname') or geocollection.get('field'),
        'vfs': geocollection.get('vfs'),
        'encoding': geocollection.get('encoding'),
    }
    metadata = {k:v for k, v in metadata.iteritems() if v is not None}
    return Map(geocollection['filepath'], **metadata)
