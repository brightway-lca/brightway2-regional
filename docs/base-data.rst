.. _basedata:

Base data needed for regionalized calculations
==============================================

Defining countries
------------------

Next, we create a geocollection ``"world"`` and topocollection ``"world"``. It is quite useful to label countries by their `ISO 3166-1 alpha-2 <https://en.wikipedia.org/wiki/ISO_3166-1>`__ country codes (e.g. "DE" for Germany), so we don't require these locations to be given a complex location key like ``("world", "DE")``; instead, we will treat any two letter country code as if it came from the ``"world"`` geocollection.

Defining ecoinvent-specific locations
-------------------------------------

Ecoinvent defines a large number of additional locations, like "Europe" or "Canada without Alberta and Quebec". See the `constructive geometries source repository <https://bitbucket.org/cmutel/constructive-geometries>`__ for more information on ecoinvent-specific locations. These locations are handled in a third new geocollection, ``"ecoinvent"``, as well as the ``"ecoinvent"`` topocollection.

Topographies
------------

Extension tables
----------------

Summary
-------

``bw2regionalsetup()`` create the following:

Geocollections
``````````````

* world
* ecoinvent
* RoW
* gdp-weighted-pop-density

Topocollections
```````````````

* world
* ecoinvent
* RoW
* gdp-weighted-pop-density

Topographies
````````````

* world
* ecoinvent
* RoW

Extension tables
````````````````

* gdp-weighted-pop-density

Intersections
`````````````

The following ``intersections`` are only created if the default pandarus_remote server, https://pandarus.brightwaylca.org, is available.

* ('world', 'geo-weighted-pop-density')
* ('ecoinvent', 'geo-weighted-pop-density')
* ('RoW', 'geo-weighted-pop-density')
