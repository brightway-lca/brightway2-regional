# -*- coding: utf-8 -*
from bw2data.validate import valid_tuple, maybe_uncertainty
from voluptuous import Any, Schema, Invalid

_maybe_uncertainty = Schema(maybe_uncertainty)
_loading_value = Schema(Any(basestring, valid_tuple))


def uncertainty_list(obj):
    try:
        assert len(obj) == 2
        assert isinstance(obj, list)
        _maybe_uncertainty(obj[0])
        _loading_value(obj[1])
    except:
        raise Invalid(u"%s is not a valid loading value" % obj)
    return obj


def float_as_last(obj):
    print obj
    try:
        assert isinstance(obj, list)
        assert len(obj) == 3
        assert isinstance(obj[2], (float, int))
    except:
        raise Invalid(u"%s is not a valid intersection value" % obj)
    return obj


loading_validator = Schema([uncertainty_list])

intersection_validator = Schema([float_as_last])
