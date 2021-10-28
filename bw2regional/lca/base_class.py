import itertools
from functools import partial

import matrix_utils as mu
import numpy as np
from bw2calc.lca import LCA
from bw2data import Database, Method, databases, methods
from scipy.sparse import csr_matrix

from ..errors import MissingIntersection, SiteGenericMethod, UnprocessedDatabase
from ..intersection import Intersection
from ..meta import intersections
from ..utils import dp


class RegionalizationBase(LCA):
    def __init__(self, demand, *args, **kwargs):
        super(RegionalizationBase, self).__init__(demand, *args, **kwargs)
        self.databases = set.union(
            *[Database(key[0]).find_graph_dependents() for key in demand]
        )

    def get_inventory_geocollections(self):
        """Get the set of all needed inventory geocollections.

        Raise UnprocessedDatabase if any database is missing the required metadata."""
        missing, present = [], set()
        for database in self.databases:
            if "geocollections" not in databases[database]:
                missing.append(database)
            else:
                present.update(set(databases[database]["geocollections"]))
        if missing:
            raise UnprocessedDatabase(
                "Database(s) {} don't specify their geocollections.".format(missing)
            )
        return present

    def get_ia_geocollections(self):
        """Retrieve the geocollections linked to the impact assessment method"""
        try:
            return set(methods[self.method]["geocollections"])
        except KeyError:
            raise SiteGenericMethod

    def create_inventory_mapping_matrix(self):
        """Get inventory mapping matrix, **M**, which maps inventory activities to inventory locations. Rows are inventory activities and columns are inventory spatial units.

        Uses ``self.technosphere_mm.row_mapper`` and ``self.databases``.

        Creates ``self.inv_mapping_mm``, ``self.inv_mapping_matrix``, and ``self.dicts.inv_spatial``/

        """
        self.inv_mapping_mm = mu.MappedMatrix(
            packages=[dp(Database(x).filepath_processed()) for x in self.databases],
            matrix="inv_geomapping_matrix",
            use_arrays=self.use_arrays,
            use_distributions=self.use_distributions,
            seed_override=self.seed_override,
            row_mapper=self.technosphere_mm.col_mapper,
        )
        self.inv_mapping_matrix = self.inv_mapping_mm.matrix
        self.dicts.inv_spatial = partial(self.inv_mapping_mm.col_mapper.to_dict)

    def needed_intersections(self):
        """Figure out which ``Intersection`` objects are needed bsed on ``self.inventory_geocollections`` and ``self.ia_geocollections``.

        Raise ``MissingIntersection`` if an intersection is required, but not available."""
        required = list(
            itertools.product(self.inventory_geocollections, self.ia_geocollections)
        )
        for obj in required:
            if obj not in intersections:
                raise MissingIntersection(
                    "Intersection {} needed but not found".format(obj)
                )
        return required

    def create_geo_transform_matrix(self):
        """Get geographic transform matrix **G**, which gives the intersecting areas of inventory and impact assessment spatial units. Rows are inventory spatial units, and columns are impact assessment spatial units.

        Uses ``self.inv_spatial_dict`` and ``self.ia_spatial_dict``.

        Returns:
            * ``geo_transform_params``: Parameter array with row/col of inventory and IA locations
            * ``geo_transform_matrix``: The matrix **G**

        """
        self.geo_transform_mm = mu.MappedMatrix(
            packages=[
                dp(Intersection(name).filepath_processed())
                for name in self.needed_intersections()
            ],
            matrix="intersection_matrix",
            use_arrays=self.use_arrays,
            use_distributions=self.use_distributions,
            seed_override=self.seed_override,
            col_mapper=self.reg_cf_mm.row_mapper,
            row_mapper=self.inv_mapping_mm.col_mapper,
        )
        self.geo_transform_matrix = self.geo_transform_mm.matrix

    def create_regionalized_characterization_matrix(self, row_mapper=None):
        """Get regionalized characterization matrix, **R**, which gives location- and biosphere flow-specific characterization factors.

        Rows are impact assessment spatial units, and columns are biosphere flows. However, we build it transverse and transpose it, as the characterization matrix indices are provided that way.

        Uses ``self._biosphere_dict`` and ``self.method``.

        Returns:
            * ``reg_cf_params``: Parameter array with row/col of IA locations/biosphere flows
            * ``ia_spatial_dict``: Dictionary linking impact assessment locations to matrix rows
            * ``reg_cf_matrix``: The matrix **R**

        """
        self.reg_cf_mm = mu.MappedMatrix(
            packages=[dp(Method(self.method).filepath_processed())],
            matrix="characterization_matrix",
            use_arrays=self.use_arrays,
            use_distributions=self.use_distributions,
            seed_override=self.seed_override,
            col_mapper=self.biosphere_mm.row_mapper,
            row_mapper=row_mapper,
            transpose=True,
        )
        self.reg_cf_matrix = self.reg_cf_mm.matrix
        if row_mapper is None:
            self.dicts.ia_spatial = partial(self.reg_cf_mm.row_mapper.to_dict)

    def create_loading_matrix(self):
        """Get diagonal regionalized loading matrix, **L**, which gives location-specific background loading factors. Dimensions are impact assessment spatial units.

        Uses ``self.dicts.ia_spatial``.

        """
        self.loading_mm = mu.MappedMatrix(
            packages=[dp(self.loading.filepath_processed())],
            matrix="loading_matrix",
            use_arrays=self.use_arrays,
            use_distributions=self.use_distributions,
            seed_override=self.seed_override,
            diagonal=True,
            row_mapper=self.reg_cf_mm.row_mapper,
        )
        self.loading_matrix = self.loading_mm.matrix

    # def fix_spatial_dictionaries(self):
    #     """Fix inventory and IA spatial dictionaries."""
    #     if not hasattr(self, "inv_spatial_dict"):
    #         # No LCIA performed yet
    #         return
    #     if getattr(self, "_mapped_spatial_dict", False):
    #         # Already reversed - should be idempotent
    #         return False
    #     rev_geomapping = {v: k for k, v in geomapping.items()}
    #     self.inv_spatial_dict = {
    #         rev_geomapping[k]: v for k, v in self.inv_spatial_dict.items()
    #     }
    #     if hasattr(self, "ia_spatial_dict"):
    #         self.ia_spatial_dict = {
    #             rev_geomapping[k]: v for k, v in self.ia_spatial_dict.items()
    #         }
    #     if hasattr(self, "xtable_spatial_dict"):
    #         self.xtable_spatial_dict = {
    #             rev_geomapping[k]: v for k, v in self.xtable_spatial_dict.items()
    #         }
    #     self._mapped_spatial_dict = True

    def _results_new_scale(self, matrix, flow):
        # self.fix_spatial_dictionaries()
        if flow is not None:
            try:
                row_index = self.biosphere_dict[flow]
                matrix = matrix[row_index, :]
            except KeyError:
                raise ValueError("Flow {} not in biosphere dict".format(flow))
        else:
            # using matrix.sum() converts to dense numpy matrix
            nc = matrix.shape[0]
            summer = csr_matrix(
                (np.ones(nc), np.arange(nc), np.array((0, nc), dtype=int))
            )
            matrix = summer * matrix
        return matrix

    def results_ia_spatial_scale(self):
        raise NotImplementedError("Must be defined in subclasses")

    def results_inv_spatial_scale(self):
        raise NotImplementedError("Must be defined in subclasses")
