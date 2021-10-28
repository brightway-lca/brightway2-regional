import hashlib
import os
from collections import defaultdict
from functools import partial

import fiona
import numpy as np
from shapely.geometry import shape

from bw2regional import geocollections
from bw2regional.lca.base_class import RegionalizationBase


def _generic_exporter(
    lca,
    geocollection,
    filepath,
    spatial_dict,
    spatial_func,
    score_column_absolute="score_abs",
    score_column_relative="score_rel",
    cutoff=1e-3,
):
    assert isinstance(lca, RegionalizationBase)
    assert geocollection in geocollections
    assert hasattr(lca, spatial_dict)
    assert os.path.isfile(geocollections[geocollection].get("filepath"))
    assert not os.path.isfile(filepath)

    vector = np.ravel(getattr(lca, spatial_func)().sum(axis=0))
    lca.fix_spatial_dictionaries()
    total = lca.score
    cut = abs(lca.score * cutoff)
    field = geocollections[geocollection].get("field")
    assert field

    # TODO: Might need to make this nicer/more robust
    if not filepath.endswith(".geojson"):
        filepath += ".geojson"

    if geocollection == "world":
        # Special case; "world" is just a string, not a tuple
        results = {
            spatial_key: vector[index]
            for spatial_key, index in getattr(lca, spatial_dict).items()
            if abs(vector[index]) >= cut
        }
    else:
        results = {
            spatial_key[1]: vector[index]
            for spatial_key, index in getattr(lca, spatial_dict).items()
            if abs(vector[index]) >= cut
        }

    with fiona.Env():
        with fiona.open(geocollections[geocollection]["filepath"]) as source:
            meta = source.meta
            meta["driver"] = "GeoJSON"
            meta["schema"]["properties"].update(
                {score_column_absolute: "float", score_column_relative: "float"}
            )

            with fiona.open(filepath, "w", **meta) as sink:
                for feature in source:
                    try:
                        score = results[feature["properties"][field]]
                        feature["properties"][score_column_absolute] = score
                        feature["properties"][score_column_relative] = abs(
                            score / total
                        )
                        sink.write(feature)
                    except KeyError:
                        continue


as_inv_spatial_scale = partial(
    _generic_exporter,
    spatial_dict="inv_spatial_dict",
    spatial_func="results_inv_spatial_scale",
)

as_ia_spatial_scale = partial(
    _generic_exporter,
    spatial_dict="ia_spatial_dict",
    spatial_func="results_ia_spatial_scale",
)

as_xt_spatial_scale = partial(
    _generic_exporter,
    spatial_dict="xtable_spatial_dict",
    spatial_func="results_xtable_spatial_scale",
)


def _hash_feature(feature):
    """Calculate SHA256 hash of feature geometry as WKT"""
    geom = shape(feature["geometry"])
    return hashlib.sha256(geom.to_wkt().encode("utf-8")).hexdigest()


def add_two_geojson_results(
    first,
    second,
    output_filepath,
    first_column_name="score_abs",
    second_column_name="score_abs",
    score_column_absolute="score_abs",
    score_column_relative="score_rel",
    cutoff=1e-4,
):
    """Sum results from two regionalized LCA calculations on the same spatial scale."""
    results, features = defaultdict(float), {}

    # TODO: Might need to make this nicer/more robust
    if not output_filepath.endswith(".geojson"):
        output_filepath += ".geojson"

    with fiona.open(first, "r") as obj:
        meta = obj.meta

        for feature in obj:
            hashed = _hash_feature(feature)
            features[hashed] = feature
            results[hashed] += feature["properties"][first_column_name]

    with fiona.open(second, "r") as obj:
        for feature in obj:
            hashed = _hash_feature(feature)
            features[hashed] = feature
            results[hashed] += feature["properties"][second_column_name]

    total = sum(results.values())

    meta["driver"] = "GeoJSON"
    meta["schema"]["properties"].update(
        {score_column_absolute: "float", score_column_relative: "float"}
    )

    with fiona.open(output_filepath, "w", **meta) as sink:
        for k, feature in features.items():
            score = results[k]
            if abs(score) < abs(total * cutoff):
                continue

            feature["properties"][score_column_absolute] = score
            feature["properties"][score_column_relative] = abs(score / total)
            sink.write(feature)
