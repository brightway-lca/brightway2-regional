# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

import os
from bw2data import JsonWrapper
from . import (
    geocollections,
    Intersection,
    intersections,
    topocollections,
    Topography,
)


def merge(data, mapping):
    """Merge topo face ids to geocollection features.

    `data` has the form [(feature 1, feature 2, area)], where `feature 1` is a topo face id.

    `mapping` has the form `{geocollection feature: [face id]}`.

    Returns a new version of `data` where `feature 1` is now geocollection features intead of topo face ids.

    """
    merged, reverse_mapping = {}, {}
    for k, v in mapping.items():
        for face_id in v:
            reverse_mapping[face_id] = reverse_mapping.get(face_id, []) + [k]

    for first, second, area in data:
        if first not in reverse_mapping:
            continue
        for feature in reverse_mapping[first]:
            merged[(feature, second)] = merged.get((feature, second), 0) + area

    return [(k[0], k[1], v) for k, v in merged.items()]


def relabel(data, first, second):
    """Add geocollection names to geo identifiers"""
    return [((first, a), (second, b), c) for a, b, c in data]


def switch_order(data):
    """Switch data order from ``(first, second, area)`` to ``(second, first, area)``."""
    return [(y, x, z) for x, y, z in data]


def load_file(filepath):
    """Load Pandarus JSON output file.

    Returns metadata and calculation results."""
    try:
        obj = JsonWrapper.load_bz2(filepath)
    except:
        obj = JsonWrapper.load(filepath)
    return obj['metadata'], obj['data']


def get_possible_collections(hash_value):
    """Return all geo- and topocollections for a file hash.

    Returns list of (collection name, collection type) tuples."""
    possibles = {
        (name, 'geocollection')
        for name, value in geocollections.items()
        if value.get('sha256') == hash_value
    }.union({
        (name, 'topocollection')
        for name, value in topocollections.items()
        if value.get('sha256') == hash_value
        and not value['empty']
    })
    return possibles


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
        return handle_area(metadata, data, fp)
    else:
        return handle_intersection(metadata, data, fp)


def handle_area(metadata, data, fp):
    assert 'first' in metadata, "Invalid metadata in file"
    collections = get_possible_collections(metadata['first']['sha256'])
    # for data, kind in


def handle_intersection(metadata, data, fp):
    # Check metadata
    assert 'first' in metadata and 'second' in metadata, "Invalid metadata in file"

    first_collections = get_possible_collections(metadata['first']['sha256'])
    second_collections = get_possible_collections(metadata['second']['sha256'])

    # No self-intersections
    assert not first_collections.intersection(second_collections), "Overlapping geocollections"

    if len({x[1] for x in second_collections}.union({x[1] for x in first_collections})) == 2:
        return handle_topographical_intersection(metadata, data,
            first_collections, second_collections, fp)

    # Only one geocollection in borth `first` and `second`
    assert len(first_collections) == 1, "Must intersect with exactly one geocollection"
    assert len(second_collections) == 1, "Must intersect with exactly one geocollection"
    first = list(first_collections)[0][0]
    second = list(second_collections)[0][0]

    assert (first, second) not in intersections, \
        "Intersection between {} and {} already exists".format(first, second)

    dataset = relabel(data, first, second)
    intersection = Intersection((first, second))
    intersection.register(filepath=fp)
    intersection.write(dataset)
    intersection.create_reversed_intersection()

    return first, second


def handle_topographical_intersection(metadata, data, first_collections, second_collections, filepath):
    """Handle an intersection between one or more topographies and a single geocollection.

    Each topography is associated with exactly one geocollection.

    Each topography is not empty, i.e. we can use the topographical definitions to filter.

    The procedure is:
    #. Check metadata validity, and make sure the topography ids are in the first column
    #. To split data into each topography
    #. Squash the topography to geocollections
    #. Create a new intersection for each geocollection/topography pair
    """
    # Check that topography(s) are in either first or second position, and
    # switch to first position if necessary
    first_labels = {x[1] for x in first_collections}
    second_labels = {x[1] for x in second_collections}
    if first_labels == {'topocollection'}:
        assert len(second_collections) == 1, "Must intersect with exactly one geocollection"
        assert second_labels == {'geocollection'}, "Must intersect topography with geocollections"
    elif second_labels == {'topocollections'}:
        assert len(first_collections) == 1, "Must intersect with exactly one geocollection"
        assert first_labels == {'geocollection'}, "Must intersect topography with geocollections"
        data = switch_order(data)
        metadata['first'], metadata['second'] = metadata['second'], metadata['first']
        first_collections, second_collections = second_collections, first_collections
    else:
        raise ValueError("Intersections between mixed topocollections and "
            "geocollections are not supported")

    topo_data = [Topography(name).load() for name, kind in first_collections]
    topo_geocollections = [
        topocollections[name]['geocollection']
        for name, kind in first_collections
    ]
    other_geocollection = list(second_collections)[0][0]

    for name in topo_geocollections:
        assert (other_geocollection, name) not in intersections, (
            "Intersection between {} and {} already exists".format(
            other_geocollection, name)
        )

    # Split data into topography-specific sections
    included_labels = [
        {face for faces in topo_dataset.values() for face in faces}
        for topo_dataset in topo_data
    ]
    data = [
        [(x, y, z) for x, y, z in data if x in labels]
        for labels in included_labels
    ]

    # Squash topographies to geocollections
    data = [
        merge(dataset, mapping)
        for dataset, mapping in zip(data, topo_data)
    ]

    for name, dataset in zip(topo_geocollections, data):
        dataset = relabel(dataset, name, other_geocollection)
        intersection = Intersection((name, other_geocollection))
        intersection.register(filepath=filepath)
        intersection.write(dataset)
        intersection.create_reversed_intersection()

    return [(n, other_geocollection) for n in topo_geocollections]
