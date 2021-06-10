import numpy as np
from .. import units


def get_finite_inds(x):
    """
    Find indices of finite numbers.
    """
    return np.where(np.isfinite(x))[0]


def finmin(x):
    """
    Finite minimum.
    """
    return np.amin(x.take(get_finite_inds(x)))


def finmax(x):
    """
    Finite maximum.
    """
    return np.amax(x.take(get_finite_inds(x)))


def to_bin_centers(x):
    """
    Convert array edges to centers
    """
    return 0.5 * (x[1:] + x[:-1])


def to_bin_edges(x):
    """
    Convert array centers to edges
    """
    centers = to_bin_centers(x)
    left = centers[0] - (x[1] - x[0])
    right = centers[-1] + (x[-1] - x[-2])
    return np.concatenate(np.concatenate(left, centers), right)


def perpendicular_vector(v):
    """
    Compute a vector perpendicular to the input vector
    """

    # x = y = z = 0 is not an acceptable solution
    if v[0] == v[1] == v[2] == 0:
        raise ValueError("zero-vector")

    if v[2] == 0:
        return [-v[1], v[0], 0]
    else:
        return [1.0, 1.0, -1.0 * (v[0] + v[1]) / v[2]]


def value_to_string(val, precision=3):
    if (not isinstance(val, float)) or (val == 0):
        text = str(val)
    elif (abs(val) >= 10.0**(precision)) or \
         (abs(val) <= 10.0**(-precision)):
        text = "{val:.{prec}e}".format(val=val, prec=precision)
    else:
        text = "{}".format(val)
        if len(text) > precision + 2 + (text[0] == '-'):
            text = "{val:.{prec}f}".format(val=val, prec=precision)
    return text


def make_label(name=None, unit=None):
    lab = ""
    if name:
        lab += name
    if unit and unit != units.dimensionless:
        if name:
            lab += " "
        lab += "[{:~}]".format(unit)
    return lab.strip()