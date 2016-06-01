import numpy as np


def normalize_array(array, nodata=None):
    """Return ``array`` normalized to (0, 1).

    Applies log transform is values span multiple orders of magnitude."""
    # First, determine if log transform would help understand the data better
    # Look at difference between
    if nodata is not None:
        mask = array != nodata
    else:
        mask = np.ones(array.shape).astype(bool)
    copy = array[mask].ravel()
    copy.sort()
    top, bottom = copy[int(copy.shape[0] * 0.005)], copy[int(copy.shape[0] * 0.995)]
    if top / bottom > 100 and copy.min() >= 0:
        array[mask] = np.log(array[mask])

    # Then normalize the values
    # Set minimum value to 0
    array[mask] = array[mask] - array[mask].min()
    # Set maximum to 1
    array[mask] = array[mask] / array[mask].max()
    return array
