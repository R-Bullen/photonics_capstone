
"""Simulate an MZ modulator working in OOK modulation format. This is mainly based on Luceda Academy example.

This script generates several outputs:
- visualize the layout in a matplotlib window (this pauses script execution)
- circuit simulation result (time-domain)
- Plot EyeDiagram
- Plot Constellation diagram
"""

import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3
from simulation.simulate_mzm import simulate_modulation_mzm, result_modified_OOK
import numpy as np
import matplotlib.pyplot as plt


########################################################################################################################
# Create a 1x1 MZM with a length difference between the two arms to set the biasing point
# by selecting the operating wavelength
########################################################################################################################

electrode_length = 8000
# mzm = asp.MZModulator1x1(with_delays=True, delay_at_input=False)
mzm = asp.MZModulator1x1(with_delays=False, delay_at_input=False)

lv = mzm.Layout(electrode_length=electrode_length, hot_width=50, electrode_gap=9)

lv.visualize(annotate=True)

########################################################################################################################
# Find the operating wavelength so that the modulator is operating at the quadrature biasing point
########################################################################################################################

cm = mzm.CircuitModel()

# Sweeping the phase shifter voltage
num_points = 101
voltages = np.linspace(0, 10.0, num_points)
out1 = np.zeros(num_points)
out2 = np.zeros(num_points)

ps_cm = cm.top_phase_shifter
#ps_cm.vpi_l = 5.0 # VpiL product for the phase shifter

for i in range(num_points):
    ps_cm.voltage = voltages[i]
    sm = cm.get_smatrix(wavelengths=[1.55])
    out1[i] = np.abs(sm['out', 'in']) ** 2

plt.plot(voltages, out1, label="Out 1")
plt.xlabel("Voltage [V]")
plt.ylabel("Power [au]")
plt.legend()
plt.show()

#vpi_ps = ?

vpi_ps = 5

wavelengths = np.linspace(1.55, 1.555, 101)
########################################################################################################################

# Define modulator characteristics
rf_vpi = cm.vpi_l / 2 / (electrode_length / 10000)        # VpiL unit is V.cm; Dividing be 2 is due to push-pull configutation
print("Modulator RF electrode Vpi: {} V".format(rf_vpi))
 # vpi_l / (heater length / 10000)
ps_vpi = 5
print("PS electrode Vpi: {} V".format(ps_vpi))



cm.bandwidth = 25e9    # Modulator bandwidth (in Hz)

num_symbols = 2**6
samples_per_symbol = 2**7
bit_rate = 50e9

results = simulate_modulation_mzm(
    cell=mzm,
    mod_amplitude=rf_vpi / 2 * 0.8,
    mod_noise=0.0,
    opt_amplitude=1.0,
    opt_noise=0.0,
    v_mzm1=0, #ps_vpi / 2,
    v_mzm2=0.0,
    bit_rate=bit_rate,
    n_bytes=num_symbols,
    steps_per_bit=samples_per_symbol,
    center_wavelength=1.55,
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
process = [np.real, np.real, np.real, np.abs, np.abs]
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
res = result_modified_OOK(results, samples_per_symbol )
plt.scatter(np.real(res), np.imag(res), marker="+", linewidths=10, alpha=0.1)
plt.grid()
plt.xlabel("real", fontsize=14)
plt.ylabel("imag", fontsize=14)
plt.title("Constellation diagram", fontsize=14)
plt.xlim([-1.0, 1.0])
plt.ylim([-1.0, 1.0])
plt.show()
