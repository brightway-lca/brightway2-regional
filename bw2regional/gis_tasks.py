from .pandarus_remote import remote, PandarusRemote, AlreadyExists, run_job, extension_tables
from .pandarus import import_xt_from_rasterstats
from .meta import geocollections
try:
    import pandarus
except ImportError:
    pandarus = None


def raster_as_extension_table(vector, raster, name=None, engine=remote):
    if vector not in geocollections or raster not in geocollections:
        raise ValueError("Vector or raster not a valid geocollection")

    if name is None:
        name = vector + " - " + raster

    # if name in extension_tables:
    #     ?

    if isinstance(engine, PandarusRemote):
        print("Uploading data")
        try:
            engine.upload(vector)
        except AlreadyExists:
            pass

        try:
            engine.upload(raster)
        except AlreadyExists:
            pass

        print("Calculating raster statistics")
        run_job(engine.calculate_rasterstats(vector, raster))

        print("Creating Extension Table")
        return engine.rasterstats_as_xt(vector, raster, name)

    elif engine = 'local':
        if not pandarus:
            raise ImportError("`pandarus` library required for this function")

        vector_fp, vector_field = geocollections[vector]['filepath'], geocollections[vector]["field"]
        raster_fp, raster_band = geocollections[raster]['filepath'], geocollections[raster].get('band', 1)

        fp = pandarus.raster_statistics(vector_fp, vector_field, raster_fp, output=None, band=raster_band, compress=True)

        return import_xt_from_rasterstats(fp, name, vector)

    else:
        raise ValueError(f"Can't understand engine {engine}")


def geocollecton_from_intersection(first, second, name=None, engine=remote):
    if vector not in geocollections or raster not in geocollections:
        raise ValueError("Vector or raster not a valid geocollection")

    if name is None:
        name = vector + " - " + raster
