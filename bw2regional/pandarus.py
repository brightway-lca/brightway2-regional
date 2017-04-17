# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from . import (
    geocollections,
    Intersection,
    intersections,
    topocollections,
    Topography,
    ExtensionTable,
)
from bw2data import JsonWrapper, geomapping, projects
from bw2data.utils import MAX_INT_32, numpy_string
import numpy as np
import os
import pandas as pd
import pprint
import pyprind
import pickle


def relabel(data, first, second):
    """Add geocollection names to geo identifiers"""
    return [((first, a), (second, b), c) for a, b, c in data]


def load_file(filepath):
    """Load Pandarus JSON output file.

    Returns metadata and calculation results."""
    try:
        obj = JsonWrapper.load_bz2(filepath)
    except:
        obj = JsonWrapper.load(filepath)
    return obj['metadata'], obj['data']


def get_possible_collections(kwargs):
    """Return all geo- and topocollections for a file hash.

    Returns list of (collection name, collection type) tuples."""
    candidates = {'sha256', 'field', 'layer', 'band'}
    filters = {
        k: v
        for k, v in kwargs.items()
        if k in candidates
        and kwargs[k]
    }

    def match(other):
        return all(other.get(key) == filters[key] for key in filters)

    possibles = {
        (name, 'geocollection')
        for name, value in geocollections.items()
        if match(value)
    }.union({
        (name, 'topocollection')
        for name, value in topocollections.items()
        if match(value)
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

    # Check metadata
    assert 'first' in metadata and 'second' in metadata, "Invalid metadata in file"

    first_collections = get_possible_collections(metadata['first'])
    second_collections = get_possible_collections(metadata['second'])

    # No self-intersections
    assert not first_collections.intersection(second_collections), "Overlapping geocollections"

    if 'topocollection' in {x[1] for x in second_collections}.union(
            {x[1] for x in first_collections}):
        return handle_topographical_intersection(metadata, data,
            first_collections, second_collections, fp)

    # Only one geocollection in both `first` and `second`
    assert len(first_collections) == 1, "Must intersect with exactly one geocollection"
    assert len(second_collections) == 1, "Must intersect with exactly one geocollection"
    first = first_collections.pop()[0]
    second = second_collections.pop()[0]

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

    We use Pandas DataFrames to do aggregation in a resource efficient way. We also write the processed Intersection arrays directly.

    """
    # Check that topography(s) are in either first or second position, and
    # switch to first position if necessary
    first_labels = {x[1] for x in first_collections}
    second_labels = {x[1] for x in second_collections}
    if first_labels == {'topocollection'}:
        assert len(second_collections) == 1, "Must intersect with exactly one geocollection"
        assert second_labels == {'geocollection'}, "Must intersect topography with geocollections"
        lbl = list(second_collections)[0][0]
        geomapping.add({(lbl, y) for x, y, z in data})
        data = pd.DataFrame(
            [(x, geomapping[(lbl, y)], z) for x, y, z in data],
            columns=['topo_id', 'feature_mapped_id', 'area']
        )
    elif second_labels == {'topocollection'}:
        assert len(first_collections) == 1, "Must intersect with exactly one geocollection"
        assert first_labels == {'geocollection'}, "Must intersect topography with geocollections"
        lbl = list(first_collections)[0][0]
        geomapping.add({(lbl, x) for x, y, z in data})
        data = pd.DataFrame(
            [(y, geomapping[(lbl, x)], z) for x, y, z in data],
            columns=['topo_id', 'feature_mapped_id', 'area']
        )
        metadata['first'], metadata['second'] = metadata['second'], metadata['first']
        first_collections, second_collections = second_collections, first_collections
    else:
        raise ValueError("Intersections between mixed topocollections and "
            "geocollections are not supported")

    grouped_data = data.groupby(['topo_id'])
    topo_geocollections = [
        topocollections[name]['geocollection']
        for name, kind in first_collections
    ]
    topo_data = [{geomapping[k]: set(v)
                 for k, v in Topography(obj[0]).load().items()
                 } for obj, name in zip(first_collections, topo_geocollections)]
    other_geocollection = second_collections.pop()[0]

    for name in topo_geocollections:
        assert (other_geocollection, name) not in intersections, (
            "Intersection between {} and {} already exists".format(
            other_geocollection, name)
        )

    dtype = [
        (numpy_string('geo_inv'), np.uint32),
        (numpy_string('geo_ia'), np.uint32),
        (numpy_string('amount'), float),
        (numpy_string('row'), np.uint32),
        (numpy_string('col'), np.uint32),
    ]

    for name, mapping in zip(topo_geocollections, topo_data):
        print("Merging topographical faces for geocollection {}".format(name))
        arrays = []
        valid_topo_ids = data['topo_id'].unique()

        for key in pyprind.prog_bar(mapping):
            try:
                # Get list of dataframes, one per face id, all
                # from a given region
                all_intersections_for_a_region = [
                    grouped_data.get_group(topo_id)
                    for topo_id in mapping[key]
                    if topo_id in valid_topo_ids
                ]
            except KeyError:
                continue

            if not all_intersections_for_a_region:
                continue

            temp = pd.concat(all_intersections_for_a_region).groupby('feature_mapped_id').sum()
            array = np.empty(len(temp), dtype=dtype)
            array['geo_inv'] = key
            array['geo_ia'] = temp.index.values
            array['amount'] = temp['area'].values
            arrays.append(array)

        assert arrays, "Empty intersection"

        arrays = np.hstack(arrays)
        arrays['row'] = MAX_INT_32
        arrays['col'] = MAX_INT_32

        print("Creating intersection ({}, {})".format(name, other_geocollection))
        intersection = Intersection((name, other_geocollection))
        intersection.register(filepath=filepath)
        filepath = os.path.join(
            projects.dir,
            "processed",
            intersection.filename + ".npy"
        )
        with open(filepath, "wb") as f:
            pickle.dump(arrays, f, protocol=pickle.HIGHEST_PROTOCOL)

        intersection = Intersection((other_geocollection, name))
        intersection.register(filepath=filepath)
        arrays.dtype.names = (
            numpy_string('geo_inv'),
            numpy_string('geo_ia'),
            numpy_string('amount'),
            numpy_string('row'),
            numpy_string('col'),
        )
        filepath = os.path.join(
            projects.dir,
            "processed",
            intersection.filename + ".npy"
        )
        with open(filepath, "wb") as f:
            pickle.dump(arrays, f, protocol=pickle.HIGHEST_PROTOCOL)

    return [(n, other_geocollection) for n in topo_geocollections]


def import_xt_from_rasterstats(fp, name, gc, **kwargs):
    metadata, data = load_file(fp)
    assert 'vector' in metadata and 'raster' in metadata, "Invalid metadata in file"

    vector = get_possible_collections(metadata['vector'])
    assert len(vector) == 1, "Must intersect with exactly one geocollection"

    vector = list(vector)[0]

    assert vector[1] != 'topocollection'

    xt = ExtensionTable(name)
    md = {
        "filepath": fp,
        "vector": metadata['vector'],
        "raster": metadata['raster'],
        'geocollection': gc,
    }
    md.update(**kwargs)
    xt.register(**md)
    xt.write([(row[1]['mean'], (vector[0], row[0]))
              for row in data
              if row[1]['mean'] is not None])
    return xt
