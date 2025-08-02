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
from si_fab.components.modulator.mzm.simulation.simulate import simulate_modulation
from pteam_library_si_fab.components.mzm.pcell.cell import MZModulator
import pylab as plt
import numpy as np
import os

name = "simpler_simulation"
results_array = []

# Phase shifter
length = 1000.0
ps = pdk.PhaseShifterWaveguide(
    name="phaseshifter",
    length=length,
    core_width=0.45,
    rib_width=8.0,
    junction_offset=-0.1,
)

vpi_lpi = 1.2  # V.cm
cl = 1.1e-15  # F/um
res = 50  # Ohm
tau = ps.length * cl * res
ps.CircuitModel(vpi_lpi=vpi_lpi)

# Heater
heater = pdk.HeatedWaveguide(name="heater_bb")
heater.Layout(shape=[(0.0, 0.0), (100.0, 0.0)])

# Modulator
mzm = MZModulator(phaseshifter=ps, heater=heater)

# Simulation
results = simulate_modulation(
    cell=mzm,
    mod_amplitude=1.0,
    mod_noise=0.1,
    opt_amplitude=1.0,
    opt_noise=0.001,
    v_heater_1=0.0,
    v_heater_2=0.0,
    bitrate=5e9,
    n_bytes=20,
    steps_per_bit=50,
    center_wavelength=1.55,
    debug=False,
    seed=20,
)


def power(t):
    return np.abs(t) ** 2


outputs = ["sig", "revsig", "h1", "h2", "src_in", "out"]
titles = ["Signal", "Reversed signal", "Heater 1", "Heater 2", "Source input", "Output"]
ylabels = ["voltage [V]", "voltage [V]", "voltage [V]", "voltage [V]", "power [W]", "power [W]"]
process = [np.real, np.real, np.real, np.real, power, power]
fig, axs = plt.subplots(nrows=len(outputs), ncols=1, figsize=(6, 15))

for ax, pr, out, title, ylabel in zip(axs, process, outputs, titles, ylabels):
    data = pr(results[out][1:])
    ax.set_title(title)
    ax.plot(results.timesteps[1:] * 1e9, data, label="Length: {}".format(length))
    ax.set_xlabel("time [ns]")
    ax.set_ylabel(ylabel)

plt.tight_layout()
fig.savefig(os.path.join("{}.png".format(name)), bbox_inches="tight")
plt.show()
