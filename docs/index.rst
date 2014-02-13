.. bw2-regional documentation master file, created by
   sphinx-quickstart on Fri Jan 17 17:10:55 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Regionalization in Brightway2
=============================

It is easy to do regionalized LCA incorrectly. This package tries to make it at least a bit easier to do regionalization correctly, for at least some definition of correctly.

bw2regional supports the following regionalization calculations:

    #. Inventory database and impact assessment method share the same spatial scale <LCA class>
    #. Inventory and impact assessment have different spatial scales <LCA class>
    #. Inventory and impact assessment have different spatial scales, with background loading used for spatial allocation <LCA class>

In addition to making regionalized LCA calculations, maps of regionalized impact can be exported from methods 2 and 3.

bw2regional is designed to work closely with `pandarus <https://bitbucket.org/cmutel/pandarus>`_, a library for matching spatial data sets and calculating their mutual intersected areas.

bw2regional introduces the idea of :ref:`geocollections`, which organize and identify spatial scales, similar to how Databases are used in bw2data.

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

bw2regional is developed by `Chris Mutel <http://chris.mutel.org/>`_ as part of his work at the `Ecological Systems Design group <http://www.ifu.ethz.ch/ESD/index_EN>`_ at ETH Zürich.

Source code is available on `bitbucket <https://bitbucket.org/cmutel/brightway2-regional>`_.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

