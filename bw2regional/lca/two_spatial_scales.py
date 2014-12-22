# -*- coding: utf-8 -*
from __future__ import division
from .mixin import RegionalizationMixin
from bw2calc.lca import LCA
from bw2calc.matrices import MatrixBuilder
from bw2data import methods
from scipy.sparse import diags
import numpy as np


class TwoSpatialScalesLCA(LCA, RegionalizationMixin):
    def __init__(self, *args, **kwargs):
        r"""Perform regionalized LCA calculation, matching the spatial scales of inventory and impact assessment.

        The calculation formula is:

        .. math::

            h_{r} = \left[ \textbf{MNGR} \right]^{T} \circ [ \textbf{B} \cdot (\textbf{A}^{-1}f) ]

        Uses sparse matrix `elementwise multiplication <http://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.multiply.html>`_.

        In addition to the normal LCA initialization steps, this class does the following:

            * Make sure that each inventory database has a set of ``geocollections`` in its metadata.

        """
        super(TwoSpatialScalesLCA, self).__init__(*args, **kwargs)
        if self.method not in methods:
            raise ValueError("Must pass valid `method` name")
        self.inventory_geocollections = self.get_inventory_geocollections()
        self.ia_geocollections = self.get_ia_geocollections()

    def load_lcia_data(self, builder=MatrixBuilder):
        self.inv_mapping_params, self.inv_spatial_dict, self.inv_mapping_matrix = \
            self.get_inventory_mapping_matrix(builder)
        self.reg_cf_params, self.ia_spatial_dict, self.reg_cf_matrix = \
            self.get_regionalized_characterization_matrix(builder)
        self.geo_transform_params, self.geo_transform_matrix = \
            self.get_geo_transform_matrix(builder)
        self.normalization_matrix = self.build_normalization_matrix()

    def build_normalization_matrix(self):
        r"""Get normalization matrix, a diagonal matrix.

        .. math::
            \textbf{N}_{i,i} = \left[ \sum_{j} \left( \textbf{G} \right)_{i,j} \right]^{-1}

        """
        vector = np.array(self.geo_transform_matrix.sum(axis=1)).T
        mask = vector > 0
        vector[mask] = 1 / vector[mask]
        return diags(vector, [0], format='csr', dtype=np.float32)

    def lcia_calculation(self):
        """Do regionalized LCA calculation.

        Creates ``self.characterized_inventory``.

        """
        self.characterized_inventory = (
            self.inv_mapping_matrix   *
            self.normalization_matrix *
            self.geo_transform_matrix *
            self.reg_cf_matrix
            ).T.multiply(self.inventory)

    def results_ia_spatial_scale(self):
        if not hasattr(self, "characterized_inventory"):
            raise ValueError("Must do lcia calculation first")
        return self.reg_cf_matrix.T.multiply(
            self.inventory            *
            self.inv_mapping_matrix   *
            self.normalization_matrix *
            self.geo_transform_matrix)

    def results_inv_spatial_scale(self):
        if not hasattr(self, "characterized_inventory"):
            raise ValueError("Must do lcia calculation first")
        return (
            self.normalization_matrix *
            self.geo_transform_matrix *
            self.reg_cf_matrix).T.multiply(
            self.inventory            *
            self.inv_mapping_matrix)
