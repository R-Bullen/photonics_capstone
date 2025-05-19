
# asp_sin_lnoi_photonics PDK
# Copyright (2023) RMIT University
#

import asp_sin_lnoi_photonics.all as asp
import numpy as np
import matplotlib.pyplot as plt
import ipkiss3.all as i3

from iq_modulator_design import IQModulator

iq_mod = IQModulator(with_delays=True)

lv = iq_mod.Layout(electrode_length=8000, hot_width=50, electrode_gap=9)

# lv.visualize(annotate=True)


# Find the quadrature biasing wavelength
cm = iq_mod.CircuitModel()

wavelengths = np.linspace(1.55, 1.552, 101)
S = cm.get_smatrix(wavelengths=wavelengths)

# plt.figure()
# plt.plot(wavelengths, np.abs(S['out', 'in'])**2)
# plt.show()

idx = np.argmin(np.abs(np.abs(S['out', 'in'])**2 - np.abs(S['out', 'in'])**2))
biasing_wl = wavelengths[idx]
print("Biasing wavelength: {}".format(biasing_wl))


# Time domain simulation

# Setup the input signal functions

# A square-wave voltage to the PM electrode
frequency = 10e9  # Frequency in Hz
def elec_signal(t):
    T = 1.0 / frequency
    n = int(t / T)
    if t - n * T < T/2:
        return -1.0
    else:
        return 1.0

def elec_ground(t):
   return 0.0

# CW laser at constant power
def opt_signal(t):
    return 1.0

# Define the test bench
testbench = i3.ConnectComponents(
    child_cells={
        'DUT': iq_mod,
        'el_signal_1': i3.FunctionExcitation(port_domain=i3.ElectricalDomain,
                                               excitation_function=elec_signal),
        'el_signal_2': i3.FunctionExcitation(port_domain=i3.ElectricalDomain,
                                               excitation_function=elec_signal),
        'el_ground_1': i3.FunctionExcitation(port_domain=i3.ElectricalDomain,
                                               excitation_function=elec_ground),
        'el_ground_2': i3.FunctionExcitation(port_domain=i3.ElectricalDomain,
                                               excitation_function=elec_ground),
        'el_ground_3': i3.FunctionExcitation(port_domain=i3.ElectricalDomain,
                                               excitation_function=elec_ground),
        'opt_signal': i3.FunctionExcitation(port_domain=i3.OpticalDomain,
                                               excitation_function=opt_signal),
        'opt_out': i3.Probe(port_domain=i3.OpticalDomain),
    },
    links=[
        ('el_ground_1:out', 'DUT:top_ground'),
        ('el_ground_2:out', 'DUT:middle_ground'),
        ('el_ground_3:out', 'DUT:bottom_ground'),
        ('el_signal_1:out', 'DUT:top_signal'),
        ('el_signal_2:out', 'DUT:bottom_signal'),
        ('opt_signal:out', 'DUT:in'),
        ('DUT:out', 'opt_out:in'),
    ]
)


testbench_cm = testbench.CircuitModel()
end_time = 1.0 / frequency * 4
results = testbench_cm.get_time_response(t0=0, t1=end_time, dt=end_time / 1000, center_wavelength=biasing_wl)

fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(6, 8))

axs[0].set_title("Electrical signal")
axs[0].plot(results.timesteps[1:] * 1e9, results['el_signal_1'][1:], 'g-+')
axs[0].set_xlabel("Time [ps]")
axs[0].set_ylabel("Voltage [V]")

axs[1].set_title("Optical output")
axs[1].set_xlabel("Time [ps]")
axs[1].set_ylabel("Power [au]")
axs[1].plot(results.timesteps[1:] * 1e9, (np.abs(results['opt_out'][1:]) ** 2), 'r', label='out')

axs[1].legend()

plt.tight_layout()
plt.show()
