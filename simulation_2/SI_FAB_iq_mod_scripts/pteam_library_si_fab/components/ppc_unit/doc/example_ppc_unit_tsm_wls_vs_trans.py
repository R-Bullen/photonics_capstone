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
from pteam_library_si_fab.components.ppc_unit.simulation.simulate_ppc_unit_single_voltages import (
    simulate_ppc_unit_single_voltages,
)
import pylab as plt
import numpy as np

# Instantiate ppc unit
ppcunit = PPCUnit(
    wg_buffer_dx=10.0,
    two_arm_length_difference=0.0,
    bend_radius=50,
)
# Simulation
v0 = 3.535  # bar:2.863V; coupler:3.535V; cross:4.10V
N = 20
# Sweep the wavelength for single voltage
wavelength = np.linspace(1.50, 1.6, N)
intensity1 = np.linspace(0, 0, N)
intensity2 = np.linspace(0, 0, N)
for m in range(N):
    results = simulate_ppc_unit_single_voltages(cell=ppcunit, volts=v0, center_wavelength=wavelength[m])
    res1 = (i3.signal_power(results["out1"][-1]),)
    res2 = (i3.signal_power(results["out2"][-1]),)
    intensity1[m] = np.float(res1[0])
    intensity2[m] = np.float(res2[0])
plt.plot(wavelength, intensity1, linewidth=2.0, label="out1 ")
plt.plot(wavelength, intensity2, linewidth=2.0, label="out2 ")
plt.xlabel("wavelengths (um)")
plt.ylabel("Output optical transmission")
plt.ylim(0, 1)
plt.legend()
plt.show()
