# regional Changelog

## 0.7.DEV2 (2024-04-28)

* Bugfix from DEV1

## 0.7.DEV1 (2024-04-28)

* Allow extension tables to reference more than one geocollection

## 0.6.DEV10 (2023-04-26)

* Add `extra_data_objs` parameter to regionalized LCA classes

## 0.6.DEV9 (2023-04-25)

* Fix bug in calling Geopandas

## 0.6.DEV8 (2023-04-24)

* Add `calculate_needed_intersections` function
* Add `rasterstats` engine to `raster_as_extension_table`
* Added `rasterstats` dependency
* Don't error out on jobs which are skipped because already done

## 0.6.DEV7 (2023-04-24)

* Don't raise errors for `AlreadyExists`
* Fix path error

## 0.6.DEV6 (2022-04-27)

* Allow masking when importing maps as extension tables

## 0.6.DEV5 (2022-04-26)

* Re-enable some pandarus functionality

## 0.6.DEV4 (2022-04-24)

* Include cutoff in geodataframe creation

## 0.6.DEV3 (2022-04-23)

* Added GeoDataframe exports to all LCA classes
* Fix matrix reconstruction on iteration

## 0.6.DEV2 (2022-04-22)

* Add ability to calculate intersections with geopandas and pandarus, in addition to pandarus remote server
* Switch to Brightway 2.5 datapackages

## 0.6.DEV1 (2021-10-20)

* Move to Py3 only
* Fix bug with long filepaths on Windows

## 0.5.2 (2019-01-01)

* Code reformatting with Black
* Update for `fiona` upstream changes
* Better messages for when remote calculation is needed (instead of just erroring)
* FIx incompatibility in datatypes between intersection and intersection from pandarus creation

## 0.5.1 (2018-08-17)

* Fix passing invalid fields to `fiona.open`
* Everything other than inputs to rasterstats must be vector files
* Small bug fixes and simplifications

# 0.5 (2017-06-15)

* Add compatibility with [rower](https://github.com/PascalLesage/RoWer) and rewrote ecoinvent/RoW handling
* Add utility to divide rasters by their cell area (`density/divide_by_area`)
* Update and test setup code
