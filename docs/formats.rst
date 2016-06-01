Data and data formats
*********************

.. _geocollections:

Geocollections
==============

Geocollections are containers that organize and describe sets of spatial data identifiers, and possibly other data, including spatial supports. They are similar to the concept of Databases in Brightway2: an inventory dataset could be identified by ``("My new database", "Dataset 14")``, while spatial unit could have a similar id: ``("My new raster", "Cell 42, 11")``. However, only metadata is stored for each geocollection, so there is no ``Geocollection`` object, only ``geocollections``.

Geocollections are used by both inventory data sets (e.g. for custom locations) and impact assessment methods.

Geocollections can refer to vector or raster data. For example, one geocollection could be the set of world countries, as described by the `Natural Earth data <http://www.naturalearthdata.com/>`_, while another could be the raster cells used in a particular impact assessment method.

Geocollections have two purposes in Brightway2:

    * They provide a conceptual and physical grouping of spatial data into manageable units
    * They provide a way to uniquely identify spatial data

A geocollection is not a geodatabase - no spatial data is required. However, if the original spatial data is available (as a vector or raster file), it can be specified and used later in analysis.

A geocollection is specified by a unique string, which is usually the name of the geocollection.

Metadata fields
---------------

There are no required metadata fields for geocollections, but some common fields are useful when the original data is available. All the below listed metadata field values should be strings:

    * **filepath**: Filepath for the vector or raster file
    * **layer**: Layer name (vector data only)
    * **field**: Field name that uniquely identifies each feature (vector data only)
    * **vfs**: Virtual file system used to load zipped shapefiles
    * **encoding**: Text encoding

.. note:: It is *strongly* preferred that ESRI shapefile be zipped to a single file, with appropriate metadata. Ideally, each Geocollection can have its associated spatial data in a single file. For example, the Natural Earth 50m political data is specified as: ``vfs="zip:///Users/cmutel/Downloads/Geodata/ne_50m_admin_0_countries.zip", filepath="/ne_50m_admin_0_countries.shp``. See `the Fiona manual <http://toblerity.org/fiona/manual.html#virtual-filesystems>`_ for more.

.. _standard-geocollections:

Standard geocollections
-----------------------

The following are some standard geocollections, and are installed automatically.

    * **global**: Only the global location "GLO"
    * **countries**: All the countries in the world, as defined by ISO, and identified by the ISO 2-letter codes.
    * **regions**: `UN regions and subregions <http://unstats.un.org/unsd/methods/m49/m49regin.htm>`_
    * **ecoinvent 2**: Special regions defined by ecoinvent in version 2 of the database
    * **ecoinvent 3**: Special regions defined by ecoinvent in version 3 of the database

.. _regionalized-ia:

Regionalized impact assessment
==============================

Regionalized impact assessment methods have characterization factors that depend both on biosphere flows and spatial units. Characterization factors can be static or uncertain.

In Brightway2, the ``Method`` object can store site-generic, regionalized, or both site-generic and regionalized characterization factors. Similarly, the ``methods`` metadata store works the same for site-generic and regionalized IA methods.

.. _specifying-spatial:

Specifying spatial objects
--------------------------

Following the Brightway2 principle of KISS, spatial objects have a simple format with reasonable defaults:

    #. If not location data is provided, the global location "GLO" is assumed
    #. A two-letter ISO county code can be used
    #. Otherwise, spatial objects should be identified by the combination of geocollection and id, just like objects in Databases: ``(geocollection, spatial unit id)``.

Metadata
--------

In addition to the standard metadata for IA methods, such as ``unit`` and ``description``, regionalized IA methods should include the following for complete functionality:

    * **geocollections**: List of one or more strings identifying the geocollections. Normally only one geocollection is associated with a regionalized IA method. See :ref:`geocollections`.
    * **band**: Band number in original raster data set. Needed to import characterization factors.
    * **cf_field**: Field name of characterization factor value. Needed to import characterization factors.

Data format
-----------

Site-generic IA methods have a simple data format:

.. code-block:: python

    [
        [biosphere flow, maybe uncertainty],
    ]

Where ``maybe uncertainty`` is either a floating point number (implying no uncertainty), or a `stats_array uncertainty dictionary <http://stats-arrays.readthedocs.io/en/latest/>`_, like:

.. code-block:: python

    {'loc': 2, 'scale': 0.5, 'uncertainty_type': NormalUncertainty.id}

.. note:: In site-generic CFs, where a location is not given, the "GLO" location is assumed.

Regionalized IA methods are almost the same; they just have an additional field for a location specifier.

.. code-block:: python

    [
        [biosphere flow, maybe uncertainty, spatial object],
    ]

Loadings
========

Background loadings are data on the spatial patterns of emission, and are used to determine the relatively likelihood that a given inventory dataset occurs in a impact assessment spatial unit. The idea is that the existing patterns of emissions are reasonable predictors of where present or future emissions will occur.

In Brightway2, background loadings are represented by the ``Loading`` objects, and metadata about all loadings is stored in ``loadings``.

Because loadings are a density of predicted activity, their unit is physical quantity (e.g. mass or energy) per unit area. Loadings are multiplied by intersected areas, and then normalized by total loading, so their units are canceled out in the end.

As loadings are emission-specific, this could mean that different loadings for different biosphere flows could predict different spatial patterns of inventory activity. There is no real research on the importance of this inconsistency.

Background loadings are, in general, supplied by the impact assessment method developers. If no loadings are supplied, the generic fallback is to allocate impact assessment spatial units to inventory spatial unit by intersected area; however, proxy loadings can be independently calculated. See **this example ipython notebook** for one such procedure.

Background loadings should always use the same geocollection as their IA methods.

Metadata
--------

Their are no required fields for background loadings, as most metadata comes from the IA method. Fields such as ``description`` can be used.

Data format
-----------

.. code-block:: python

    [
        [maybe_uncertainty, location_id],
    ]

.. warning:: Industry sector-specific loadings and emission-specific loadings are not yet supported in bw2regional.

Intersections
=============

Data for the geographic transform matrix **G** is stored in Intersection objects. In Brightway2, areal intersection data is represented by the ``Intersection`` object, and the metadata store is ``intersections``. Each combination of geocollections should be a separate ``Intersection`` object.

Intersection data is calculated using `pandarus <https://bitbucket.org/cmutel/pandarus>`_. Conversion from the pandarus data format  is done with the utility function :ref:`load-from-pandarus`.

Metadata
--------

No metadata is required for intersections.

The ``pandarus-filepath`` field is the filepath of the Pandarus file, and is set automatically when imported.

Data format
-----------

We assume that data is written automatically after conversion from pandarus, so users shouldn't be writing or manipulating intersection data themselves. Nevertheless, here is the data format:

.. code-block:: python

    [
        [spatial object 1, spatial object 2, intersection area],
    ]

Extension tables
================

Metadata
--------

In addition to the standard metadata for IA methods, such as ``unit`` and ``description``, regionalized IA methods should include the following for complete functionality:

    * **geocollection**: String identifying a geocollection. See :ref:`geocollections`.
    * **xt_field**: Field name used for extension table values. Only needed for vector spatial data.
    * **band**: Raster band index for extension table values.

Data format
-----------

.. code-block:: python

    [
        [float, spatial object 1]
    ]
