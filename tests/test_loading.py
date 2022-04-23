import hashlib

import pytest
from bw2data import geomapping
from bw2data.tests import bw2test
from voluptuous import Invalid

from bw2regional.loading import Loading


@bw2test
def test_add_geomappings():
    lg = Loading("some loadings")
    lg.register()
    assert ("foo", "bar") not in geomapping
    lg.write([[1, ("foo", "bar")]])
    assert ("foo", "bar") in geomapping


@bw2test
def test_validation():
    lg = Loading("some loadings")
    assert lg.validate([])
    assert lg.validate([[1, "f"]])
    assert lg.validate([[{"amount": 1}, "f"]])
    assert lg.validate([[1, ("f", "b")]])
    assert lg.validate([[{"amount": 1}, ("f", "b")]])
    with pytest.raises(Invalid):
        lg.validate(())
    with pytest.raises(Invalid):
        lg.validate([["f", 1]])


@bw2test
def test_filename():
    s = "some loading with a crazy name"
    r = (
        s.replace(" ", "-")
        + "."
        + hashlib.md5(s.encode("utf-8")).hexdigest()[:8]
        + ".loading"
    )
    lg = Loading("some loading with a crazy name")
    assert lg.filename == r


@bw2test
def test_allow_zero_loadings():
    lg = Loading("some loadings")
    assert lg.validate([[0.0, "f"]])
