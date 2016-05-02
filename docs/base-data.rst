.. _basedata:

Base data needed for regionalized calculations
==============================================

Defining Rest-of-the-World locations
------------------------------------

Calling the function ``bw2regionalsetup()`` creates several new metadatasets.

First, a data file that defines the various Rest-of-the-World locations for ecoinvent 3+ is downloaded, and added to the data store ``restofworlds``. Each Rest-of-the-World dataset has a label like *RoW-42*, and is defined by the areas which are excluded from its location. For example, *RoW-152* excludes Germany, Algeria, the Netherlands, Norway, and Russia. The data format for ``restofworlds`` is a dictionary of excluded codes::

    {'RoW-152': ['DE', 'DZ', 'NL', 'NO', 'RU']}

In ``restofworlds``, these codes are the ecoinvent *shortnames*, and there is no distinction between what will later be split into different ``geocollections``.

For more information on Rest-of-the-Worlds, see the `ecoinvent geography report <http://geography.ecoinvent.org/report/>`__ and the `ecoinvent interactive Rest-of-the-Worlds explorer <http://geography.ecoinvent.org/rows/>`__.

However, it is not enough to have a list of information that could be used to identify each Rest-of-the-Word - we also need to have concrete data on what these locations include. This means that we create a new geocollection ``"RoW"``, as well as a topocollection ``"RoW"``.

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
