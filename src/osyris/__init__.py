# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Osyris contributors (https://github.com/osyris-project/osyris)

""" Osyris: A Python package for the analysis of astrophysical simulations

   isort:skip_file
"""

import importlib.metadata

from .config import config
from .units import units
from .core import Array, Datagroup, Dataset, Plot, Vector, VectorBasis
from .io import RamsesDataset
from .plot import histogram1d, histogram2d, map, plot, scatter
from .spatial import (
    angular_momentum_vector,
    extract_box,
    extract_sphere,
    side_view,
    top_view,
)

try:
    __version__ = importlib.metadata.version(__package__ or __name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

del importlib

__all__ = [
    "Array",
    "Datagroup",
    "Dataset",
    "Plot",
    "Vector",
    "VectorBasis",
    "RamsesDataset",
    "config",
    "units",
    "histogram1d",
    "histogram2d",
    "scatter",
    "map",
    "plot",
    "angular_momentum_vector",
    "extract_box",
    "extract_sphere",
    "side_view",
    "top_view",
]
