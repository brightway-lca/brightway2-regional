from bw2data import methods

from ..errors import GeocollectionsMismatch
from .base_class import RegionalizationBase


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
        missing = self.ia_geocollections.difference(self.inventory_geocollections)
        if missing:
            raise GeocollectionsMismatch(
                "{} geocollection(s) needed by IA method but not in inventory".format(
                    missing
                )
            )

    def load_lcia_data(self):
        self.create_inventory_mapping_matrix()
        self.create_regionalized_characterization_matrix(self.inv_mapping_mm.col_mapper)

    def lcia_calculation(self):
        """Do regionalized LCA calculation.

        Creates ``self.characterized_inventory``.

        """
        self.characterized_inventory = (
            self.inv_mapping_matrix * self.reg_cf_matrix
        ).T.multiply(self.inventory)

    def results_ia_spatial_scale(self):
        raise NotImplementedError("No separate IA spatial scale")

    def results_inv_spatial_scale(self):
        if not hasattr(self, "characterized_inventory"):
            raise ValueError("Must do lcia calculation first")
        return self.reg_cf_matrix.T.multiply(self.inventory * self.inv_mapping_matrix)
