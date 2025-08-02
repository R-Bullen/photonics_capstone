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
from si_fab.components.heater.simulation.simulate import get_current_density
from pteam_library_si_fab.components.mzm.pcell.cell import MZModulator
import pylab as plt
import numpy as np
import os

sweep_name = "sweep_heater"

# Phase Shifter
ps = pdk.PhaseShifterWaveguide(
    name="phaseshifter",
    length=1000.0,
    core_width=0.45,
    rib_width=7.8,
    junction_offset=-0.1,
    n_width=3.9,
    p_width=4.1,
)
vpi_lpi = 1.2  # V.cm
Cl = 1.1e-15  # F/um
R = 50  # Ohm
j_max = 0.05  # A/um2 maximum current density assumption

tau = ps.length * Cl * R
ps.CircuitModel(vpi_lpi=vpi_lpi)

# Heater
heater = pdk.HeatedWaveguide(name="heater_bb")
heater.Layout(shape=[(0.0, 0.0), (100.0, 0.0)])

# Modulator
mzm = MZModulator(phaseshifter=ps, heater=heater)

# Simulation
results_array = []
heater_voltages = np.linspace(0.0, 1.0, 6)

for v in heater_voltages:
    print("simulating for voltage {:.1f}".format(v))
    results = simulate_modulation(
        cell=mzm,
        mod_amplitude=1.0,
        mod_noise=0.05,
        opt_amplitude=1.0,
        opt_noise=0.001,
        v_heater_1=v,
        v_heater_2=0,
        bitrate=5e9,
        n_bytes=20,
        steps_per_bit=50,
        center_wavelength=1.5,
        debug=False,
        seed=20,
    )
    results_array.append(results)


def power(t):
    return np.abs(t) ** 2


outputs = ["sig", "revsig", "out", "src_in", "h1", "h2"]
titles = ["Signal", "Reversed signal", "Output", "Source input", "Heater 1", "Heater 2"]
ylabels = ["voltage [V]", "voltage [V]", "power [W]", "power [W]", "voltage [V]", "voltage [V]"]
process = [np.real, np.real, power, power, np.real, np.real]
fig, axs = plt.subplots(nrows=6, ncols=1, figsize=(6, 10))

for ax, pr, out, title, ylabel in zip(axs, process, outputs, titles, ylabels):
    for v, results in zip(heater_voltages, results_array):
        data = pr(results[out][1:])
        ax.set_title(title)
        ax.plot(results.timesteps[1:] * 1e9, data, label="vh: {:.1f}".format(v))
        ax.set_xlabel("time [ns]")
        ax.set_ylabel(ylabel)
        if ax is axs[0]:
            ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)

plt.tight_layout()
fig.savefig(os.path.join("{}.png".format(sweep_name)), bbox_inches="tight")
plt.show()

fig = plt.figure()
plt.plot(heater_voltages, get_current_density(cell=heater, v_bias=heater_voltages), label="Current density")
plt.title("Heater current density")
plt.xlabel("Heater voltage [V]")
plt.ylabel("Current density [A/um2]")
plt.axhline(y=j_max, label="Maximum current density")
fig.savefig(os.path.join("{}.png".format("current_density")), bbox_inches="tight")
plt.show()
