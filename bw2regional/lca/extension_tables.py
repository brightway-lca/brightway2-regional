# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from eight import *

from ..errors import MissingIntersection
from ..intersection import Intersection
from ..meta import extension_tables, intersections
from ..utils import get_pandarus_map, filter_columns, filter_rows
from ..xtables import ExtensionTable
from .base_class import RegionalizationBase
from bw2calc.lca import LCA
from bw2calc.matrices import MatrixBuilder
from scipy.sparse import diags
import itertools
import numpy as np


class ExtensionTablesLCA(RegionalizationBase):
    def __init__(self, *args, **kwargs):
        r"""Perform regionalized LCA calculation, using biosphere flow- and activity-specific extension tables.

        The calculation formula is:

        .. math::

            h_{r} = \left[ \textbf{MN}_{dx} \textbf{DXN}_{g} \textbf{GR} \right]^{T} \circ [ \textbf{B} \cdot (\textbf{A}^{-1}f) ]

        Extension tables provide detailed information on the spatial pattern of occurrence for one, some, or all  activities, and one, some, or all of their environmental flows. In contrast with background loadings, which are on the spatial scale of impact assessment, extension tables provide data on a new spatial scale which is linked to inventory activities. This third spatial scale (inventory, impact assessment, and extension table) makes the calculation formula more complicated, and makes two normalization steps necessary.

        **Foo**

        **X** is the extension table mapping matrix, a diagonal matrix that indicates the relative importance of each extension table spatial unit. It has dimensions of *extension spatial scale* by *extension spatial scale*.

        :math:`N_{x}` is the extension

        **L** is the extension table

        The idea of extension tables is rather flexible, and this class supports limiting activities and flows with the ``limitations`` object:

        .. code-block:: python

            limitations = {
                'activities': list of activities to include/exclude,
                'activities mode': 'exclude',  # or 'include',
                'flows': list of flows to include/exclude,
                'flows mode': 'exclude',  # or 'include'

            }

        The ``limitations`` object can have activities, flows, or both. An ``exclude`` mode means that these activities or flows are removed from the regionalized matrices; an ``include`` mode means that only the specified activities and flows are kept. The default mode is ``include``.

        """
        try:
            xtable = kwargs.pop('xtable')
            limitations = kwargs.pop('limitations', {})
        except:
            raise ValueError("``xtable`` kwarg required")
        assert xtable in extension_tables
        super(ExtensionTablesLCA, self).__init__(*args, **kwargs)
        self.xtable = ExtensionTable(xtable)
        self.xtable_meta = extension_tables[xtable]
        self.limitations = limitations

        if 'activities mode' in self.limitations:
            if self.limitations['activities mode'] not in ('exclude, include'):
                raise ValueError("`activities mode` must be either `exclude` or `include`.")
        if 'flows mode' in self.limitations:
            if self.limitations['flows mode'] not in ('exclude, include'):
                raise ValueError("`flows mode` must be either `exclude` or `include`.")

        self.inventory_geocollections = self.get_inventory_geocollections()
        self.ia_geocollections = self.get_ia_geocollections()
        self.xtable_geocollections, self.xtable_intersections = self.get_xtable_geodata()

        self.inv_xtable_intersections = self.needed_inv_xtable_intersections()
        self.xtable_ia_intersections = self.needed_xtable_ia_intersections()
        self.check_geocollection_intersections()

    def needed_inv_xtable_intersections(self):
        return list(itertools.product(
            self.inventory_geocollections,
            self.xtable_geocollections
        ))

    def needed_xtable_ia_intersections(self):
        return list(itertools.product(
            self.xtable_geocollections,
            self.ia_geocollections
        ))

    def check_geocollection_intersections(self):
        missing_inv_xtable_inters = [
            x for x in self.inv_xtable_intersections
            if x not in intersections
        ]
        missing_xtable_ia_inters = [
            x for x in self.xtable_ia_intersections
            if x not in intersections
        ]
        if missing_inv_xtable_inters or missing_xtable_ia_inters:
            error_text = """
Some Intersection objects are required for this calculation, but were not found.

If you know these intersections are not needed, you can create empty intersections as follows:

    from bw2regional import create_empty_intersection
    create_empty_intersection(('missing', 'name'))

            """
            if missing_inv_xtable_inters:
                error_text += "Intersections between inventory and extension tables:"
                error_text += "\n\t".join([str(x)
                    for x in missing_inv_xtable_inters])
                error_text += "\n"
            if missing_xtable_ia_inters:
                error_text += "Intersections between extension tables and IA method:"
                error_text += "\n\t".join([str(x)
                    for x in missing_xtable_ia_inters])
            raise MissingIntersection(error_text)

    def get_xtable_geodata(self):
        gc = self.xtable_meta['geocollection']
        return (
            [gc],  # Only one geocollection per extension table, but need list
            {x for x in intersections if x[1] == gc}
        )

    def build_distribution_matrix(self):
        params, _, spatial_dict, matrix = \
            MatrixBuilder.build(
                paths=[Intersection(name).filepath_processed()
                       for name in self.inv_xtable_intersections],
                data_label="amount",
                row_id_label="geo_inv",
                row_index_label="row",
                col_id_label="geo_ia",
                col_index_label="col",
                row_dict=self.inv_spatial_dict,
            )
        return (params, spatial_dict, matrix)

    def load_xtable_matrix(self):
        params, _, _, matrix = MatrixBuilder.build(
            paths=[self.xtable.filepath_processed()],
            data_label="amount",
            row_id_label="geo",
            row_index_label="row",
            row_dict=self.xtable_spatial_dict,
            one_d=True
        )
        return params, matrix

    def build_distribution_normalization_matrix(self):
        r"""Get normalization matrix for inventory-xtable mapping. Normalizes to

        .. math::
            ( \textbf{N}_{dx} )_{i, i} = \left[ \sum_{j} \textbf{DX}_{i, j} \right]^{-1}

        """
        vector = np.array((
            self.distribution_matrix * self.xtable_matrix
            ).sum(axis=1)).T
        mask = vector > 0
        vector[mask] = 1 / vector[mask]
        return diags(vector, [0], format='csr', dtype=np.float32)

    def build_geo_transform_normalization_matrix(self):
        r"""Get normalization value for areas in each IA spatial unit:

        .. math::
            ( \textbf{N}_{g} )_{i, i} = \left[ \sum_{j} \textbf{G}_{i, j} \right]^{-1}

        """
        vector = np.array(self.geo_transform_matrix.sum(axis=1)).T
        mask = vector > 0
        vector[mask] = 1 / vector[mask]
        return diags(vector, [0], format='csr', dtype=np.float32)

    def get_geo_transform_matrix(self, builder=MatrixBuilder):
        geo_transform_params, _, _, geo_transform_matrix = \
            builder.build(
                paths=[
                    Intersection(name).filepath_processed()
                    for name in self.xtable_ia_intersections
                ],
                data_label="amount",
                row_id_label="geo_inv",
                row_index_label="row",
                col_id_label="geo_ia",
                col_index_label="col",
                row_dict=self.xtable_spatial_dict,
                col_dict=self.ia_spatial_dict,
            )
        return geo_transform_params, geo_transform_matrix

    def load_lcia_data(self, builder=MatrixBuilder):
        self.inv_mapping_params, self.inv_spatial_dict, \
            self.inv_mapping_matrix = \
            self.get_inventory_mapping_matrix()

        if 'activities' in self.limitations:
            self.inv_mapping_matrix = filter_rows(
                self.inv_mapping_matrix,
                [self.activity_dict[x] for x in self.limitations['activities']],
                exclude=self.limitations.get('activities mode', None) == 'exclude'
            )

        self.distribution_params, self.xtable_spatial_dict, \
            self.distribution_matrix = \
            self.build_distribution_matrix()
        self.xtable_params, self.xtable_matrix = self.load_xtable_matrix()
        self.distribution_normalization_matrix = \
            self.build_distribution_normalization_matrix()
        self.reg_cf_params, self.ia_spatial_dict, self.reg_cf_matrix = \
            self.get_regionalized_characterization_matrix(builder)

        if 'flows' in self.limitations:
            self.reg_cf_matrix = filter_columns(
                self.reg_cf_matrix,
                [self.biosphere_dict[x] for x in self.limitations['flows']],
                exclude=self.limitations.get('flows mode', None) == 'exclude'
            )

        self.geo_transform_params, self.geo_transform_matrix = \
            self.get_geo_transform_matrix(builder)
        self.geo_transform_normalization_matrix = self.build_geo_transform_normalization_matrix()

    def lcia_calculation(self):
        """Do regionalized LCA calculation.

        Creates ``self.characterized_inventory``.

        """
        self.characterized_inventory = (
            self.inv_mapping_matrix                 *
            self.distribution_normalization_matrix  *
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
            self.inv_mapping_matrix                 *
            self.distribution_normalization_matrix  *
            self.distribution_matrix                *
            self.xtable_matrix                      *
            self.geo_transform_normalization_matrix *
            self.geo_transform_matrix)

    def results_inv_spatial_scale(self):
        if not hasattr(self, "characterized_inventory"):
            raise ValueError("Must do lcia calculation first")
        return (
            self.distribution_normalization_matrix  *
            self.distribution_matrix                *
            self.xtable_matrix                      *
            self.geo_transform_normalization_matrix *
            self.geo_transform_matrix               *
            self.reg_cf_matrix).T.multiply(
            self.inventory                          *
            self.inv_mapping_matrix)

    def results_xtable_spatial_scale(self):
        if not hasattr(self, "characterized_inventory"):
            raise ValueError("Must do lcia calculation first")
        return (
            self.geo_transform_normalization_matrix *
            self.geo_transform_matrix               *
            self.reg_cf_matrix).T.multiply(
            self.inventory                          *
            self.inv_mapping_matrix                 *
            self.distribution_normalization_matrix  *
            self.distribution_matrix                *
            self.xtable_matrix)
