Regionalization in Brightway2
=============================

.. image:: images/mnglr.png
    :align: center

It is easy to do regionalized LCA incorrectly. This package tries to make it at least a bit easier to do regionalization correctly, for at least some definitions of correctly.

bw2regional supports the following regionalization calculations:

    #. Inventory database and impact assessment method share the same spatial scale (:ref:`one-scale`)
    #. Inventory and impact assessment have different spatial scales (:ref:`two-scales`)
    #. Inventory and impact assessment have different spatial scales, with background loading used for spatial allocation (:ref:`two-scales-with-loading`)
    #. Inventory and impact assessment have different spatial scales, with extension tables used as a third spatial scale to allocate impact assessment units to inventory units.

In addition to making regionalized LCA calculations, maps of regionalized impact can be exported from methods 2-4.

Each separate spatial scale is stored as a ``geocollection``. The relationships between spatial scales (i.e. how much area of unit *a* in spatial scale *1* intersects unit *b* in spatial scale *2*) is stored as an ``Intersection``. Areal intersection calculations are done using the separate utility `pandarus <https://bitbucket.org/cmutel/pandarus>`__, a library for matching spatial data sets and calculating their mutual intersected areas. Impact assessment methods store characterization factors per biosphere flow and spatial unit. Each organization unit is described in more detail below.

Spatial scales (``geocollections``)
===================================

Spatial scales each need a name and some metadata. Spatial scale names are stored in :ref:`geocollections`. No additional information about a ``geocollection`` is required, but if you want to be able to export maps or import characterization factors, the following fields can be provided:

    * ``filepath``: The absolute filepath to the vector or raster dataset.
    * ``field``: The unique field that identifies each feature, e.g. name for countries.
    * ``layer``: The name of the layer. Only needed for vector datasets with more than one layer.
    * ``encoding``: The text encoding. Only needed for shapefiles.
    * ``vfs``: For shapefiles stored in zip archives, this is the virtual file system string, e.g. ``vfs="zip:///path/to/file/ne_50m_admin_0_countries.zip"``. Note that with a vfs, you must spcify the filepath within the zip archive, e.g. ``filepath="/ne_50m_admin_0_countries.shp"``. See also `the fiona manual <https://github.com/Toblerity/Fiona#collections-from-archives-and-virtual-file-systems>`__.

Example creation of a geocollection:

.. code-block:: python

    from bw2regional import *
    geocollections['water cfs'] = {'filepath': u'/my/favorite/directory/pretty-picture.tiff'}

Intersections
=============

An ``Intersection`` is set of data that gives areal intersections from one spatial scale to the next. Areal intersections can be calculated using whatever GIS software and projection that you want, but ``bw2regional`` is designed to work seamlessly with `pandarus <https://bitbucket.org/cmutel/pandarus>`__, which can quickly and painlessly do these areal intersection calculations and write data in a data format ``bw2regional`` understands.

An ``Intersection`` object does not have its own name, but rather is defined by the two ``geocollections`` which are intersected.

Example use of pandarus (see also the `pandarus documentation <http://pandarus.readthedocs.org/en/latest/>`__):

.. code-block:: bash

    pandarus /Users/somebody/some-raster.tiff /Users/somebody/some-shapefile.shp --field2=name foo.bar

This would create the file ``foo.bar.json.bz2``.

Example import of pandarus output data:

.. note:: You should create the geocollections first before creating an Intersection between them.

.. code-block:: python

    from bw2regional import *
    geocollections['some-raster'] = {'filepath': u'/Users/somebody/some-raster.tiff'}
    geocollections['some-shapefile'] = {
                                        'filepath': u'/Users/somebody/some-shapefile.shp',
                                        'field': 'name'
                                        }
    Intersection(('some-raster', 'some-shapefile')).import_from_pandarus('foo.bar.json.bz2')



A number of utility functions should make importing and manipulating the spatial data needed.

Contents:

.. toctree::
   :maxdepth: 2

   formats
   lca
   common
   technical

Development
===========

bw2regional is developed by `Chris Mutel <http://chris.mutel.org/>`_, previously during his work as a postdoctoral assistant in the `Ecological Systems Design group <http://www.ifu.ethz.ch/ESD/index_EN>`__ at ETH Zürich, and currently as a scientist in the `Technology Assessment group <http://www.psi.ch/ta/>`__ at the Paul Scherrer Institute.

Source code is available on `bitbucket <https://bitbucket.org/cmutel/brightway2-regional>`__.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

