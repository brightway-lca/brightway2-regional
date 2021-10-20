.. _basedata:

Base data needed for regionalized calculations
==============================================

Defining countries
------------------

Next, we create a geocollection ``"world"`` and topocollection ``"world"``. It is quite useful to label countries by their `ISO 3166-1 alpha-2 <https://en.wikipedia.org/wiki/ISO_3166-1>`__ country codes (e.g. "DE" for Germany), so we don't require these locations to be given a complex location key like ``("world", "DE")``; instead, we will treat any two letter country code as if it came from the ``"world"`` geocollection.

Defining ecoinvent-specific locations
-------------------------------------

Ecoinvent defines a large number of additional locations, like "Europe" or "Canada without Alberta and Quebec". See the `constructive geometries source repository <https://github.com/cmutel/constructive_geometries>`__ for more information on ecoinvent-specific locations. These locations are handled in a third new geocollection, ``"ecoinvent"``, as well as the ``"ecoinvent"`` topocollection.

Topographies
------------

Extension tables
----------------

Summary
-------

``create_world_collections()`` creates the following:

Geocollections
``````````````

* world

Topocollections
```````````````

* world

Topographies
````````````

* world

``create_ecoinvent_collections()`` creates the following:

Geocollections
``````````````

* ecoinvent
* RoW

Topocollections
```````````````

* ecoinvent
* RoW

Topographies
````````````

* ecoinvent
* RoW
