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

sweep_name = "sweep_length"

results_array = []
lengths = np.linspace(500, 2500, 6)

for lps in lengths:
    print("Simulating for length {} um".format(lps))

    # Phase Shifter
    ps = pdk.PhaseShifterWaveguide(
        length=lps,
        core_width=0.45,
        rib_width=7.8,
        junction_offset=-0.1,
        n_width=3.9,
        p_width=4.1,
    )
    vpi_lpi = 1.2
    cl = 1.1e-15  # F/um
    res = 50
    tau = ps.length * cl * res
    ps.CircuitModel(vpi_lpi=vpi_lpi)

    # Modulator
    mzm = MZModulator(phaseshifter=ps)

    # Simulation
    results = simulate_modulation(
        cell=mzm,
        mod_amplitude=1.0,
        mod_noise=0.05,
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
    results_array.append(results)


def power(t):
    return np.abs(t) ** 2


outputs = ["sig", "revsig", "out"]
titles = ["Signal", "Reversed signal", "Output"]
ylabels = ["voltage [V]", "voltage [V]", "power [W]"]
process = [np.real, np.real, power]
fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(6, 6))

for ax, pr, out, title, ylabel in zip(axs, process, outputs, titles, ylabels):
    for length, results in zip(lengths, results_array):
        data = pr(results[out][1:])
        ax.set_title(title)
        ax.plot(results.timesteps[1:] * 1e9, data, label="length: {}".format(length))
        ax.set_xlabel("time [ns]")
        ax.set_ylabel(ylabel)
        if ax is axs[0]:
            ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)

plt.tight_layout()
fig.savefig(os.path.join("{}.png".format(sweep_name)), bbox_inches="tight")
plt.show()
plt.close(fig)
