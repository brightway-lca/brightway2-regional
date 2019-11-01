# 0.5.2 (2019-01-01)

* Code reformatting with Black
* Update for `fiona` upstream changes
* Better messages for when remote calculation is needed (instead of just erroring)
* FIx incompatibility in datatypes between intersection and intersection from pandarus creation

# 0.5.1 (2018-08-17)

* Fix passing invalid fields to `fiona.open`
* Everything other than inputs to rasterstats must be vector files
* Small bug fixes and simplifications

# 0.5 (2017-06-15)

* Add compatibility with [rower](https://github.com/PascalLesage/RoWer) and rewrote ecoinvent/RoW handling
* Add utility to divide rasters by their cell area (`density/divide_by_area`)
* Update and test setup code
