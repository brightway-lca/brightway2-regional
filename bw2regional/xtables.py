# -*- coding: utf-8 -*
from .meta import extension_tables, geocollections
from .validate import xtable_validator
from .loading import Loading
from .utils import get_pandarus_map


class ExtensionTable(Loading):
    metadata = extension_tables
    validator = xtable_validator

    @property
    def filename(self):
        return super(ExtensionTable, self).filename.replace(".loading", ".xtable")

    def write_to_map(self, *args, **kwargs):
        raise NotImplementedError

    def import_from_map(self):
        geocollection = extension_tables[self.name].get('geocollection')
        xt_field = extension_tables[self.name].get('xt_field')
        band = extension_tables[self.name].get('band')

        # TODO: Handle raster bands here

        if not geocollection:
            raise ValueError("No geocollection for this extension table")

        map_obj = get_pandarus_map(geocollection)
        data = []

        if map_obj.vector:
            if xt_field is None:
                raise ValueError("No `xt_field` field name specified")

            id_field = geocollections[geocollection].get('field')
            if not id_field:
                raise ValueError("Geocollection must specify ``field`` field name for unique feature ids")

        for feature in map_obj:
            if map_obj.vector:
                label = feature['properties'][id_field]
                value = float(feature['properties'][xt_field])
            else:
                label = feature['label']
                value = feature['value']
            data.append((value, (geocollection, label)))

        self.write(data)
        self.process()
