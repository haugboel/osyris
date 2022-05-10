# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Osyris contributors (https://github.com/osyris-project/osyris)
from common import arrayclose, arraytrue
from osyris import Array, units
from copy import copy, deepcopy
import numpy as np
from pint.errors import DimensionalityError
import pytest


def test_constructor():
    a = np.arange(100.)
    array = Array(values=a, unit='m')
    assert array.unit == units('m')
    assert len(array) == len(a)
    assert array.shape == a.shape
    assert np.allclose(array.values, a)


def test_equal():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = Array(values=[1., 2., 3., 4., 5.], unit='m')
    c = Array(values=[100., 200., 300., 400., 500.], unit='cm')
    assert arraytrue(a == b)
    assert arraytrue(a == c)


def test_not_equal():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = Array(values=[1., 2., 3., 4., 5.], unit='cm')
    c = Array(values=[100., 200., 300., 400., 500.], unit='m')
    d = Array(values=[1.1, 2., 3., 4., 5.], unit='m')
    assert arraytrue(a != b)
    assert arraytrue(a != c)
    assert all((a != d).values == [True, False, False, False, False])


def test_addition():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = Array(values=[6., 7., 8., 9., 10.], unit='m')
    expected = Array(values=[7., 9., 11., 13., 15.], unit='m')
    assert arrayclose(a + b, expected)


def test_addition_bad_units():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = Array(values=[6., 7., 8., 9., 10.], unit='s')
    with pytest.raises(DimensionalityError):
        _ = a + b
    with pytest.raises(TypeError):
        _ = a + 3.0


def test_addition_quantity():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = 3.5 * units('m')
    expected = Array(values=[4.5, 5.5, 6.5, 7.5, 8.5], unit='m')
    assert arrayclose(a + b, expected)


def test_addition_inplace():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = Array(values=[6., 7., 8., 9., 10.], unit='m')
    expected = Array(values=[7., 9., 11., 13., 15.], unit='m')
    a += b
    assert arrayclose(a, expected)


def test_addition_quantity_inplace():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = 3.5 * units('m')
    expected = Array(values=[4.5, 5.5, 6.5, 7.5, 8.5], unit='m')
    a += b
    assert arrayclose(a, expected)


def test_subtraction():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = Array(values=[6., 7., 8., 9., 10.], unit='m')
    expected = Array(values=[5., 5., 5., 5., 5.], unit='m')
    assert arrayclose(b - a, expected)


def test_subtraction_bad_units():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = Array(values=[6., 7., 8., 9., 10.], unit='s')
    with pytest.raises(DimensionalityError):
        _ = a - b
    with pytest.raises(TypeError):
        _ = a - 3.0


def test_subtraction_quantity():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = 3.5 * units('m')
    expected = Array(values=[-2.5, -1.5, -0.5, 0.5, 1.5], unit='m')
    assert arrayclose(a - b, expected)


def test_subtraction_inplace():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = Array(values=[6., 7., 8., 9., 10.], unit='m')
    expected = Array(values=[5., 5., 5., 5., 5.], unit='m')
    b -= a
    assert arrayclose(b, expected)


def test_subtraction_quantity_inplace():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = 3.5 * units('m')
    expected = Array(values=[-2.5, -1.5, -0.5, 0.5, 1.5], unit='m')
    a -= b
    assert arrayclose(a, expected)


def test_multiplication():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = Array(values=[6., 7., 8., 9., 10.], unit='m')
    expected = Array(values=[6., 14., 24., 36., 50.], unit='m*m')
    assert arrayclose(a * b, expected)


def test_multiplication_float():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = 3.0
    expected = Array(values=[3., 6., 9., 12., 15.], unit='m')
    assert arrayclose(a * b, expected)
    assert arrayclose(b * a, expected)


def test_multiplication_ndarray():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = np.arange(5.)
    expected = Array(values=[0., 2., 6., 12., 20.], unit='m')
    assert arrayclose(a * b, expected)
    assert arrayclose(b * a, expected)


def test_multiplication_quantity():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = 3.5 * units('s')
    expected = Array(values=[3.5, 7.0, 10.5, 14.0, 17.5], unit='m*s')
    assert arrayclose(a * b, expected)


def test_multiplication_inplace():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = Array(values=[6., 7., 8., 9., 10.], unit='m')
    expected = Array(values=[6., 14., 24., 36., 50.], unit='m*m')
    a *= b
    assert arrayclose(a, expected)


def test_multiplication_float_inplace():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = 3.0
    expected = Array(values=[3., 6., 9., 12., 15.], unit='m')
    a *= b
    assert arrayclose(a, expected)


def test_multiplication_ndarray_inplace():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = np.arange(5.)
    expected = Array(values=[0., 2., 6., 12., 20.], unit='m')
    a *= b
    assert arrayclose(a, expected)


def test_multiplication_quantity_inplace():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = 3.5 * units('s')
    expected = Array(values=[3.5, 7.0, 10.5, 14.0, 17.5], unit='m*s')
    a *= b
    assert arrayclose(a, expected)


def test_division():
    a = Array(values=[1., 2., 3., 4., 5.], unit='s')
    b = Array(values=[6., 7., 8., 9., 10.], unit='m')
    expected = Array(values=[6., 3.5, 8. / 3., 2.25, 2.], unit='m/s')
    assert arrayclose(b / a, expected)


def test_division_float():
    a = Array(values=[1., 2., 3., 4., 5.], unit='s')
    b = 3.0
    expected = Array(values=[1. / 3., 2. / 3., 1., 4. / 3., 5. / 3.], unit='s')
    assert arrayclose(a / b, expected)
    expected = Array(values=[3., 3. / 2., 1., 3. / 4., 3. / 5.], unit='1/s')
    assert arrayclose(b / a, expected)


def test_division_ndarray():
    a = Array(values=[1., 2., 3., 4., 5.], unit='s')
    b = np.arange(5., 10.)
    expected = Array(values=[1. / 5., 2. / 6., 3. / 7., 4. / 8., 5. / 9.], unit='s')
    assert arrayclose(a / b, expected)
    # expected = Array(values=[3., 3. / 2., 1., 3. / 4., 3. / 5.], unit='1/s')
    # assert arrayclose(b / a, expected)


def test_division_quantity():
    a = Array(values=[0., 2., 4., 6., 200.], unit='s')
    b = 2.0 * units('s')
    expected = Array(values=[0., 1., 2., 3., 100.], unit='dimensionless')
    assert arrayclose(a / b, expected)


def test_division_inplace():
    a = Array(values=[1., 2., 3., 4., 5.], unit='s')
    b = Array(values=[6., 7., 8., 9., 10.], unit='m')
    expected = Array(values=[6., 3.5, 8. / 3., 2.25, 2.], unit='m/s')
    b /= a
    assert arrayclose(b, expected)


def test_division_float_inplace():
    a = Array(values=[1., 2., 3., 4., 5.], unit='s')
    b = 3.0
    expected = Array(values=[1. / 3., 2. / 3., 1., 4. / 3., 5. / 3.], unit='s')
    a /= b
    assert arrayclose(a, expected)


def test_division_ndarray_inplace():
    a = Array(values=[1., 2., 3., 4., 5.], unit='s')
    b = np.arange(5., 10.)
    expected = Array(values=[1. / 5., 2. / 6., 3. / 7., 4. / 8., 5. / 9.], unit='s')
    a /= b
    assert arrayclose(a, expected)
    # expected = Array(values=[3., 3. / 2., 1., 3. / 4., 3. / 5.], unit='1/s')
    # assert arrayclose(b / a, expected)


def test_division_quantity_inplace():
    a = Array(values=[0., 2., 4., 6., 200.], unit='s')
    b = 2.0 * units('s')
    expected = Array(values=[0., 1., 2., 3., 100.], unit='dimensionless')
    a /= b
    assert arrayclose(a, expected)


def test_norm():
    a2d = Array(values=np.array([[1., 2.], [3., 4.], [5., 6.], [7., 8.]]), unit='s')
    a3d = Array(values=np.array([[1., 2., 3.], [4., 5., 6.]]), unit='g')
    assert arrayclose(a2d.norm, Array(values=np.sqrt([5., 25., 61., 113.]), unit='s'))
    assert arrayclose(a3d.norm, Array(values=np.sqrt([14., 77.]), unit='g'))


# def test_broadcast():
#     a1d = Array(values=np.array([1., 2., 3., 4., 5.]), unit='s')
#     a3d = Array(values=np.array([[1., 2., 3.], [4., 5., 6.], [7., 8., 9.],
#                                  [10., 11., 12.], [13., 14., 15.]]),
#                 unit='g')
#     expected = Array(values=np.array([[1., 2., 3.], [8., 10., 12.], [21., 24., 27.],
#                                       [40., 44., 48.], [65., 70., 75.]]),
#                      unit='g*s')
#     assert arrayclose(a1d * a3d, expected)


def test_power():
    a = Array(values=[1., 2., 4., 6., 200.], unit='s')
    expected = Array(values=[1., 8., 64., 216., 8.0e6], unit='s**3')
    assert arrayclose(a**3, expected)


def test_negative():
    a = Array(values=[1., 2., 4., 6., 200.], unit='s')
    expected = Array(values=[-1., -2., -4., -6., -200.], unit='s')
    assert arrayequal(-a, expected)


def test_less_than():
    a = Array(values=[1., 2., 3., 4., 5.], unit='s')
    b = Array(values=[6., 7., 1., 4., 10.], unit='s')
    expected = [True, True, False, False, True]
    assert all((a < b).values == expected)


def test_less_than_conversion():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = Array(values=[600., 700., 100., 400., 1000.], unit='cm')
    expected = [True, True, False, False, True]
    assert all((a < b).values == expected)


def test_less_than_bad_units():
    a = Array(values=[1., 2., 3., 4., 5.], unit='s')
    b = Array(values=[6., 7., 1., 4., 10.], unit='m')
    with pytest.raises(DimensionalityError):
        _ = a < b


def test_less_equal():
    a = Array(values=[1., 2., 3., 4., 5.], unit='s')
    b = Array(values=[6., 7., 1., 4., 10.], unit='s')
    expected = [True, True, False, True, True]
    assert all((a <= b).values == expected)


def test_less_equal_bad_units():
    a = Array(values=[1., 2., 3., 4., 5.], unit='s')
    b = Array(values=[6., 7., 1., 4., 10.], unit='m')
    with pytest.raises(DimensionalityError):
        _ = a <= b


def test_greater_than():
    a = Array(values=[1., 2., 3., 4., 5.], unit='s')
    b = Array(values=[6., 7., 1., 4., 10.], unit='s')
    expected = [True, True, False, False, True]
    assert all((b > a).values == expected)


def test_greater_than_bad_units():
    a = Array(values=[1., 2., 3., 4., 5.], unit='s')
    b = Array(values=[6., 7., 1., 4., 10.], unit='K')
    with pytest.raises(DimensionalityError):
        _ = b > a


def test_greater_equal():
    a = Array(values=[1., 2., 3., 4., 5.], unit='s')
    b = Array(values=[6., 7., 1., 4., 10.], unit='s')
    expected = [True, True, False, True, True]
    assert all((b >= a).values == expected)


def test_greater_equal_bad_units():
    a = Array(values=[1., 2., 3., 4., 5.], unit='s')
    b = Array(values=[6., 7., 1., 4., 10.], unit='K')
    with pytest.raises(DimensionalityError):
        _ = b >= a


def test_to():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    b = Array(values=[1.0e-3, 2.0e-3, 3.0e-3, 4.0e-3, 5.0e-3], unit='km')
    assert arrayclose(a.to('km'), b)
    assert a.unit.units == units('m')


def test_to_bad_units():
    a = Array(values=[1., 2., 3., 4., 5.], unit='m')
    with pytest.raises(DimensionalityError):
        _ = a.to('s')


def test_min():
    a = Array(values=[1., -2., 3., 0.4, 0.5, 0.6], unit='m')
    assert (a.min() == Array(values=-2., unit='m')).values
    b = Array(values=np.array([1., -2., 3., 0.4, 0.5, 0.6]).reshape(2, 3), unit='m')
    assert (b.min() == Array(values=-2., unit='m')).values


def test_max():
    a = Array(values=[1., 2., 3., -15., 5., 6.], unit='m')
    assert (a.max() == Array(values=6.0, unit='m')).values
    b = Array(values=np.array([1., 2., 3., -15., 5., 6.]).reshape(2, 3), unit='m')
    assert (b.max() == Array(values=6.0, unit='m')).values


def test_reshape():
    a = Array(values=[1., 2., 3., 4., 5., 6.], unit='m')
    expected = Array(values=[[1., 2., 3.], [4., 5., 6.]], unit='m')
    assert arraytrue(np.ravel(a.reshape(2, 3) == expected))


def test_slicing():
    a = Array(values=[11., 12., 13., 14., 15.], unit='m')
    assert a[2] == Array(values=[13.], unit='m')
    assert arraytrue(a[:4] == Array(values=[11., 12., 13., 14.], unit='m'))
    assert arraytrue(a[2:4] == Array(values=[13., 14.], unit='m'))


def test_slicing_vector():
    a = Array(values=np.arange(12.).reshape(4, 3), unit='m')
    assert arraytrue(np.ravel(a[2:3] == Array(values=[[6., 7., 8.]], unit='m')))
    assert a[2:3].shape == (1, 3)
    assert arraytrue(
        np.ravel(a[:2] == Array(values=[[0., 1., 2.], [3., 4., 5.]], unit='m')))


def test_copy():
    a = Array(values=[11., 12., 13., 14., 15.], unit='m')
    b = a.copy()
    a *= 10.
    assert arraytrue(b == Array(values=[11., 12., 13., 14., 15.], unit='m'))


def test_copy_overload():
    a = Array(values=[11., 12., 13., 14., 15.], unit='m')
    b = copy(a)
    a *= 10.
    assert arraytrue(b == Array(values=[11., 12., 13., 14., 15.], unit='m'))


def test_deepcopy():
    a = Array(values=[11., 12., 13., 14., 15.], unit='m')
    b = deepcopy(a)
    a *= 10.
    assert arraytrue(b == Array(values=[11., 12., 13., 14., 15.], unit='m'))


def test_numpy_unary():
    values = [1., 2., 3., 4., 5.]
    a = Array(values=values, unit='m')
    expected = np.log10(values)
    result = np.log10(a)
    assert np.allclose(result.values, expected)
    assert result.unit == units('m')


def test_numpy_sqrt():
    values = [1., 2., 3., 4., 5.]
    a = Array(values=values, unit='m*m')
    expected = np.sqrt(values)
    result = np.sqrt(a)
    assert np.allclose(result.values, expected)
    assert result.unit == units('m')


def test_numpy_binary():
    a_buf = [1., 2., 3., 4., 5.]
    b_buf = [6., 7., 8., 9., 10.]
    a = Array(values=a_buf, unit='m')
    b = Array(values=b_buf, unit='m')
    expected = np.dot(a_buf, b_buf)
    result = np.dot(a, b)
    assert result.values == expected
    assert result.unit == units('m')


def test_numpy_iterable():
    a_buf = [1., 2., 3., 4., 5.]
    b_buf = [6., 7., 8., 9., 10.]
    a = Array(values=a_buf, unit='m')
    b = Array(values=b_buf, unit='m')
    expected = np.concatenate([a_buf, b_buf])
    result = np.concatenate(a, b)
    assert np.array_equal(result.values, expected)
    assert result.unit == units('m')
