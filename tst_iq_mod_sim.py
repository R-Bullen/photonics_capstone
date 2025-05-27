import asp_sin_lnoi_photonics.all as asp
import numpy as np
import matplotlib.pyplot as plt
import ipkiss3.all as i3

from iq_modulator_design import IQModulator
from tst_SimFunc import *

mod = IQModulator()
lv = mod.Layout()
#lv.visualize()

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
