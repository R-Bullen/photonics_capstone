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

# Instantiate ppc unit
ppcunit = PPCUnit(
    wg_buffer_dx=10.0,
    two_arm_length_difference=0.0,
    bend_radius=50,
)
ppcunit.Layout().visualize(annotate=True)

# Time simulation
v0 = 3.535  # bar:2.863V; coupler:3.535V; cross:4.10V
res = simulate_ppc_unit_single_voltages(cell=ppcunit, volts=v0, center_wavelength=1.55)
# print(type(res))
for cnt in range(2):
    plt.plot(res.timesteps * 1e9, i3.signal_power(res["out{}".format(cnt + 1)]), label="out{}".format(cnt + 1))

plt.xlabel("Time (ns)")
plt.ylabel("Output optical transmission")
plt.ylim(0, 1)
plt.legend()
plt.show()
