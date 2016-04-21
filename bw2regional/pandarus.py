# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

import os
from bw2data import JsonWrapper
from . import geocollections, topocollections, Topology


def merge(data, mapping):
    """Merge topo face ids to geocollection features.

    `data` has the form [(feature 1, feature 2, area)], where `feature 1` is a topo face id.

    `mapping` has the form `{geocollection feature: [face id]}`.

    Returns a new version of `data` where `feature 1` is now geocollection features intead of topo face ids.

    """
    merged = {}
    reverse_mapping = {}
    for k, v in mapping.items():
        for face_id in v:
            reverse_mapping[face_id] = reverse_mapping.get(face_id, []) + [k]

    for first, second, area in data:
        if first not in reverse_mapping:
            continue
        for feature in reverse_mapping[first]:
            merged[(feature, second)] = merged.get((feature, second), 0) + area

    return [(k[0], k[1], v) for k, v in merged.items()]


# def relabel(data, label):
#     return [((first, a), b, c) for a, b, c in data]


def import_from_pandarus(fp):
    """Load output file from Pandarus job.

    This function will:

    * Load pandarus output file
    * Locate the appropriate geo- or topocollection
    * Check to make sure that SHA256 hashes and other metadata match
    * If ``first`` is a topocollection, make sure the appropriate ``Topology`` exists, and squash the pandarus results to the linked geocollection(s).

    """
    assert os.path.isfile(fp)
    metadata, data = load_file(fp)
    is_area = len(metadata) == 1
    if is_area:
        return handle_area(metadata, data)
    else:
        return handle_intersection(metadata, data)


def handle_area(metadata, data):
    assert 'first' in metadata, "Invalid metadata in file"
    collections = get_possible_collections(metadata['first']['sha256'])
    # for data, kind in


def handle_intersection(metadata, data):
    # Check metadata
    assert 'first' in metadata and 'second' in metadata, "Invalid metadata in file"

    first_collections = get_possible_collections(metadata['first']['sha256'])
    second_collections = self.get_possible_collections(metadata['second']['sha256'])

    # No self-intersections
    assert not first_collections.intersection(second_collections), "Overlapping geocollections"

    # Either geo- or topocollection
    if len({x[1] for x in first_collections}) == 2:
        raise ValueError("Intersecting both geocollections and "
            "topocollections is not supported")
    if len({x[1] for x in second_collections}) == 2:
        raise ValueError("Intersecting both geocollections and "
            "topocollections is not supported")

    # Only one topocollection
    if {x[1] for x in second_collections} == \
        {x[1] for x in first_collections} == {'topocollection'}:
        raise ValueError("Intersections between a topography and "
            "another topography are not supported")


def load_file(fp):
    try:
        obj = JsonWrapper.load_bz2(filepath)
    except:
        obj = JsonWrapper.load(filepath)
    return obj['metadata'], obj['data']


def get_possible_collections(hash_value):
    possibles = {
        (name, 'geocollection')
        for name, value in geocollections
        if value.get('sha256') == hash_value
    }.union({
        (name, 'topocollection')
        for name, value in topocollections
        if value.get('sha256') == hash_value
        and not value['empty']
    })
    return possibles


def squash_topo_data_to_geocollection(data, topography):
    """Squash intersection data in ``data`` from topographical face ids to geocollection identifiers.

    Returns (geocollection name, modified data).

    Topography/geocollection intersection is guaranteed to be one to one.

    """
    geocollection = topocollections[topography]["geocollection"]
    topography_obj = Topography(topography)
    assert not topography_obj.metadata['empty'], "Empty topography can't be processed"
    mapping = topography_obj.load()
    return geocollection, merge(data, mapping)


# data = [((self.name[0], row[0]), (self.name[1], row[1]), row[2])
#     for row in data]

# with warnings.catch_warnings():
#     warnings.simplefilter("ignore")
#     self.write(data)
#     self.metadata['filepath'] =  filepath

# self.create_reversed_intersection()