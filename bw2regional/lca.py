# -*- coding: utf-8 -*
from __future__ import division
from bw2calc.matrices import MatrixBuilder
from bw2calc.lca import LCA
import itertools
from .errors import UnprocessedDatabase
from bw2data import databases


class TwoSpatialScalesWithLoadingLCA(LCA):
    def __init__(self, *args, **kwargs):
        r"""Perform regionalized LCA calculation, matching the spatial scales of inventory and impact assessment, including emission-specific loading factors.

        The calculation formula is:

        .. math::

            h_{r} = \left[ \textbf{M }\left(\textbf{N} \circ \left[\textbf{G} \left( \textbf{L} \circ \textbf{R} \right) \right] \right) \right]^{T} \circ [ \textbf{B} \cdot (\textbf{A}^{-1}f) ]

        Uses sparse matrix `elementwise multiplication <http://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.multiply.html>`_.

        In addition to the normal LCA initialization steps, this class does the following:

            * Make sure that each inventory database has a set of ``geocollections`` in its metadata.

        """
        super(TwoSpatialScalesWithLoadingLCA, self).__init__(*args, **kwargs)
        self.inventory_geocollections = self.get_inventory_geocollections()

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
                names=self.databases,
                data_label="amount",
                row_id_label="activity",
                row_index_label="row",
                col_id_label="geo",
                col_index_label="col",
                row_dict=self.technosphere_dict,
            )
        return (inv_mapping, inv_spatial_dict, inv_mapping_matrix)

    def get_geo_transform_matrix(self, builder=MatrixBuilder):
        """Get geographic transform matrix **G**, which gives the intersecting areas of inventory and impact assessment spatial units. Rows are inventory spatial units, and columns are impact assessment spatial units.

        Uses ``self.inv_spatial_dict`` and ``self.ia_spatial_dict``.

        Returns:
            * ``geo_transform_params``: Parameter array with row/col of inventory and IA locations
            * ``geo_transform_matrix``: The matrix **G**

        """
        self.geo_transform_params, d, d, self.geo_transform_matrix = \
            builder.build(
                dirpath=self.dirpath,
                names=None,  # FIXME
                data_label="amount",
                row_id_label="geo_inv",
                row_index_label="row",
                col_id_label="geo_ia",
                col_index_label="col",
                row_dict=self.inv_spatial_dict,
                col_dict=self.ia_spatial_dict
            )

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
        """Get regionalized loading matrix, **L**, which gives location- and biosphere flow-specific background loading factors. Rows are impact assessment spatial units, and columns are biosphere flows.

        Uses ``self.inv_spatial_dict`` and ``self.ia_spatial_dict``.

        Returns:
            * ``loading_params``: Parameter array with row/col of IA locations/biosphere flows
            * ``loading_matrix``: The matrix **L**

        """
        loading_params, _, _, loading_matrix = \
            builder.build(
                dirpath=self.dirpath,
                names=None,  # FIXME
                data_label="amount",
                row_id_label="geo_inv",
                row_index_label="row",
                col_id_label="geo_ia",
                col_index_label="col",
                row_dict=self.inv_spatial_dict,
                col_dict=self.ia_spatial_dict
            )
        return (loading_params, loading_matrix)

    def load_lcia_data(self, builder=MatrixBuilder):
        self.inv_mapping_params, self.inv_spatial_dict, self.inv_mapping_matrix = \
            self.get_inventory_mapping_matrix(builder)
        self.reg_cf_params, self.ia_spatial_dict, self.reg_cf_matrix = \
            self.get_regionalized_characterization_matrix(builder)
        self.geo_transform_params, self.geo_transform_matrix = \
            self.get_geo_transform_matrix(builder)
        self.loading_params, self.loading_matrix = \
            self.get_loading_matrix(builder)
        self.normalization_matrix = self.build_normalization_matrix()

    def build_normalization_matrix(self):
        r"""Get normalization matrix. Values in row *i* and column *j* are defined by:

        .. math::
            L_{i,j} = \sum f(x())

        """
        nm = self.geo_transform_matrix * self.loading_matrix
        mask = nm.data != 0
        nm.data[mask] = 1 / nm.data[mask]
        return nm

    def lcia_calculation(self):
        """Do regionalized LCA calculation.

        Creates ``self.characterized_inventory``.

        """
        self.characterized_inventory = (self.inv_mapping_matrix * (
            self.normalization_matrix.multiply(self.geo_transform_matrix * (
            self.loading_matrix.multiply(self.reg_cf_matrix)
            )))).T * self.inventory

