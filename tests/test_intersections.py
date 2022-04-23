import pytest
from bw2data import geomapping
from bw2data.tests import bw2test
from voluptuous import Invalid

from bw2regional.intersection import Intersection


@bw2test
def test_add_geomappings():
    inter = Intersection(("foo", "bar"))
    inter.register()
    assert ("foo", "bar") not in geomapping
    assert "baz" not in geomapping
    inter.write([[("foo", "bar"), "baz", 42]])
    assert ("foo", "bar") in geomapping
    assert "baz" in geomapping


@bw2test
def test_validation():
    inter = Intersection(("foo", "bar"))
    assert inter.validate([])
    assert inter.validate([[1, 2, 3]])
    assert inter.validate([["foo", "bar", 3.0]])
    with pytest.raises(Invalid):
        inter.validate(())
    with pytest.raises(Invalid):
        inter.validate([[1, 2]])
    with pytest.raises(Invalid):
        inter.validate([[1, 2, {"amount": 3.0}]])
