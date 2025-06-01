
"""Simulate an MZ modulator working in BPSK modulation format. This is mainly based on Luceda Academy example.

This script generates several outputs:
- visualize the layout in a matplotlib window (this pauses script execution)
- circuit simulation result (time-domain)
- Plot EyeDiagram
- Plot Constellation diagram
"""

import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3
from simulation.sim_functions.simulate_mzm import simulate_modulation_mzm, result_modified_BPSK
import numpy as np
import matplotlib.pyplot as plt


########################################################################################################################
# Create a 1x1 MZM with a length difference between the two arms to set the biasing point 
# by selecting the operating wavelength
########################################################################################################################

electrode_length = 8000
mzm = asp.MZModulator1x1(with_delays=True, delay_at_input=False)

lv = mzm.Layout(electrode_length=electrode_length, hot_width=50, electrode_gap=9)

lv.visualize(annotate=True)

########################################################################################################################
# Find the operating wavelength so that the modulator is operating at the minimum transmission point
########################################################################################################################
cm = mzm.CircuitModel()

wavelengths = np.linspace(1.55, 1.555, 101)
S = cm.get_smatrix(wavelengths=wavelengths)

idx_min = np.argmin(np.abs(np.abs(S['out', 'in'])**2))
wl = wavelengths[idx_min]
print("Minimum transmission wavelength: {}".format(wl))

plt.figure()
plt.plot(wavelengths * 1e3, np.abs(S['out', 'in'])**2)
plt.plot([wl*1e3, wl*1e3], [0, 1])
plt.plot(wavelengths * 1e3, [np.abs(S['out', 'in'][idx_min])**2 for x in wavelengths])
plt.xlabel("Wavelength [nm]")
plt.ylabel("Transmission [au]")
plt.xlim([wavelengths[0] * 1e3, wavelengths[-1] * 1e3])
plt.ylim(0, 1)
plt.show()
 
########################################################################################################################
# Simulation of a MZM working in BPSK modulation format.
########################################################################################################################

# Define modulator characteristics
rf_vpi = cm.vpi_l / 2 / (electrode_length / 10000)       # VpiL unit is V.cm; Dividing be 2 is due to push-pull configutation
print("Modulator RF electrode Vpi: {} V".format(rf_vpi))

cm.bandwidth = 50e9    # Modulator bandwidth (in Hz)

results = simulate_modulation_mzm(
    cell=mzm,
    mod_amplitude=rf_vpi/2,
    mod_noise=0.01,
    opt_amplitude=1.0,
    opt_noise=0.01,
    v_mzm1= 0,  
    v_mzm2=0, 
    bit_rate=50e9,
    n_bytes=2**8,
    steps_per_bit=2**7,
    center_wavelength=wl,
)

outputs = ["sig", "mzm1", "mzm2", "src_in", "out"]
titles = [
    "RF signal",
    "Heater(bottom) electrical input",
    "Heater(top) electrical input",
    "Optical input",
    "Optical output",
]
ylabels = ["voltage [V]", "voltage [V]", "voltage [V]", "amplitude [au]", "amplitude [au]"]
process = [np.real, np.real, np.real, np.abs, np.real]
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
res = result_modified_BPSK(results)
plt.scatter(np.real(res), np.imag(res), marker="+", linewidths=10, alpha=0.1)
plt.grid()
plt.xlabel("real", fontsize=14)
plt.ylabel("imag", fontsize=14)
plt.title("Constellation diagram", fontsize=14)
plt.xlim([-1.0, 1.0])
plt.ylim([-1.0, 1.0])
plt.show()
