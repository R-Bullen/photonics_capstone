# Copyright (C) 2020 Luceda Photonics
# This version of Luceda Academy and related packages
# (hereafter referred to as Luceda Academy) is distributed under a proprietary License by Luceda
# It does allow you to develop and distribute add-ons or plug-ins, but does
# not allow redistribution of Luceda Academy  itself (in original or modified form).
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
#
# For the details of the licensing contract and the conditions under which
# you may use this software, we refer to the
# EULA which was distributed along with this program.
# It is located in the root of the distribution folder.

from si_fab import all as pdk
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

# Heater
heater = pdk.HeatedWaveguide(name="heater_bb")
heater.Layout(shape=[(0.0, 0.0), (100.0, 0.0)])

# Modulator
mzm = MZModulator(
    phaseshifter=ps,
    heater=heater,
    rf_pitch_in=150.0,
    rf_pitch_out=100.0,
    rf_pad_length=75,
    rf_signal_width=5.0,
    rf_ground_width=20.0,
)
mzm_lv = mzm.Layout()
mzm_lv.write_gdsii("mzm.gds")
