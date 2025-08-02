# Copyright (C) 2020-2024 Luceda Photonics

"""Instantiate an IQ modulator and packages.

This script generates several outputs:
- visualize the layout in a matplotlib window (this pauses script execution)
- write to GDSII (IQ_mod_packaged.gds)
"""

import si_fab.all as pdk
from iqmodulator_designs import IQModulator, PackagedIQModulator
from pteam_library_si_fab.components.mzm.pcell.cell import MZModulator

# Phase Shifter
ps = pdk.PhaseShifterWaveguide(
    name="phaseshifter",
    length=1000.0,
    core_width=0.45,
    rib_width=7.8,
    junction_offset=-0.1,
    p_width=4.1,
    n_width=3.9,
)

# Phase Shifter (heater)
heater = pdk.HeatedWaveguide(name="heater")
heater.Layout(shape=[(0.0, 0.0), (100.0, 0.0)])

# MZModulator
mzm = MZModulator(
    phaseshifter=ps,
    heater=heater,
    rf_pad_width=75,
    rf_pad_length=350,
    rf_signal_width=5.0,
    rf_ground_width=20.0,
    rf_pitch_in=200,
)
# mzm.Layout().visualize(annotate=True)

# IQ Modulator
IQ_mod = IQModulator(mzm=mzm)
IQ_mod.Layout().visualize(annotate=True)


# Packaged IQ modulator
IQ_mod_packaged = PackagedIQModulator(
    dut=IQ_mod,
)
IQ_mod_packaged.Layout().visualize()
IQ_mod_packaged.Layout().write_gdsii("IQ_mod_packaged.gds")
