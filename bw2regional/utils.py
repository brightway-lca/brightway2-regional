# -*- coding: utf-8 -*
from bw2data import Method, methods
from .meta import geocollections
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
