import numpy as np
import pytest
from scipy.sparse import dok_matrix

from bw2regional.utils import filter_columns, filter_fiona_metadata, filter_rows


@pytest.fixture
def M():
    S = dok_matrix((3, 5))
    for i in range(5):
        S[0, i] = i
        S[1, i] = i / 2
    S[2, 0] = 100
    S[2, 2] = 200
    S[2, 4] = 400
    return S


def test_setup(M):
    expected = np.array(((0, 1, 2, 3, 4), (0, 0.5, 1, 1.5, 2), (100, 0, 200, 0, 400)))
    assert np.allclose(M.todense(), expected)


def test_filter_rows_inclusive(M):
    expected = np.array(((0, 1, 2, 3, 4), (0, 0, 0, 0, 0), (100, 0, 200, 0, 400)))
    assert np.allclose(filter_rows(M, [0, 2], False).todense(), expected)


def test_filter_rows_exclusive(M):
    expected = np.array(((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (100, 0, 200, 0, 400)))
    assert np.allclose(filter_rows(M, [0, 1]).todense(), expected)


def test_filter_columns_inclusive(M):
    expected = np.array(((0, 1, 0, 0, 4), (0, 0.5, 0, 0, 2), (100, 0, 0, 0, 400)))
    assert np.allclose(filter_columns(M, [0, 1, 4], False).todense(), expected)


def test_filter_columns_exclusive(M):
    expected = np.array(((0, 0, 2, 3, 4), (0, 0, 1, 1.5, 2), (0, 0, 200, 0, 400)))
    assert np.allclose(filter_columns(M, [0, 1]).todense(), expected)


def test_filter_fiona_metadata():
    given = {"crs": 1, "driver": 2, "description": 3, "filepath": 4}
    expected = {"crs": 1, "driver": 2}
    result = filter_fiona_metadata(given)
    assert result == expected
    assert result is not given
