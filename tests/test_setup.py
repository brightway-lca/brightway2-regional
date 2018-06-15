from bw2data.tests import bw2test
from bw2regional.base_data import *
import bw2regional
import json
import os
import pytest
import requests
import warnings


def nope(*args, **kwargs):
    return os.path.join(os.path.dirname(__file__), "data", "test_countries.gpkg")


@pytest.fixture
@bw2test
def no_download(monkeypatch):
    monkeypatch.setattr(bw2regional.base_data, 'download_file', nope)


@bw2test
def test_row_only():
    bw2regionalsetup('RoW')
    assert len(geocollections) == 1
    assert len(topocollections) == 1
    assert Topography('RoW').load()
    assert not geocollections['RoW']

def test_world_only(no_download):
    bw2regionalsetup('world')
    assert len(geocollections) == 1
    assert len(topocollections) == 1
    assert Topography('world').load()
    assert geocollections['world']['field'] == "isotwolettercode"

def test_ecoinvent_only(no_download):
    bw2regionalsetup('ecoinvent')
    assert len(geocollections) == 1
    assert len(topocollections) == 1
    assert Topography('ecoinvent').load()
    assert geocollections['ecoinvent']['field'] == 'shortname'

def test_all_basic_data(no_download):
    bw2regionalsetup('ecoinvent')
    bw2regionalsetup('world')
    bw2regionalsetup('RoW')
    assert len(geocollections) == 3
    assert len(topocollections) == 3


class Callable:
    def __init__(self, name):
        self.name = name
        self.called = False

    def __call__(self):
        self.called = True


@pytest.fixture
@bw2test
def fake_functions(monkeypatch):
    fake_world = Callable("world")
    fake_ei = Callable("ecoinvent")
    fake_row = Callable("RoW")
    monkeypatch.setattr(bw2regional.base_data, 'create_world', fake_world)
    monkeypatch.setattr(bw2regional.base_data, 'create_ecoinvent', fake_ei)
    monkeypatch.setattr(bw2regional.base_data, 'create_RoW', fake_row)
    return fake_world, fake_ei, fake_row


@bw2test
def test_regional_setup_error():
    with pytest.raises(ValueError):
        bw2regionalsetup('foo')

def test_regional_setup_default(fake_functions):
    for x in fake_functions:
        assert not x.called

    bw2regionalsetup()

    for x in fake_functions:
        assert x.called

def test_regional_setup_specific(fake_functions):
    bw2regionalsetup('ecoinvent')

    w, e, r = fake_functions
    assert not w.called
    assert not r.called
    assert e.called

def test_regional_setup_no_overwrite(fake_functions):
    geocollections['ecoinvent'] = {}

    bw2regionalsetup('ecoinvent')

    for x in fake_functions:
        assert not x.called

def test_regional_setup_overwrite(fake_functions):
    geocollections['ecoinvent'] = {}

    bw2regionalsetup('ecoinvent', overwrite=True)

    w, e, r = fake_functions
    assert not w.called
    assert not r.called
    assert e.called
