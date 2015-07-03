Common tasks with regionalized data
***********************************

.. _match-geocollections:

Match geocollections using Pandarus
===================================

.. _convert-to-ia:

Convert geocollection to Method data
====================================

.. note:: Conversion requires access to the actual spatial data and all needed metadata, i.e. filepaths, layer and field name for shapefiles, and raster band for rasters.

.. _convert-to-loading:

Convert geocollection to Loading data
=====================================

.. _load-from-pandarus:

Load Pandarus output
====================

To load the output from a Pandarus calculation, use ``Pandarus.import_from_pandarus`` (insert ref. to method docs here) like:

.. code-block:: python

    Intersection(("from geocollection name", "to geocollection name")).import_from_pandarus("")

.. note:: Be sure to pass the ``--lca`` if calling Pandarus from the command line.

.. warning:: Make sure the order of the two geocollections is the same in the Intersection object as it was in the Pandarus calculation.
