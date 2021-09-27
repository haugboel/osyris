# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2021 Osyris contributors (https://github.com/nvaytet/osyris)

import numpy as np
import os
from ..core import Array, Datagroup
from .. import config
from .reader import ReaderKind
from .. import units
from . import utils


class SinkReader:
    def __init__(self):
        self.kind = ReaderKind.SINK
        self.initialized = False

    def initialize(self, meta, select):
        sink_file = utils.generate_fname(meta["nout"],
                                         meta["path"],
                                         ftype="sink",
                                         cpuid=0,
                                         ext=".csv")
        if not os.path.exists(sink_file):
            return

        sink_data = np.loadtxt(sink_file, delimiter=',', skiprows=2)

        with open(sink_file, 'r') as f:
            key_list = f.readline()
            unit_combinations = f.readline()

        key_list = key_list.lstrip(' #').rstrip('\n').split(',')
        unit_combinations = unit_combinations.lstrip(' #').rstrip('\n').split(',')

        # Parse units
        unit_list = []
        for u in unit_combinations:
            m = meta['unit_d'] * meta['unit_l']**3 * units.g
            l = meta['unit_l'] * units.cm
            t = meta['unit_t'] * units.s
            if u == '1':
                unit_list.append(1.0 * units.dimensionless)
            else:
                unit_list.append(eval(u.replace(' ', '*')))

        sinks = Datagroup()
        for i, (key, unit) in enumerate(zip(key_list, unit_list)):
            sinks[key] = Array(values=sink_data[:, i] * unit.magnitude, unit=unit.units)
            if unit_combinations[i] == 'l':
                sinks[key] = sinks[key].to(meta["scale"])
        utils.make_vector_arrays(sinks, ndim=meta["ndim"])
        return sinks
