import numpy as np
import rasterio


def get_area(lat1, lat2, width):
    """Get area of a spherical quadrangle.

    lat1, lat2, and width should all be in degrees.

    Uses the formula derived and demonstrated in https://gis.stackexchange.com/questions/127165/more-accurate-way-to-calculate-area-of-rasters."""
    a = 6378137  # Meters
    b = 6356752.3142  # Meters
    to_radians = lambda x: x / 180 * np.pi

    e = 0.08181919084296  # e = sqrt(1 - (b/a)^2)

    width /= 360  # No wrap around from way rasters are defined

    def area(latitude):
        o = np.sin(to_radians(latitude))
        return (
            np.pi
            * b ** 2
            * (2 * np.arctanh(e * o) / (2 * e) + o / ((1 + e * o) * (1 - e * o)))
        )

    if lat1 >= 0 and lat2 <= 0:
        return width * (area(lat1) + area(lat2))
    else:
        return width * abs(area(lat1) - area(lat2))


def get_column_array(affine, rows, width):
    return np.array(
        [
            get_area(affine[5] + i * affine[4], affine[5] + (i + 1) * affine[4], width)
            for i in range(rows)
        ]
    ).reshape((1, -1, 1))


def divide_by_area(source_fp, destination_fp):
    """Create a new raster file at ``destination_fp``, dividing the values in ``source_fp`` by their cell's area.

    Will raise an error is the CRS is not geographic, or the raster is rotated."""
    with rasterio.open(source_fp) as src:
        meta = src.meta
        affine = src.transform
        rotated = affine[1] or affine[3]
        projected = "WGS 84" not in src.meta["crs"].wkt
        if rotated or projected:
            ERROR = """This function can't process projected or rotated rasters.
            Try https://geographiclib.sourceforge.io/html/python/interface.html"""
            raise ValueError(ERROR)

        areas = get_column_array(affine, src.height, abs(affine[0]))
        original = src.read()
        array = original / areas.astype(original.dtype)
        array[original == meta["nodata"]] = meta["nodata"]

        with rasterio.open(destination_fp, "w", **src.meta) as sink:
            for i, a in enumerate(array):
                sink.write(a, i + 1)
