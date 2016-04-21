# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from .meta import topocollections, geocollections, intersections
from .intersection import Intersection
from bw2data import DataStore, JsonWrapper


class Topography(DataStore):
    """A topographical description of a `geocollection`.

    A topography must be registered to exactly one geocollection.

    For example, the geocollection 'countries' could have the location 'Ghana', and include a spatial data file which defines 'Ghana'. The `Topography` 'countries-topo' would have two files:

        #. A mapping file that linked each location in the geocollection 'countries' to a set of topographical faces
        #. A spatial dataset which defines the topographical faces

    Topographies can make some calculations much quicker for two reasons:

        #. Large features are split into smaller faces, making GIS calculations easier and spatial index queries more efficient, as bounding boxes are smaller
        #. You only do GIS work on each topographical face once

    The LCA classes in `bw2regional` don't work directly with the `Topography` objects; rather, GIS calculations on topographies can be merged to the spatial features of the `geocollection`.

    TODO: What default topographies are installed, if any?

    The usual order of operations with a `geocollection` that has a `Topography` is the following:

        #. Create a `geocollection`, including defining a spatial dataset
        #. Create a new `topocollection` and specify the linked `geocollection`. You can also optionally define another spatial dataset, using the same format as for `geocollections`.
        #. Instantiate the new `Topography` object created in the earlier step, and write mapping data from spatial features in the `geocollection`(s) to face ids in the `Topography` spatial data set.
        #. Import intersection data between the `Topography` and `geocollection` 2 using the method `import_from_pandarus`. This method will create a new `Intersection` between the `geocollection` linked to the current `Topography` and `geocollection` 2.

    The data format for mapping data is ``{feature field value: [list of topo field values (usually id numbers)]}``.

    Here is a code sample for using the test data in `bw2regional`:

    .. code-block:: python

        from bw2regional import Topography, geocollections
        from bw2regional.tests import data_dir
        import json

        geocollections['countries'] = {
            'filepath': os.path.join(data_dir, "test_countries.gpkg"),
            'field': 'name'
        }
        topocollections['countries-topo'] = {
            'geocollection': 'countries',
            'filepath': os.path.join(data_dir, "test_provinces.gpkg"),
            'field': 'OBJECTID_1'
        }
        topo = Topography('countries-topo')
        topo.write(json.load(open(os.path.join(data_dir, "test_topo_mapping.json"))))
        topo.import_from_pandarus(os.path.join(data_dir, "intersect-topo-cfs.json.bz2"), "countries")

    """
    _metadata = topocollections

    def write(self, data):
        self.metadata['empty'] = False
        self._metadata.flush()
        super(Topography, self).write(data)

    def import_from_pandarus(self, filepath, target_geocollection):
        """Import a `pandarus` intersections output file.

        The imported file must be between the current topography and the geocollection `target_geocollection`, and in this order.

        An intersection between this topography's associated geocollection and the `target_geocollection` is created, as well as the reversed intersection.

        """
        our_geocollection = self.metadata.get("geocollection")
        assert our_geocollection in geocollections, "No registered geocollection"
        assert target_geocollection in geocollections, "Can't find target geocollection"
        assert (our_geocollection, target_geocollection) not in intersections, "intersection already exists"

        mapping = self.load()
        assert mapping, "No topographical mapping data available"

        try:
            intersection_data = JsonWrapper.load_bz2(filepath)
        except:
            intersection_data = JsonWrapper.load(filepath)

        merged_data = merge(intersection_data, mapping)
        processed_data = relabel(
            merged_data,
            our_geocollection,
            target_geocollection
        )

        intersection = Intersection((our_geocollection, target_geocollection))
        intersection.write(processed_data)
        intersection.metadata['filepath'] = filepath
        intersection.create_reversed_intersection()

        return intersection
