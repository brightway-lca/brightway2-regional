from brightway2 import config, geomapping, Method, Database
from bw2data.utils import download_file
from bw2regional import *
from sys import stderr
import json
import os
import pytest
import requests
import sys
import warnings


def test_one_arg_no_kwarg(capsys):
    captured = capsys.readouterr()
    bw2regionalsetup('rows')
    # todo: test on RoWs will need to be adapted once base_data is complete
    # assert captured.out == "Adding RoW topology"
    bw2regionalsetup('world')
    assert captured.out == "Adding world topology"
    assert geocollections['world'] is not None
    assert topocollections['world'] is not None
    assert Topography('world') is not None
    bw2regionalsetup('ecoinvent')
    assert captured.out == "Adding ecoinvent-specific topology"
    assert geocollections['ecoinvent'] is not None
    assert topocollections['world'] is not None
    assert Topography('world') is not None


def test_one_arg_geocollections_exist_overwrite_true(capsys):
    # 4 cases to study whether the geocollections already exist or not and whether overwrite is True or False
    # Case 1: Geocollections already exist and overwrite=True
    bw2regionalsetup('rows')
    bw2regionalsetup('world')
    bw2regionalsetup('ecoinvent')
    captured = capsys.readouterr()
    bw2regionalsetup('rows', overwrite=True)
    assert captured.out == "Adding RoW topology"
    bw2regionalsetup('world', overwrite=True)
    assert captured.out == "Adding world topology"
    bw2regionalsetup('ecoinvent', overwrite=True)
    assert captured.out == "Adding ecoinvent-specific topology"


def test_one_arg_geocollections_exist_overwrite_false(capsys):
    # Case 2: Geocollections already exist and overwrite=False
    captured = capsys.readouterr()
    bw2regionalsetup('rows', overwrite=False)
    assert captured.out is None
    bw2regionalsetup('world', overwrite=False)
    assert captured.out is None
    bw2regionalsetup('ecoinvent', overwrite=False)
    assert captured.out is None


def test_one_arg_no_geocollection_overwrite_true(capsys):
    # Case 3: Geocollections don't exist and overwrite = True
    del geocollections['RoWs']
    del geocollections['world']
    del geocollections['ecoinvent']
    captured = capsys.readouterr()
    bw2regionalsetup('rows', overwrite=True)
    assert captured.out == "Adding RoW topology"
    bw2regionalsetup('world', overwrite=True)
    assert captured.out == "Adding world topology"
    bw2regionalsetup('ecoinvent', overwrite=True)
    assert captured.out == "Adding ecoinvent-specific topology"


def test_one_arg_no_geocollection_overwrite_false(capsys):
    # Case 4: Geocollections don't exist and overwrite = False
    del geocollections['RoWs']
    del geocollections['world']
    del geocollections['ecoinvent']
    captured = capsys.readouterr()
    bw2regionalsetup('rows', overwrite=False)
    assert captured.out == "Adding RoW topology"
    bw2regionalsetup('world', overwrite=False)
    assert captured.out == "Adding world topology"
    bw2regionalsetup('ecoinvent', overwrite=False)
    assert captured.out == "Adding ecoinvent-specific topology"

