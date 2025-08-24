# Copyright (C) 2020-2024 Luceda Photonics

"""Simulate an MZ modulator working in OOK modulation format.

This script generates several outputs:
- visualize the layout in a matplotlib window (this pauses script execution)
- circuit simulation result (time-domain)
- Plot EyeDiagram
- Plot Constellation diagram
"""

import numpy as np
import matplotlib.pyplot as plt

import si_fab.all as pdk
from ipkiss3 import all as i3
from pteam_library_si_fab.components.mzm.pcell.cell import MZModulator
from simulation.simulate_mzm import simulate_modulation_mzm, result_modified_OOK

########################################################################################################################
# visualize the layout of MZM.
########################################################################################################################

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
vpi_lpi = 1.2  # V.cm
cl = 1.1e-16  # F/um
res = 25  # Ohm
tau = ps.length * cl * res  # Time constant associated with the modulator
ps.CircuitModel(vpi_lpi=vpi_lpi, tau=tau)

# heater
heater_length = 100
heater = pdk.HeatedWaveguide(name="heater")
heater.Layout(shape=[(0.0, 0.0), (heater_length, 0.0)])
heater_width = heater.heater_width * 2
p_pi_sq = heater.CircuitModel().p_pi_sq  # Power needed for a pi phase shift on a square [W]
V_half_pi = np.sqrt(
    np.pi / 2 * p_pi_sq * heater_length / (np.pi * heater_width)
)  # Voltage needed for a half pi phase shift
V_pi = np.sqrt(np.pi * p_pi_sq * heater_length / (np.pi * heater_width))  # Voltage needed for a pi phase shift

# MZModulator
mzm = MZModulator(
    phaseshifter=ps,
    heater=heater,
    rf_pad_width=75,
    rf_pad_length=100,
    rf_signal_width=5.0,
    rf_ground_width=20.0,
    rf_pitch_in=200,
)
mzm.Layout().visualize(show=False)

########################################################################################################################
# Simulation of a MZM working in OOK modulation format.
########################################################################################################################

results = simulate_modulation_mzm(
    cell=mzm,
    mod_amplitude=3.0,
    mod_noise=0.5,
    opt_amplitude=1.0,
    opt_noise=0.01,
    v_mzm1=0.0,  # MZM works at its linear biased point
    v_mzm2=0.0,
    bit_rate=50e9,
    n_bytes=2**8,
    steps_per_bit=2**7,
    center_wavelength=1.55,
)
outputs = ["sig", "revsig", "mzm1", "mzm2", "src_in", "out"]
titles = [
    "RF signal",
    "RF reversed signal",
    "Heater(bottom) electrical input",
    "Heater(top) electrical input",
    "Optical input",
    "Optical output",
]
ylabels = ["voltage [V]", "voltage [V]", "voltage [V]", "voltage [V]", "power [W]", "power [W]"]
process = [np.real, np.real, np.real, np.real, np.abs, np.abs]
fig, axs = plt.subplots(nrows=len(outputs), ncols=1, figsize=(6, 10))
for ax, pr, out, title, ylabel in zip(axs, process, outputs, titles, ylabels):
    data = pr(results[out][1:])
    ax.set_title(title)
    ax.plot(results.timesteps[1:] * 1e9, data, label="mzm")
    ax.set_xlabel("time [ns]")
    ax.set_ylabel(ylabel)
plt.tight_layout()

########################################################################################################################
# Plot EyeDiagram
########################################################################################################################

num_symbols = 2**8
samples_per_symbol = 2**7
data_stream = np.abs(results["out"]) ** 2
baud_rate = 50e9
time_step = 1.0 / (baud_rate * samples_per_symbol)
eye = i3.EyeDiagram(data_stream, baud_rate, time_step, resampling_rate=2, n_eyes=2, offset=0.2)
eye.visualize(show=False)

########################################################################################################################
# Plot Constellation diagram
########################################################################################################################

plt.figure(4)
res = result_modified_OOK(results)
plt.scatter(np.real(res), np.imag(res), marker="+", linewidths=10, alpha=0.1)
plt.grid()
plt.xlabel("real", fontsize=14)
plt.ylabel("imag", fontsize=14)
plt.title("Constellation diagram", fontsize=14)
plt.xlim([-1.0, 1.0])
plt.ylim([-1.0, 1.0])
plt.show()
