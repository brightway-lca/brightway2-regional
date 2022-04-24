import bw2data as bd

from . import (
    Intersection,
    extension_tables,
    geocollections,
    intersections,
    topocollections,
)
from .pandarus import import_from_pandarus, import_xt_from_rasterstats
from .pandarus_remote import PandarusRemote, remote, run_job

try:
    import pandarus
except ImportError:
    pandarus = None
import multiprocessing
import os

import geopandas as gp

CPU_COUNT = multiprocessing.cpu_count()


def raster_as_extension_table(
    vector, raster, name=None, engine=remote, overwrite=False
):
    if vector not in geocollections or raster not in geocollections:
        raise ValueError("Vector or raster not a valid geocollection")
    if vector in topocollections:
        raise ValueError(
            "this function only works with geocollections, not topocollections"
        )

    if name is None:
        name = vector + " - " + raster

    dirpath = bd.projects.request_directory("regional")
    fp = str(dirpath / name + ".json")

    if name in extension_tables and not overwrite:
        return

    if isinstance(engine, PandarusRemote):
        print("Calculating raster statistics")
        run_job(engine.calculate_rasterstats(vector, raster))

        print("Creating Extension Table")
        return engine.rasterstats_as_xt(vector, raster, name)

    elif engine == "pandarus":
        if not pandarus:
            raise ImportError("`pandarus` library required for this function")

        vector_fp, vector_field = (
            geocollections[vector]["filepath"],
            geocollections[vector]["field"],
        )
        raster_fp, raster_band = geocollections[raster]["filepath"], geocollections[
            raster
        ].get("band", 1)

        fp = pandarus.raster_statistics(
            vector_fp,
            vector_field,
            raster_fp,
            output=fp,
            band=raster_band,
            compress=True,
        )

        return import_xt_from_rasterstats(fp, name, vector)

    else:
        raise ValueError(f"Can't understand engine {engine}")


def calculate_intersection(first, second, engine=remote, overwrite=False, cpus=None):
    """Calculate and write areal intersections between two vector geocollections"""
    if (first, second) in intersections and not overwrite:
        return

    if engine == "geopandas":
        for gc in (first, second):
            assert (
                gc in geocollections
                and geocollections[gc].get("kind") == "vector"
                and "field" in geocollections[gc]
            )
        assert geocollections[first]["filepath"] != geocollections[second]["filepath"]

        df1 = gp.read_file(geocollections[first]["filepath"])
        df2 = gp.read_file(geocollections[second]["filepath"])
        id1 = geocollections[first]["field"]
        id2 = geocollections[second]["field"]

        assert id1 != id2, "Conflicting ID labels"

        intersection = gp.overlay(df1, df2)
        areas = intersection.to_crs(
            "esri:54009"
        ).area  # World Mollweidge in square meters

        data = []
        for index, feature in intersection.iterrows():
            data.append(((first, feature[id1]), (second, feature[id2]), areas[index]))

        obj = Intersection((first, second))
        obj.write(data)
        obj.create_reversed_intersection()
    elif engine == "pandarus":
        try:
            first_meta = topocollections[first]
        except KeyError:
            first_meta = geocollections[first]
        try:
            second_meta = topocollections[second]
        except KeyError:
            second_meta = geocollections[second]

        dirpath = str(bd.projects.request_directory("regional"))

        fiona_fp, data_fp = pandarus.intersect(
            first_meta["filepath"],
            first_meta["field"],
            second_meta["filepath"],
            second_meta["field"],
            dirpath=dirpath,
            cpus=cpus or CPU_COUNT,
            driver="GeoJSON",
            compress=True,
        )

        return import_from_pandarus(data_fp)
    elif isinstance(engine, PandarusRemote):
        print("Calculating intersection")
        run_job(engine.calculate_intersection(first, second))

        print("Creating Intersection")
        return engine.intersection(first, second)
