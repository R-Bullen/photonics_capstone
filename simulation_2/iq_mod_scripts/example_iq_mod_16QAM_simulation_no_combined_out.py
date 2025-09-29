
"""Simulate an MZ modulator working in OOK modulation format. This is mainly based on Luceda Academy example.

This script generates several outputs:
- visualize the layout in a matplotlib window (this pauses script execution)
- circuit simulation result (time-domain)
- Plot EyeDiagram
- Plot Constellation diagram
"""

import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3
from custom_components.iq_modulator2_design_no_combined_output import IQModulator
from simulation_2.iq_mod_scripts.simulation.simulate_iq_mod_16QAM_no_combiner import simulate_modulation_16QAM, result_modified_16QAM

import numpy as np
import matplotlib.pyplot as plt

########################################################################################################################
# Create a 1x1 MZM with a length difference between the two arms to set the biasing point 
# by selecting the operating wavelength
########################################################################################################################

electrode_length = 8000
iq_mod = IQModulator(with_delays=True, delay_at_input=True)

lv = iq_mod.Layout(electrode_length=electrode_length, hot_width=50, electrode_gap=9)
lv.visualize(annotate=True)

########################################################################################################################
# Find the operating wavelength so that the modulator is operating at the quadrature biasing point
########################################################################################################################

cm = iq_mod.CircuitModel()

wavelengths = np.linspace(1.55, 1.555, 101)
S = cm.get_smatrix(wavelengths=wavelengths)

idx_min = np.argmin(np.abs(np.abs(S['top_out', 'in'])**2))
idx_max = np.argmax(np.abs(np.abs(S['top_out', 'in'])**2))
wl = wavelengths[int((idx_min + idx_max) / 2)]
print("Quadrature wavelength: {}".format(wl))

wl = wavelengths[int(idx_min)]
print("Min transmission wavelength: {}".format(wl))

plt.figure()
plt.plot(wavelengths * 1e3, np.abs(S['top_out', 'in'])**2)
plt.plot([wl*1e3, wl*1e3], [0, 1])
# plt.plot(wavelengths * 1e3, [np.abs(S['top_out', 'in'][int((idx_min + idx_max) / 2)])**2 for x in wavelengths])
plt.plot(wavelengths * 1e3, [np.abs(S['top_out', 'in'][int(idx_min)])**2 for x in wavelengths])
plt.xlabel("Wavelength [nm]")
plt.ylabel("Transmission [au]")
plt.xlim([wavelengths[0] * 1e3, wavelengths[-1] * 1e3])
plt.ylim(0, 1)
plt.show()

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

num_symbols = 2**10
samples_per_symbol = 2**7
bit_rate = 50e9

results = simulate_modulation_16QAM(
    cell=iq_mod,
    mod_amplitude_i=rf_vpi,
    mod_noise_i=0.0,
    mod_amplitude_q=rf_vpi,
    mod_noise_q=0.0,
    opt_amplitude=1.0,
    opt_noise=0.0,

    # Output Heaters
    v_heater_i=0.0,
    v_heater_q=ps_vpi/2,

    # WG Heaters
    v_mzm_left1=ps_vpi,    # Top Arm - Top PS
    v_mzm_left2=0.0,    # Top Arm - Bottom PS
    v_mzm_right1=ps_vpi,   # Bottom Arm - Top PS
    v_mzm_right2=0.0,   # Bottom Arm - Bottom PS

    bit_rate=50e9,
    n_bytes=num_symbols,
    steps_per_bit=samples_per_symbol,
    center_wavelength=float(wl),
)

outputs = ["sig_i", "sig_q","src_in", "top_out", "bottom_out"]
titles = [
    "RF signal_i",
    "RF signal_q",
    "Optical input",
    "Optical output_i",
    "Optical output_q",
]
ylabels = [
    "voltage [V]",
    "voltage [V]",
    "power [W]",
    "power [W]",
    "power [W]",
]
process = [np.real, np.real, np.abs, np.abs, np.abs]
fig, axs = plt.subplots(nrows=len(outputs), ncols=1, figsize=(6, 10))

for ax, pr, out, title, ylabel in zip(axs, process, outputs, titles, ylabels):
    data = pr(results[out][1:])
    ax.set_title(title)
    ax.plot(results.timesteps[1:] * 1e9, data, label="iq_mod")
    ax.set_xlabel("time [ns]")
    ax.set_ylabel(ylabel)
plt.tight_layout()

########################################################################################################################
# Plot EyeDiagram
########################################################################################################################

data_stream_top = np.abs(results["top_out"]) ** 2
data_stream_bottom = np.abs(results["bottom_out"]) ** 2

time_step = 1.0 / (bit_rate * samples_per_symbol)

eye_top = i3.EyeDiagram(data_stream_top, bit_rate, time_step, resampling_rate=2, n_eyes=2, offset=0.2)
eye_top.visualize(show=False, title="Top Eye Diagram")
eye_bottom = i3.EyeDiagram(data_stream_bottom, bit_rate, time_step, resampling_rate=2, n_eyes=2, offset=0.2)
eye_bottom.visualize(show=False, title="Bottom Eye Diagram")

########################################################################################################################
# Plot Constellation diagram
########################################################################################################################

plt.figure(4)
res_top = result_modified_16QAM(results, "top_out", samples_per_symbol=samples_per_symbol, sampling_point=0.8)
res_bottom = result_modified_16QAM(results, "bottom_out", samples_per_symbol=samples_per_symbol, sampling_point=0.8)
plt.subplot(1,2,1)
plt.scatter(np.real(res_top), np.imag(res_top), marker="+", linewidths=10, alpha=0.1)
plt.grid()
plt.xlabel("real", fontsize=14)
plt.ylabel("imag", fontsize=14)
plt.title("(Top) Constellation diagram", fontsize=14)
plt.xlim([-1.0, 1.0])
plt.ylim([-1.0, 1.0])

plt.subplot(1,2,2)
plt.scatter(np.real(res_bottom), np.imag(res_top), marker="+", linewidths=10, alpha=0.1)
plt.grid()
plt.xlabel("real", fontsize=14)
plt.ylabel("imag", fontsize=14)
plt.title("(Bottom) Constellation diagram", fontsize=14)
plt.xlim([-1.0, 1.0])
plt.ylim([-1.0, 1.0])
plt.show()
