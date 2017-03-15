#!/usr/bin/env bash
rm *.json.bz2
pandarus intersect test_countries.gpkg --field1=name test_raster_cfs.tif intersect-countries-cfs
pandarus intersect test_countries.gpkg --field1=name test_provinces.gpkg --field2=OBJECTID_1 intersect-countries-provinces
pandarus intersect test_provinces.gpkg --field1=OBJECTID_1 test_raster_cfs.tif intersect-topo-cfs
pandarus area test_provinces.gpkg --field=OBJECTID_1 areas-topo
pandarus area test_countries.gpkg --field=name areas-countries
pandarus area test_raster_cfs.tif areas-cfs
