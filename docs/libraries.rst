.. _libraries:

Regionalization libraries
*************************

`Constructive Geometries <https://bitbucket.org/cmutel/constructive-geometries>`__
==================================================================================

This repository contains the scripts and data needed to build a consistent topology of the world (provinces, countries, and states), needed for the ecoinvent life cycle inventory database. It also includes the ability to define recipes to generate custom locations.

`Py-Constructive-Geometries <https://bitbucket.org/cmutel/py-constructive-geometries>`__
========================================================================================

Brightway2-regional uses the `py-constructive-geometries <https://bitbucket.org/cmutel/py-constructive-geometries>`__ library, which includes a topographical map of the world, as well as a few functions for manipulating topographical geometries.

.. autoclass:: constructive_geometries.ConstructiveGeometries
    :members:

`Ecoinvent RoW Report <https://bitbucket.org/cmutel/ecoinvent-row-report>`__
============================================================================

`Pandarus <https://bitbucket.org/cmutel/pandarus>`__
====================================================

Pandarus is software for taking two geospatial data sets (either raster or vector), and efficiently calculating their combined intersected areas. Brightway2-regional is designed to import the calculation results from Pandarus. See the source code repository for more information.

`Pandarus Remote <https://bitbucket.org/cmutel/pandarus_remote>`__
==================================================================

Pandarus remote is a web service for processing and managing data for regionalized life cycle assessment using Pandarus. Many large GIS calculations are better done on servers with enough resources to handle everything in memory. See the source code repository for API endpoints and installation instructions.
