# -*- coding: utf-8 -*
from __future__ import division
from ..errors import UnprocessedDatabase, SiteGenericMethod, MissingIntersection
from ..intersection import Intersection
from ..meta import intersections
from bw2calc.matrices import MatrixBuilder
from bw2data import databases, methods, geomapping
import itertools


class RegionalizationMixin(object):
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

        Uses ``self.technosphere_dict`` and ``self.databases``.

        Returns:
            * ``inv_mapping_params``: Parameter array with row/col of inventory activities/locations
            * ``inv_spatial_dict``: Dictionary linking inventory locations to matrix columns
            * ``inv_mapping_matrix``: The matrix **M**

        """
        inv_mapping_params, _, inv_spatial_dict, inv_mapping_matrix = \
            builder.build(
                dirpath=self.dirpath,
                names=[x + u".geomapping" for x in self.databases],
                data_label="amount",
                row_id_label="activity",
                row_index_label="row",
                col_id_label="geo",
                col_index_label="col",
                row_dict=self.technosphere_dict,
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
                dirpath=self.dirpath,
                names=[
                    Intersection(name).filename
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

        Uses ``self.biosphere_dict`` and ``self.method``.

        Returns:
            * ``reg_cf_params``: Parameter array with row/col of IA locations/biosphere flows
            * ``ia_spatial_dict``: Dictionary linking impact assessment locations to matrix rows
            * ``reg_cf_matrix``: The matrix **R**

        """
        reg_cf_params, _, ia_spatial_dict, reg_cf_matrix = \
            builder.build(
                dirpath=self.dirpath,
                names=[methods[self.method]['abbreviation']],
                data_label="amount",
                row_id_label="flow",
                row_index_label="row",
                col_id_label="geo",
                col_index_label="col",
                row_dict=self.biosphere_dict,
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
                dirpath=self.dirpath,
                names=[self.loading.filename],
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
        if not isinstance(self.inv_spatial_dict.keys()[0], int):
            # Already reversed
            return
        rev_geomapping = {v: k for k, v in geomapping.iteritems()}
        self.inv_spatial_dict = {rev_geomapping[k]: v for k, v in self.inv_spatial_dict.iteritems()}
        self.ia_spatial_dict = {rev_geomapping[k]: v for k, v in self.ia_spatial_dict.iteritems()}
