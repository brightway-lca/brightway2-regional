# -*- coding: utf-8 -*
from __future__ import division
from ..loading import Loading
from ..meta import loadings
from .mixin import RegionalizationMixin
from bw2calc.lca import LCA
from bw2calc.matrices import MatrixBuilder
from bw2data import methods


class TwoSpatialScalesWithGenericLoadingLCA(LCA, RegionalizationMixin):
    def __init__(self, *args, **kwargs):
        r"""Perform regionalized LCA calculation, matching the spatial scales of inventory and impact assessment, including generic loading factors applied to all flows.

        The calculation formula is:

        .. math::

            h_{r} = \left[ \textbf{M}\left(\textbf{N} \circ \left[\textbf{GLR} \right] \right) \right]^{T} \circ [ \textbf{B} \cdot (\textbf{A}^{-1}f) ]

        Uses sparse matrix `elementwise multiplication <http://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.multiply.html>`_.

        In addition to the normal LCA initialization steps, this class does the following:

            * Make sure that each inventory database has a set of ``geocollections`` in its metadata.

        """
        try:
            loading_name = kwargs.pop("loading")
            assert loading_name in loadings
        except:
            raise ValueError("Must pass valid `loading` name")
        super(TwoSpatialScalesWithGenericLoadingLCA, self).__init__(*args, **kwargs)
        if self.method not in methods:
            raise ValueError("Must pass valid `method` name")
        self.loading = Loading(loading_name)
        self.inventory_geocollections = self.get_inventory_geocollections()
        self.ia_geocollections = self.get_ia_geocollections()

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
        r"""Get normalization matrix. Values in row *i* and column *e* are defined by:

        .. math::
            L_{i,e} = \left[ GL \right]_{i,e}^{-1}

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
            self.normalization_matrix.multiply(
                self.geo_transform_matrix * \
                self.loading_matrix * \
                self.reg_cf_matrix
                )
            )
        ).T * self.inventory
