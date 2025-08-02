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

import si_fab.all as pdk
from pteam_library_si_fab.all import MZI


coupler = pdk.SiDirectionalCouplerSPower(power_fraction=0.5)
phase_shifter = pdk.HeatedWaveguide()
phase_shifter.Layout(shape=[(0, 0), (100, 0)])

mzi = MZI(
    coupler=coupler,
    phase_shifter=phase_shifter,
    x_separation=10,
    extra_y_separation=25,
)

mzi_lv = mzi.Layout()
mzi_lv.visualize()
