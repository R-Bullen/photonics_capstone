import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3
from simulation.sim_functions.simulate_mzm import simulate_modulation_mzm, result_modified_OOK
import numpy as np
import matplotlib.pyplot as plt

electrode_length = 8000
mzm = asp.MZModulator1x1(with_delays=True, delay_at_input=False)

lv = mzm.Layout(electrode_length=electrode_length, hot_width=50, electrode_gap=9)
lv.visualize(annotate=True)

# Find the operating wavelength so that the modulator is operating at the quadrature biasing point

cm = mzm.CircuitModel()

wavelengths = np.linspace(1.55, 1.555, 101)
S = cm.get_smatrix(wavelengths=wavelengths)

idx_min = np.argmin(np.abs(np.abs(S['out', 'in'])**2))
idx_max = np.argmax(np.abs(np.abs(S['out', 'in'])**2))
wl = wavelengths[int((idx_min + idx_max) / 2)]
print("Quadrature wavelength: {}".format(wl))
