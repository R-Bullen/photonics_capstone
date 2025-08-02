# Copyright (C) 2020 Luceda Photonics
# This version of Luceda Academy and related packages
# (hereafter referred to as Luceda Academy) is distributed under a proprietary License by Luceda
# It does allow you to develop and distribute add-ons or plug-ins, but does
# not allow redistribution of Luceda Academy  itself (in original or modified form).
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
#
# For the details of the licensing contract and the conditions under which
# you may use this software, we refer to the
# EULA which was distributed along with this program.
# It is located in the root of the distribution folder.

from si_fab import all as pdk
from pteam_library_si_fab import all as pt_lib
import numpy as np
from pteam_library_si_fab.components.heated_mux2.simulate.simulate_mux2 import simulate_mux2
import pylab as plt

cell = pt_lib.Mux2Heated(
    fsr=0.01,
    center_wavelength=1.55,
    heater_width=1.0,
)
lv = cell.Layout()
lv.visualize(annotate=True)

heater_voltages = [[0.0, 0.0, 0.0, 0], [1.0, 1.0, 1.0, 1.0]]
plt.figure()
for hv in heater_voltages:
    wavelengths = np.linspace(1.54, 1.56, 200)
    print("Simulating...")
    results = simulate_mux2(mux2=cell, heater_voltages=hv, wavelengths=wavelengths, debug=False)
    plt.plot(wavelengths, np.abs(results["out1"]) ** 2, label="out1-{}".format(hv))
    plt.plot(wavelengths, np.abs(results["out2"]) ** 2, label="out2-{}".format(hv))

plt.legend()
plt.show()
