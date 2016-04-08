# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from ..errors import GeocollectionsMismatch
from .base_class import RegionalizationBase
from bw2calc.lca import LCA
from bw2calc.matrices import MatrixBuilder
from bw2data import methods, Method


class OneSpatialScaleLCA(RegionalizationBase):
    def __init__(self, *args, **kwargs):
        r"""Perform regionalized LCA calculation, where the inventory shares the same spatial scale as impact assessment.

        The calculation formula is:

        .. math::

            h_{r} = \left[ \textbf{MR} \right]^{T} \circ [ \textbf{B} \cdot (\textbf{A}^{-1}f) ]

        Uses sparse matrix `elementwise multiplication <http://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.multiply.html>`_.

        """
        super(OneSpatialScaleLCA, self).__init__(*args, **kwargs)
        if self.method not in methods:
            raise ValueError("Must pass valid `method` name")
        self.inventory_geocollections = self.get_inventory_geocollections()
        self.ia_geocollections = self.get_ia_geocollections()
        missing = self.ia_geocollections.difference(
            self.inventory_geocollections)
        if missing:
            raise GeocollectionsMismatch("{} geocollection(s) needed by IA method but not in inventory".format(missing))

    def get_regionalized_characterization_matrix(self, builder=MatrixBuilder):
        """Get regionalized characterization matrix, **R**, which gives location- and biosphere flow-specific characterization factors. Rows are inventory spatial units, and columns are biosphere flows.

        Uses ``self.inv_spatial_dict``, ``self._biosphere_dict`` and ``self.method``.

        Returns:
            * ``reg_cf_params``: Parameter array with row/col of IA locations/biosphere flows
            * ``reg_cf_matrix``: The matrix **R**

        """
        reg_cf_params, _, _, reg_cf_matrix = \
            builder.build(
                paths=[Method(self.method).filepath_processed()],
                data_label="amount",
                row_id_label="geo",
                row_index_label="row",
                col_id_label="flow",
                col_index_label="col",
                row_dict=self.inv_spatial_dict,
                col_dict=self._biosphere_dict,
            )
        return (reg_cf_params, reg_cf_matrix)

    def load_lcia_data(self, builder=MatrixBuilder):
        self.inv_mapping_params, self.inv_spatial_dict, self.inv_mapping_matrix = \
            self.get_inventory_mapping_matrix(builder)
        self.reg_cf_params, self.reg_cf_matrix = \
            self.get_regionalized_characterization_matrix(builder)

    def lcia_calculation(self):
        """Do regionalized LCA calculation.

        Creates ``self.characterized_inventory``.

        """
        self.characterized_inventory = (
            self.inv_mapping_matrix *
            self.reg_cf_matrix
            ).T.multiply(self.inventory)

    def results_ia_spatial_scale(self):
        raise NotImplementedError("No separate IA spatial scale")

    def results_inv_spatial_scale(self):
        if not hasattr(self, "characterized_inventory"):
            raise ValueError("Must do lcia calculation first")
        return self.reg_cf_matrix.T.multiply(
            self.inventory * self.inv_mapping_matrix
            )

