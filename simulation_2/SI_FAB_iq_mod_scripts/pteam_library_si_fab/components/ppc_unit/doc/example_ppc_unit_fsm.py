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
from ipkiss3 import all as i3
from pteam_library_si_fab.components.ppc_unit.pcell.cell import PPCUnit
import pylab as plt
import numpy as np

# Instantiate ppc unit
ppcunit = PPCUnit(
    wg_buffer_dx=10.0,
    two_arm_length_difference=0.0,
    bend_radius=50,
)
ppcunit.Layout().visualize(annotate=True)

# Frequency simulation visualization
wavelengths = np.linspace(1.5, 1.6, 101)
cm = ppcunit.CircuitModel()
S = cm.get_smatrix(wavelengths=wavelengths)
plt.plot(wavelengths, i3.signal_power(S["out1", "in1"]), label="out1")
plt.plot(wavelengths, i3.signal_power(S["out2", "in1"]), label="out2")
plt.legend()
plt.xlabel("Wavelengths [um]")
plt.ylabel("Output optical transmission")
plt.show()
