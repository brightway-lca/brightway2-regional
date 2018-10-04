from bw2regional import geocollections
from bw2regional.lca.base_class import RegionalizationBase
from functools import partial
import fiona
import numpy as np
import os


def _generic_exporter(lca, geocollection, filepath,
                      spatial_dict, spatial_func,
                      score_column_absolute="score_abs",
                      score_column_relative="score_rel", cutoff=1e-3,

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
        results = {spatial_key: vector[index]
                   for spatial_key, index in getattr(lca, spatial_dict).items()
                   if abs(vector[index]) >= cut}
    else:
        results = {spatial_key[1]: vector[index]
                   for spatial_key, index in getattr(lca, spatial_dict).items()
                   if abs(vector[index]) >= cut}


    with fiona.drivers():
        with fiona.open(geocollections[geocollection]["filepath"]) as source:
            meta = source.meta
            meta['driver'] = 'GeoJSON'
            meta['schema']['properties'].update({
                score_column_absolute: "float",
                score_column_relative: "float"
            })

            with fiona.open(filepath, 'w', **meta) as sink:
                for feature in source:
                    try:
                        score = results[feature['properties'][field]]
                        feature['properties'][score_column_absolute] = score
                        feature['properties'][score_column_relative] = abs(score / total)
                        sink.write(feature)
                    except KeyError:
                        continue


as_inv_spatial_scale = partial(
    _generic_exporter,
    spatial_dict="inv_spatial_dict",
    spatial_func="results_inv_spatial_scale"
)

as_ia_spatial_scale = partial(
    _generic_exporter,
    spatial_dict="ia_spatial_dict",
    spatial_func="results_ia_spatial_scale"
)

as_xt_spatial_scale = partial(
    _generic_exporter,
    spatial_dict="xtable_spatial_dict",
    spatial_func="results_xtable_spatial_scale"
)
