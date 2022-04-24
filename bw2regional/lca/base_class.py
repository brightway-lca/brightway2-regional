import itertools
from functools import partial

import matrix_utils as mu
import numpy as np
from bw2calc.lca import LCA
from bw2data import Database, Method, databases, get_activity, methods
from scipy.sparse import coo_matrix, csr_matrix

from ..errors import MissingIntersection, SiteGenericMethod, UnprocessedDatabase
from ..export import create_geodataframe
from ..intersection import Intersection
from ..meta import intersections
from ..utils import dp


def get_dependent_databases(demand_dict):
    """Demand can be activitiy ids or tuple keys."""
    db_labels = [
        x[0] if isinstance(x, tuple) else get_activity(x)["database"]
        for x in demand_dict
    ]
    return set.union(*[Database(label).find_graph_dependents() for label in db_labels])


def annotate_flow(flow_id, _):
    flow = get_activity(id=flow_id)
    return {
        "flow_name": flow.get("name", ""),
        "flow_unit": flow.get("unit", ""),
        "flow_categories": str(flow.get("categories", "")),
    }


class RegionalizationBase(LCA):
    def __init__(self, demand, *args, **kwargs):
        self.databases = get_dependent_databases(demand)
        super(RegionalizationBase, self).__init__(demand, *args, **kwargs)

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
        ia_gc = set(methods[self.method]["geocollections"])
        if not ia_gc:
            raise SiteGenericMethod
        return ia_gc

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

    def __geodataframe(
        self, matrix, sum_flows, annotate_flows, col_dict, used_geocollections, cutoff
    ):
        if sum_flows:
            matrix = coo_matrix(matrix.sum(axis=0))
            annotate_flows = None
        elif annotate_flows:
            annotate_flows = annotate_flow

        return create_geodataframe(
            matrix=matrix,
            used_geocollections=used_geocollections,
            row_dict=self.dicts.biosphere,
            col_dict=col_dict,
            attribute_adder=annotate_flows,
            cutoff=cutoff,
        )

    def geodataframe_xtable_spatial_scale(
        self, sum_flows=True, annotate_flows=None, cutoff=None
    ):
        if not hasattr(self, "results_xtable_spatial_scale"):
            raise NotImplementedError

        matrix = self.results_xtable_spatial_scale()
        return self.__geodataframe(
            matrix=matrix,
            sum_flows=sum_flows,
            annotate_flows=annotate_flows,
            col_dict=self.dicts.xtable_spatial,
            used_geocollections=self.xtable_geocollections,
            cutoff=cutoff,
        )

    def geodataframe_ia_spatial_scale(
        self, sum_flows=True, annotate_flows=None, cutoff=None
    ):
        matrix = self.results_ia_spatial_scale()
        return self.__geodataframe(
            matrix=matrix,
            sum_flows=sum_flows,
            annotate_flows=annotate_flows,
            col_dict=self.dicts.ia_spatial,
            used_geocollections=self.ia_geocollections,
            cutoff=cutoff,
        )

    def geodataframe_inv_spatial_scale(
        self, sum_flows=True, annotate_flows=None, cutoff=None
    ):
        matrix = self.results_inv_spatial_scale()
        return self.__geodataframe(
            matrix=matrix,
            sum_flows=sum_flows,
            annotate_flows=annotate_flows,
            col_dict=self.dicts.inv_spatial,
            used_geocollections=self.inventory_geocollections,
            cutoff=cutoff,
        )
