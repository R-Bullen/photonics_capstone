
"""Simulate an MZ modulator working in OOK modulation format. This is mainly based on Luceda Academy example.

This script generates several outputs:
- visualize the layout in a matplotlib window (this pauses script execution)
- circuit simulation result (time-domain)
- Plot EyeDiagram
- Plot Constellation diagram
"""

import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3
from custom_components.iq_modulator_design import IQModulator
from simulation_2.iq_mod_scripts.simulation.simulate_iq_mod_QAM import simulate_modulation_QAM, result_modified_16QAM

import numpy as np
import matplotlib.pyplot as plt


########################################################################################################################
# Create a 1x1 MZM with a length difference between the two arms to set the biasing point
# by selecting the operating wavelength
########################################################################################################################

electrode_length = 8000
iq_mod = IQModulator(with_delays=True, delay_at_input=True)

lv = iq_mod.Layout(electrode_length=electrode_length, hot_width=50, electrode_gap=9)
#
# lv.visualize(annotate=True)

########################################################################################################################
# Find the operating wavelength so that the modulator is operating at the quadrature biasing point
########################################################################################################################

cm = iq_mod.CircuitModel()

wavelengths = np.linspace(1.55, 1.555, 101)
S = cm.get_smatrix(wavelengths=wavelengths)

idx_min = np.argmin(np.abs(np.abs(S['out', 'in'])**2))
idx_max = np.argmax(np.abs(np.abs(S['out', 'in'])**2))
wl = wavelengths[int((idx_min + idx_max) / 2)]
print("Quadrature wavelength: {}".format(wl))

# plt.figure()
# plt.plot(wavelengths * 1e3, np.abs(S['out', 'in'])**2)
# plt.plot([wl*1e3, wl*1e3], [0, 1])
# plt.plot(wavelengths * 1e3, [np.abs(S['out', 'in'][int((idx_min + idx_max) / 2)])**2 for x in wavelengths])
# plt.xlabel("Wavelength [nm]")
# plt.ylabel("Transmission [au]")
# plt.xlim([wavelengths[0] * 1e3, wavelengths[-1] * 1e3])
# plt.ylim(0, 1)
# plt.show()

########################################################################################################################
# Simulation of a MZM working in OOK modulation format.
########################################################################################################################

# Define modulator characteristics
# Voltage needed for a pi phase shift and half pi shift
rf_vpi = cm.vpi_l / 2 / (electrode_length / 10000)        # VpiL unit is V.cm; Dividing be 2 is due to push-pull configutation
V_half_pi = rf_vpi / 2
print("Modulator RF electrode Vpi: {} V".format(rf_vpi))

ps_vpi = 0.1 / (200/10000)
print("PS Vpi = %f" % ps_vpi)

cm.bandwidth = 100e9    # Modulator bandwidth (in Hz)

num_symbols = 2**7
samples_per_symbol = 2**7
bit_rate = 50e9

results = simulate_modulation_QAM(
    cell=iq_mod,
    mod_amplitude_i=rf_vpi*0.8,
    mod_noise_i=0.1,
    mod_amplitude_q=rf_vpi*0.8,
    mod_noise_q=0.1,
    opt_amplitude=2.0,
    opt_noise=0.01,
    v_heater_i=ps_vpi/2,  # The half pi phase shift implements orthogonal modulation
    v_heater_q=0.0,
    v_mzm_left1=ps_vpi/2,  # MZM (left) works at its Maximum transmission points
    v_mzm_left2=0.0,
    v_mzm_right1=ps_vpi/2,  # MZM (right) works at its Maximum transmission points
    v_mzm_right2=0.0,
    bit_rate=50e9,
    n_bytes=2**10,
    steps_per_bit=2**7,
    center_wavelength=1.55,
)
# outputs = ["sig", "mzm1", "mzm2", "src_in", "out"]
# titles = [
#     "RF signal",
#     "Heater(bottom) electrical input",
#     "Heater(top) electrical input",
#     "Optical input",
#     "Optical output",
# ]
#
# ylabels = ["voltage [V]", "voltage [V]", "voltage [V]", "amplitude [au]", "amplitude [au]"]
# process = [np.real, np.real, np.real, np.abs, np.abs]
outputs = ["sig_i", "sig_q", "src_in", "out"] #, "top_out", "bottom_out"]
titles = [
    "RF signal (top)",
    "RF signal (bottom)",
    "Optical input",
    "Optical output",
    # "Optical output (top)",
    # "Optical output (bottom)",
]
ylabels = ["voltage [V]", "voltage [V]", "amplitude [au]", "amplitude [au]"] #, "amplitude [au]", "amplitude [au]"]
process = [np.real, np.real, np.abs, np.real] #, np.real, np.real]

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

data_stream = np.abs(results["out"]) ** 2
time_step = 1.0 / (bit_rate * samples_per_symbol)
eye = i3.EyeDiagram(data_stream, bit_rate, time_step, resampling_rate=2, n_eyes=2, offset=0.2)
eye.visualize(show=False)

########################################################################################################################
# Plot Constellation diagram
########################################################################################################################

plt.figure(4)
res = result_modified_16QAM(results )
plt.scatter(np.real(res), np.imag(res), marker="+", linewidths=10, alpha=0.1)
plt.grid()
plt.xlabel("real", fontsize=14)
plt.ylabel("imag", fontsize=14)
plt.title("Constellation diagram", fontsize=14)
# plt.xlim([-1.0, 1.0])
# plt.ylim([-1.0, 1.0])
plt.show()
