import os

from bw2data import geomapping
from bw2data.data_store import ProcessedDataStore

from .meta import loadings
from .utils import create_certain_datapackage
from .validate import loading_validator


class Loading(ProcessedDataStore):
    """ """

    _metadata = loadings
    validator = loading_validator
    matrix = "loading_matrix"

    def add_geomappings(self, data):
        """In theory, this shouldn't do anything, as all spatial units should be in defined by the method."""
        geomapping.add({obj[1] for obj in data})

    def process(self, **extra_metadata):
        data = self.load()
        create_certain_datapackage(
            [(geomapping[line[1]], 0) for line in data],
            [line[0] for line in data],
            self,
            **extra_metadata
        )

    @property
    def filename(self):
        return super(Loading, self).filename + ".loading"

    # def write_to_map(self, method, flow, geocollection=None):
    #     map_obj = get_pandarus_map(method, geocollection)
    #     data = {x[1][1]: x[0] for x in self.load()}
    #     if map_obj.raster:
    #         self._write_raster_loadings_to_map(map_obj, data)
    #     else:
    #         self._write_vector_loadings_to_map(map_obj, data)

    # def _write_raster_loadings_to_map(self, map_obj, data):
    #     NODATA = -9999.0
    #     filepath = os.path.join(projects.output_dir, self.filename + ".tiff")

    #     array = np.zeros(map_obj.file.array().shape) + NODATA
    #     for obj in map_obj:
    #         if obj["label"] in data:
    #             array[obj["row"], obj["col"]] = data[obj["label"]]

    #     map_obj.file.write_modified_array(filepath, array, nodata=NODATA)
    #     return filepath

    # def _write_vector_loadings_to_map(self, map_obj, data):
    #     raise NotImplementedError
