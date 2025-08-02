import asp_sin_lnoi_photonics.all as asp
import numpy as np
import matplotlib.pyplot as plt
import ipkiss3.all as i3

from components.iq_modulator_design import IQModulator
#from deprecated.tst_SimFunc import *

from sim_functions.simulate_iqmodulator2 import simulate_modulation_iqmod2, result_modified_OOK

mod = IQModulator()
lv = mod.Layout()
#lv.visualize()

cm = mod.CircuitModel()

wavelengths = np.linspace(1.55, 1.555, 101)
S = cm.get_smatrix(wavelengths=wavelengths)

idx_min = np.argmin(np.abs(np.abs(S['out', 'in'])**2))
idx_max = np.argmax(np.abs(np.abs(S['out', 'in'])**2))
wl = wavelengths[int((idx_min + idx_max) / 2)]
print("Quadrature wavelength: {}".format(wl))

plt.figure()
plt.plot(wavelengths * 1e3, np.abs(S['out', 'in'])**2)
plt.plot([wl*1e3, wl*1e3], [0, 1])
plt.plot(wavelengths * 1e3, [np.abs(S['out', 'in'][int((idx_min + idx_max) / 2)])**2 for x in wavelengths])
plt.xlabel("Wavelength [nm]")
plt.ylabel("Transmission [au]")
plt.xlim([wavelengths[0] * 1e3, wavelengths[-1] * 1e3])
plt.ylim(0, 1)
plt.show()

########################################################################################################################
# Simulation of a MZM working in OOK modulation format.
########################################################################################################################

# Define modulator characteristics
# NOTE - electrode length = 7000
electrode_length = 7000
rf_vpi = cm.vpi_l / 2 / (electrode_length / 10000)        # VpiL unit is V.cm; Dividing be 2 is due to push-pull configutation
print("Modulator RF electrode Vpi: {} V".format(rf_vpi))

cm.bandwidth = 50e9    # Modulator bandwidth (in Hz)

results = simulate_modulation_iqmod2(
    cell=mod,
    mod_amplitude_i=rf_vpi / 2 * 0.8,
    mod_noise_i=0.01,
    mod_amplitude_q=rf_vpi / 2 * 0.8,
    mod_noise_q=0.01,
    opt_amplitude=1.0,
    opt_noise=0.01,
    bit_rate=50e9,
    n_bytes=2**8,
    steps_per_bit=2**7,
    center_wavelength=wl,

)
'''
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
'''

'''
test = i3.ConnectComponents(
    child_cells={
        "MOD": mod,

        'el_ground_top': i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=elec_ground),
        'el_ground_middle': i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=elec_ground),
        'el_ground_bottom': i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=elec_ground),

        'el_signal_top': i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=elec_signal_i),
        'el_signal_bottom': i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=elec_signal_q),

        'opt_signal': i3.FunctionExcitation(port_domain=i3.OpticalDomain, excitation_function=opt_signal),
        'opt_out': i3.Probe(port_domain=i3.OpticalDomain),
    },
    links=[
        ('el_ground_top:out', 'MOD:top_ground'),
        ('el_ground_middle:out', 'MOD:middle_ground'),
        ('el_ground_bottom:out', 'MOD:bottom_ground'),

        ('el_signal_top:out', 'MOD:top_signal'),
        ('el_signal_bottom:out', 'MOD:bottom_signal'),

        ('opt_signal:out', 'MOD:in'),
        ('MOD:out', 'opt_out:in'),
    ]
)

test_cm = test.CircuitModel()
end_time = 1.0 / frequency * 4
results = test_cm.get_time_response(t0=0, t1=end_time, dt=end_time / 1000, center_wavelength=1.55)

fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(6, 8))

axs[0,0].set_title("Top Electrical signal")
axs[0,0].plot(results.timesteps[1:] * 1e9, results['el_signal_top'][1:], 'g-+')
axs[0,0].set_xlabel("Time [ps]")
axs[0,0].set_ylabel("Voltage [V]")

axs[0,1].set_title("Bottom Electrical signal")
axs[0,1].plot(results.timesteps[1:] * 1e9, results['el_signal_bottom'][1:], 'g-+')
axs[0,1].set_xlabel("Time [ps]")
axs[0,1].set_ylabel("Voltage [V]")

axs[1,0].set_title("Optical Output")
axs[1,0].set_xlabel("Time [ps]")
axs[1,0].set_ylabel("Phase [degree]")
axs[1,0].plot(results.timesteps[1:] * 1e9, np.angle(results['opt_out'][1:], deg=True), 'r', label='out')
axs[1,0].legend()

end_time2 = 1.0 / 10e6 * 4
results2 = test_cm.get_time_response(t0=0, t1=end_time2, dt=end_time2 / 1000, center_wavelength=1.55)

axs[1,1].set_title("Optical Input")
axs[1,1].set_xlabel("Time [ps]")
axs[1,1].set_ylabel("Amplitude [Voltage]")
axs[1,1].plot(results2.timesteps[1:] * 1e9, results2['opt_signal'][1:], 'r', label='in')
axs[1,1].legend()

plt.tight_layout()
plt.show()
'''