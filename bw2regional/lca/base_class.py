# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from eight import *

from ..errors import (
    MissingIntersection,
    SiteGenericMethod,
    UnprocessedDatabase,
)
from ..intersection import Intersection
from ..meta import intersections
from ..utils import get_pandarus_map, get_pandarus_map_for_method
from bw2calc.lca import LCA
from bw2calc.matrices import MatrixBuilder
from bw2data import databases, methods, geomapping, Method, Database
from scipy.sparse import csr_matrix
import itertools
import numpy as np


class RegionalizationBase(LCA):
    def __init__(self, demand, *args, **kwargs):
        super(RegionalizationBase, self).__init__(demand, *args, **kwargs)
        self.databases = set.union(*[Database(key[0]).find_graph_dependents() for key in demand])

    def get_inventory_geocollections(self):
        """Get the set of all needed inventory geocollections.

        Raise UnprocessedDatabase if any database is missing the required metadata."""
        missing, present = [], set()
        for database in self.databases:
            if "geocollections" not in databases[database]:
                missing.append(database)
            else:
                present.update(set(databases[database]['geocollections']))
        if missing:
            raise UnprocessedDatabase(
                u"Database(s) {} don't specify their geocollections.".format(
                missing)
            )
        return present

    def get_ia_geocollections(self):
        """Retrieve the geocollections linked to the impact assessment method"""
        try:
            return set(methods[self.method]['geocollections'])
        except:
            raise SiteGenericMethod

    def get_inventory_mapping_matrix(self, builder=MatrixBuilder):
        """Get inventory mapping matrix, **M**, which maps inventory activities to inventory locations. Rows are inventory activities and columns are inventory spatial units.

        Uses ``self._activity_dict`` and ``self.databases``.

        Returns:
            * ``inv_mapping_params``: Parameter array with row/col of inventory activities/locations
            * ``inv_spatial_dict``: Dictionary linking inventory locations to matrix columns
            * ``inv_mapping_matrix``: The matrix **M**

        """
        inv_mapping_params, _, inv_spatial_dict, inv_mapping_matrix = \
            builder.build(
                paths=[Database(x).filepath_geomapping() for x in self.databases],
                data_label="amount",
                row_id_label="activity",
                row_index_label="row",
                col_id_label="geo",
                col_index_label="col",
                row_dict=self._activity_dict,
            )
        return (inv_mapping_params, inv_spatial_dict, inv_mapping_matrix)

    def needed_intersections(self):
        """Figure out which ``Intersection`` objects are needed bsed on ``self.inventory_geocollections`` and ``self.ia_geocollections``.

        Raise ``MissingIntersection`` if an intersection is required, but not available."""
        required = list(itertools.product(
            self.inventory_geocollections,
            self.ia_geocollections
        ))
        for obj in required:
            if obj not in intersections:
                raise MissingIntersection(
                    u"Intersection {} needed but not found".format(obj))
        return required

    def get_geo_transform_matrix(self, builder=MatrixBuilder):
        """Get geographic transform matrix **G**, which gives the intersecting areas of inventory and impact assessment spatial units. Rows are inventory spatial units, and columns are impact assessment spatial units.

        Uses ``self.inv_spatial_dict`` and ``self.ia_spatial_dict``.

        Returns:
            * ``geo_transform_params``: Parameter array with row/col of inventory and IA locations
            * ``geo_transform_matrix``: The matrix **G**

        """
        geo_transform_params, _, _, geo_transform_matrix = \
            builder.build(
                paths=[
                    Intersection(name).filepath_processed()
                    for name in self.needed_intersections()
                ],
                data_label="amount",
                row_id_label="geo_inv",
                row_index_label="row",
                col_id_label="geo_ia",
                col_index_label="col",
                row_dict=self.inv_spatial_dict,
                col_dict=self.ia_spatial_dict
            )
        return geo_transform_params, geo_transform_matrix

    def get_regionalized_characterization_matrix(self, builder=MatrixBuilder):
        """Get regionalized characterization matrix, **R**, which gives location- and biosphere flow-specific characterization factors. Rows are impact assessment spatial units, and columns are biosphere flows.

        Uses ``self._biosphere_dict`` and ``self.method``.

        Returns:
            * ``reg_cf_params``: Parameter array with row/col of IA locations/biosphere flows
            * ``ia_spatial_dict``: Dictionary linking impact assessment locations to matrix rows
            * ``reg_cf_matrix``: The matrix **R**

        """
        reg_cf_params, ia_spatial_dict, _, reg_cf_matrix = \
            builder.build(
                paths=[Method(self.method).filepath_processed()],
                data_label="amount",
                row_id_label="geo",
                row_index_label="row",
                col_id_label="flow",
                col_index_label="col",
                col_dict=self._biosphere_dict,
            )
        return (reg_cf_params, ia_spatial_dict, reg_cf_matrix)

    def get_loading_matrix(self, builder=MatrixBuilder):
        """Get regionalized loading matrix, **L**, which gives location-specific background loading factors. Rows are impact assessment spatial units, and columns are biosphere flows.

        Uses ``self.inv_spatial_dict`` and ``self.ia_spatial_dict``.

        Returns:
            * ``loading_params``: Parameter array with row/col of IA locations/biosphere flows
            * ``loading_matrix``: The matrix **L**

        """
        loading_params, _, _, loading_matrix = \
            builder.build(
                paths=[self.loading.filepath_processed()],
                data_label="amount",
                row_id_label="geo",
                row_index_label="row",
                row_dict=self.ia_spatial_dict,
                one_d=True
            )
        return (loading_params, loading_matrix)

    def fix_spatial_dictionaries(self):
        """Fix inventory and IA spatial dictionaries."""
        if not hasattr(self, "inv_spatial_dict"):
            # No LCIA performed yet
            return
        if getattr(self, "_mapped_spatial_dict", False):
            # Already reversed - should be idempotent
            return False
        rev_geomapping = {v: k for k, v in geomapping.items()}
        self.inv_spatial_dict = {rev_geomapping[k]: v for k, v
            in self.inv_spatial_dict.items()}
        if hasattr(self, "ia_spatial_dict"):
            self.ia_spatial_dict = {rev_geomapping[k]: v for k, v
                in self.ia_spatial_dict.items()}
        if hasattr(self, "xtable_spatial_dict"):
            self.xtable_spatial_dict = {rev_geomapping[k]: v for k, v
                in self.xtable_spatial_dict.items()}
        self._mapped_spatial_dict = True

    def _results_new_scale(self, matrix, flow):
        self.fix_spatial_dictionaries()
        if flow is not None:
            try:
                row_index = self.biosphere_dict[flow]
                matrix = matrix[row_index, :]
            except KeyError:
                raise ValueError("Flow {} not in biosphere dict".format(flow))
        else:
            # using matrix.sum() converts to dense numpy matrix
            nc = matrix.shape[0]
            summer = csr_matrix((
                np.ones(nc),
                np.arange(nc),
                np.array((0, nc), dtype=int)
            ))
            matrix = summer * matrix
        return matrix

    def results_ia_spatial_scale(self):
        raise NotImplementedError("Must be defined in subclasses")

    def results_inv_spatial_scale(self):
        raise NotImplementedError("Must be defined in subclasses")
