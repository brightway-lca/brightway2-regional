import itertools

import numpy as np
from scipy.sparse import diags
import matrix_utils as mu
from functools import partial

from ..errors import MissingIntersection
from ..intersection import Intersection
from ..meta import extension_tables, intersections
from ..utils import filter_columns, filter_rows, dp
from ..xtables import ExtensionTable
from .base_class import RegionalizationBase


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
            xtable = kwargs.pop("xtable")
            limitations = kwargs.pop("limitations", {})
        except KeyError:
            raise ValueError("``xtable`` kwarg required")
        assert xtable in extension_tables
        super(ExtensionTablesLCA, self).__init__(*args, **kwargs)
        self.xtable = ExtensionTable(xtable)
        self.xtable_meta = extension_tables[xtable]
        self.limitations = limitations

        if "activities mode" in self.limitations:
            if self.limitations["activities mode"] not in ("exclude, include"):
                raise ValueError(
                    "`activities mode` must be either `exclude` or `include`."
                )
        if "flows mode" in self.limitations:
            if self.limitations["flows mode"] not in ("exclude, include"):
                raise ValueError("`flows mode` must be either `exclude` or `include`.")

        self.inventory_geocollections = self.get_inventory_geocollections()
        self.ia_geocollections = self.get_ia_geocollections()
        (
            self.xtable_geocollections,
            self.xtable_intersections,
        ) = self.get_xtable_geodata()

        self.inv_xtable_intersections = self.needed_inv_xtable_intersections()
        self.xtable_ia_intersections = self.needed_xtable_ia_intersections()
        self.check_geocollection_intersections()

    def needed_inv_xtable_intersections(self):
        return list(
            itertools.product(self.inventory_geocollections, self.xtable_geocollections)
        )

    def needed_xtable_ia_intersections(self):
        return list(
            itertools.product(self.xtable_geocollections, self.ia_geocollections)
        )

    def check_geocollection_intersections(self):
        missing_inv_xtable_inters = [
            x for x in self.inv_xtable_intersections if x not in intersections
        ]
        missing_xtable_ia_inters = [
            x for x in self.xtable_ia_intersections if x not in intersections
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
                error_text += "\n\t".join([str(x) for x in missing_inv_xtable_inters])
                error_text += "\n"
            if missing_xtable_ia_inters:
                error_text += "Intersections between extension tables and IA method:"
                error_text += "\n\t".join([str(x) for x in missing_xtable_ia_inters])
            raise MissingIntersection(error_text)

    def get_xtable_geodata(self):
        gc = self.xtable_meta["geocollection"]
        return (
            [gc],  # Only one geocollection per extension table, but need list
            {x for x in intersections if x[1] == gc},
        )

    def create_distribution_matrix(self):
        """Get distribution matrix, **D**, which provides the area of inventory spatial units in each extension table spatial unit. Rows are inventory spatial units and columns are extension table spatial units."""
        self.distribution_mm = mu.MappedMatrix(
            packages=[
                dp(Intersection(name).filepath_processed())
                for name in self.inv_xtable_intersections
            ],
            matrix="intersection_matrix",
            use_arrays=self.use_arrays,
            use_distributions=self.use_distributions,
            seed_override=self.seed_override,
            row_mapper=self.inv_mapping_mm.col_mapper,
        )
        self.distribution_matrix = self.distribution_mm.matrix
        self.dicts.xtable_spatial = partial(self.distribution_mm.col_mapper.to_dict)

    def create_xtable_matrix(self):
        """Diagonal extension table matrix that indicates the extension table density value in each extension table spatial unit."""
        self.xtable_mm = mu.MappedMatrix(
            packages=[dp(self.xtable.filepath_processed())],
            matrix="xtable_matrix",
            use_arrays=self.use_arrays,
            use_distributions=self.use_distributions,
            seed_override=self.seed_override,
            diagonal=True,
            row_mapper=self.distribution_mm.col_mapper,
        )
        self.xtable_matrix = self.xtable_mm.matrix

    def build_distribution_normalization_matrix(self):
        r"""Get normalization matrix for inventory-xtable mapping. Normalizes to

        .. math::
            ( \textbf{N}_{dx} )_{i, i} = \left[ \sum_{j} \textbf{DX}_{i, j} \right]^{-1}

        """
        vector = np.array((self.distribution_matrix * self.xtable_matrix).sum(axis=1)).T
        mask = vector > 0
        vector[mask] = 1 / vector[mask]
        return diags(vector, [0], format="csr", dtype=np.float32)

    def build_geo_transform_normalization_matrix(self):
        r"""Get normalization value for areas in each IA spatial unit:

        .. math::
            ( \textbf{N}_{g} )_{i, i} = \left[ \sum_{j} \textbf{G}_{i, j} \right]^{-1}

        """
        vector = np.array(self.geo_transform_matrix.sum(axis=1)).T
        mask = vector > 0
        vector[mask] = 1 / vector[mask]
        return diags(vector, [0], format="csr", dtype=np.float32)

    def create_geo_transform_matrix(self):
        self.geo_transform_mm = mu.MappedMatrix(
            packages=[
                dp(Intersection(name).filepath_processed())
                for name in self.xtable_ia_intersections
            ],
            matrix="intersection_matrix",
            use_arrays=self.use_arrays,
            use_distributions=self.use_distributions,
            seed_override=self.seed_override,
            col_mapper=self.reg_cf_matrix.row_mapper,
            row_mapper=self.distribution_mm.col_mapper,
        )
        self.geo_transform_matrix = self.geo_transform_mm.matrix

    def load_lcia_data(self):
        self.create_inventory_mapping_matrix()

        if "activities" in self.limitations:
            self.inv_mapping_matrix = self.inv_mapping_mm.matrix = filter_rows(
                self.inv_mapping_matrix,
                [self.dicts.activity[x] for x in self.limitations["activities"]],
                exclude=self.limitations.get("activities mode", None) == "exclude",
            )

        self.create_distribution_matrix()
        self.create_xtable_matrix()
        self.distribution_normalization_matrix = (
            self.build_distribution_normalization_matrix()
        )
        self.create_regionalized_characterization_matrix()

        if "flows" in self.limitations:
            self.reg_cf_matrix = self.reg_cf_mm.matrix = filter_columns(
                self.reg_cf_matrix,
                [self.dicts.biosphere[x] for x in self.limitations["flows"]],
                exclude=self.limitations.get("flows mode", None) == "exclude",
            )

        self.create_geo_transform_matrix()
        self.geo_transform_normalization_matrix = (
            self.build_geo_transform_normalization_matrix()
        )

    def lcia_calculation(self):
        """Do regionalized LCA calculation.

        Creates ``self.characterized_inventory``.

        """
        self.characterized_inventory = (
            self.inv_mapping_matrix
            * self.distribution_normalization_matrix
            * self.distribution_matrix
            * self.xtable_matrix
            * self.geo_transform_normalization_matrix
            * self.geo_transform_matrix
            * self.reg_cf_matrix
        ).T.multiply(self.inventory)

    def results_ia_spatial_scale(self):
        if not hasattr(self, "characterized_inventory"):
            raise ValueError("Must do lcia calculation first")
        return self.reg_cf_matrix.T.multiply(
            self.inventory
            * self.inv_mapping_matrix
            * self.distribution_normalization_matrix
            * self.distribution_matrix
            * self.xtable_matrix
            * self.geo_transform_normalization_matrix
            * self.geo_transform_matrix
        )

    def results_inv_spatial_scale(self):
        if not hasattr(self, "characterized_inventory"):
            raise ValueError("Must do lcia calculation first")
        return (
            self.distribution_normalization_matrix
            * self.distribution_matrix
            * self.xtable_matrix
            * self.geo_transform_normalization_matrix
            * self.geo_transform_matrix
            * self.reg_cf_matrix
        ).T.multiply(self.inventory * self.inv_mapping_matrix)

    def results_xtable_spatial_scale(self):
        if not hasattr(self, "characterized_inventory"):
            raise ValueError("Must do lcia calculation first")
        return (
            self.geo_transform_normalization_matrix
            * self.geo_transform_matrix
            * self.reg_cf_matrix
        ).T.multiply(
            self.inventory
            * self.inv_mapping_matrix
            * self.distribution_normalization_matrix
            * self.distribution_matrix
            * self.xtable_matrix
        )
