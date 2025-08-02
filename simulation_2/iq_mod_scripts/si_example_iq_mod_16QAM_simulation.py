# Copyright (C) 2020-2024 Luceda Photonics

"""Simulate an IQ modulator working in 16QAM modulation format.

This script generates several outputs:
- visualize the layout in a matplotlib window (this pauses script execution)
- circuit simulation result (time-domain)
- Plot EyeDiagram
- Plot Constellation diagram
"""

import numpy as np
import pylab as plt

import si_fab.all as pdk
from ipkiss3 import all as i3
from iqmodulator_designs import IQModulator
from pteam_library_si_fab.components.mzm.pcell.cell import MZModulator
from simulation.simulate_QAM import simulate_modulation_QAM, result_modified_16QAM

########################################################################################################################
# visualize the layout of IQ modulator.
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

# IQ Modulator
IQ_mod = IQModulator(mzm=mzm)
IQ_mod.Layout().visualize(show=False)

########################################################################################################################
# Simulation of a IQ modulator working in 16QAM modulation format.
########################################################################################################################

results = simulate_modulation_QAM(
    cell=IQ_mod,
    mod_amplitude_i=3.0,
    mod_noise_i=0.1,
    mod_amplitude_q=3.0,
    mod_noise_q=0.1,
    opt_amplitude=2.0,
    opt_noise=0.01,
    v_heater_i=V_half_pi,  # The half pi phase shift implements orthogonal modulation
    v_heater_q=0.0,
    v_mzm_left1=V_half_pi,  # MZM (left) works at its Maximum transmission points
    v_mzm_left2=0.0,
    v_mzm_right1=V_half_pi,  # MZM (right) works at its Maximum transmission points
    v_mzm_right2=0.0,
    bit_rate=50e9,
    n_bytes=2**10,
    steps_per_bit=2**7,
    center_wavelength=1.55,
)

outputs = ["sig_i", "revsig_i", "sig_q", "revsig_q", "ht_i", "ht_q", "src_in", "out"]
titles = [
    "RF signal_i",
    "RF reversed signal_i",
    "RF signal_q",
    "RF reversed signal_q",
    "Heater(left) electrical input",
    "Heater(right) electrical input",
    "Optical input",
    "Optical output",
]
ylabels = [
    "voltage [V]",
    "voltage [V]",
    "voltage [V]",
    "voltage [V]",
    "voltage [V]",
    "voltage [V]",
    "power [W]",
    "power [W]",
]
process = [np.real, np.real, np.real, np.real, np.real, np.real, np.abs, np.abs]
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

num_symbols = 2**10
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
res = result_modified_16QAM(results)
plt.scatter(np.real(res), np.imag(res), marker="+", linewidths=10, alpha=0.1)
plt.grid()
plt.xlabel("real", fontsize=14)
plt.ylabel("imag", fontsize=14)
plt.title("Constellation diagram", fontsize=14)
plt.xlim([-1.0, 1.0])
plt.ylim([-1.0, 1.0])
plt.show()
