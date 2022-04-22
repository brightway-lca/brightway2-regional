## 0.6.DEV2 (2022-04-22)

* Add ability to calculate intersections with geopandas instead of pandarus remote server
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
