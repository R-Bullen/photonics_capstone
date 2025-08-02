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
from pteam_library_si_fab.components.ppc_unit.simulation.simulate_ppc_unit_linear_voltages import (
    simulate_ppc_unit_linear_voltages,
)
import pylab as plt
import numpy as np
import os

# Instantiate ppc unit
ppcunit = PPCUnit(
    wg_buffer_dx=10.0,
    two_arm_length_difference=0.0,
    bend_radius=50,
)
# Time domain simulation
# Sweep the voltage for single wavelength
results = simulate_ppc_unit_linear_voltages(cell=ppcunit, v_start=0.0, v_end=5.0, center_wavelength=1.55)
times = results.timesteps
signals = ["gnd", "ht", "optical_in", "out1", "out2"]
ylabels = ["voltage [V]", "voltage [V]", "power [W]", "power [W]", "power [W]"]
processes = [np.real, np.real, i3.signal_power, i3.signal_power, i3.signal_power]
# Simulation visualization
fig, axs = plt.subplots(nrows=len(signals), ncols=1, figsize=(6, 8))
for axes, signal, ylabel, process in zip(axs, signals, ylabels, processes):
    data = process(results[signal])
    axes.set_title(signal)
    axes.plot(times, data)
    axes.set_ylabel(ylabel)
    axes.set_xlabel("time [s]")
fig.savefig(os.path.join("{}.png".format("simulation_results_linear_volts")), bbox_inches="tight")
plt.show()
