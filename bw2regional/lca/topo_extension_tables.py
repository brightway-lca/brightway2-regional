# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from eight import *

from ..xtables import ExtensionTable
from .extension_tables import ExtensionTablesLCA
from bw2calc.matrices import MatrixBuilder
from bw2data import Database
from scipy.sparse import diags
import numpy as np


class TopologicalExtensionTablesLCA(ExtensionTablesLCA):
    """LCA class that handles intersections that work directly with topological face ids.

    This code is not recommended - please use the topological merging functions instead.

    """

    def __init__(self, *args, **kwargs):
        super(TopologicalExtensionTablesLCA, self).__init__(*args, **kwargs)

    def needed_inv_xtable_intersections(self):
        return [('ecoinvent-topology', obj) for obj in self.xtable_geocollections]

    def get_inventory_mapping_matrix(self, builder=MatrixBuilder):
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

    def build_topo_normalization_matrix(self):
        r"""Get normalization matrix for inventory-xtable mapping. Normalizes to

        .. math::
            ( \textbf{N}_{t} )_{i, i} = \left[ \sum_{j} \textbf{MDX}_{i, j} \right]^{-1}

        """
        vector = np.array((
            self.inv_mapping_matrix *
            self.distribution_matrix     *
            self.xtable_matrix
        ).sum(axis=1)).T
        mask = vector > 0
        vector[mask] = 1 / vector[mask]
        return diags(vector, [0], format='csr', dtype=np.float32)

    def load_lcia_data(self, builder=MatrixBuilder):
        self.inv_mapping_params, self.inv_spatial_dict, \
            self.inv_mapping_matrix = \
            self.get_inventory_mapping_matrix()
        self.distribution_params, self.xtable_spatial_dict, \
            self.distribution_matrix = \
            self.build_distribution_matrix()
        self.xtable_params, self.xtable_matrix = self.load_xtable_matrix()
        self.topo_normalization_matrix = \
            self.build_topo_normalization_matrix()
        self.reg_cf_params, self.ia_spatial_dict, self.reg_cf_matrix = \
            self.get_regionalized_characterization_matrix(builder)
        self.geo_transform_params, self.geo_transform_matrix = \
            self.get_geo_transform_matrix(builder)
        self.geo_transform_normalization_matrix = self.build_geo_transform_normalization_matrix()

    def lcia_calculation(self):
        """Do regionalized LCA calculation.

        Creates ``self.characterized_inventory``.

        """
        self.characterized_inventory = (
            self.topo_normalization_matrix  *
            self.inv_mapping_matrix                 *
            self.distribution_matrix                *
            self.xtable_matrix                      *
            self.geo_transform_normalization_matrix *
            self.geo_transform_matrix               *
            self.reg_cf_matrix
            ).T.multiply(self.inventory)

    def results_ia_spatial_scale(self):
        if not hasattr(self, "characterized_inventory"):
            raise ValueError("Must do lcia calculation first")
        return self.reg_cf_matrix.T.multiply(
            self.inventory                          *
            self.topo_normalization_matrix  *
            self.inv_mapping_matrix                 *
            self.distribution_matrix                *
            self.xtable_matrix                      *
            self.geo_transform_normalization_matrix *
            self.geo_transform_matrix)

    def results_inv_spatial_scale(self):
        raise NotImplemented

    def results_xtable_spatial_scale(self):
        if not hasattr(self, "characterized_inventory"):
            raise ValueError("Must do lcia calculation first")
        return (
            self.geo_transform_normalization_matrix *
            self.geo_transform_matrix               *
            self.reg_cf_matrix).T.multiply(
            self.inventory                          *
            self.topo_normalization_matrix          *
            self.inv_mapping_matrix                 *
            self.distribution_matrix                *
            self.xtable_matrix)
