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

"""Example of how to instantiate the layout of the SplitterTree PCell and simulate it for a given set of wavelengths."""

from si_fab import all as pdk
from ipkiss3 import all as i3
from pteam_library_si_fab.components.splitter_tree.cell import SplitterTree
import os
import numpy as np
import pylab as plt

splitter = pdk.MMI1x2Optimized1550()
scm = splitter.CircuitModel()

cell = SplitterTree(levels=4, name="Splitter_tree", splitter=splitter)
cell_lv = cell.Layout()
cell_lv.visualize(annotate=True)

# Simulating the circuit
wavelengths = np.linspace(1.54, 1.58, 501)
Ssplitter = scm.get_smatrix(wavelengths=wavelengths)
cm = cell.CircuitModel()
Stotal = cm.get_smatrix(wavelengths=wavelengths)
Ss = [Ssplitter, Stotal]
names = ["Splitter", "Stotal_{}".format(cell.levels)]
nports = [2, 2 ** (cell.levels)]
in_names = ["in1", "in"]

# Creating the folder to save the plots
curdir = os.path.dirname(os.path.abspath(__file__))
save_dir = os.path.join(curdir, "pics")
if not os.path.exists(save_dir):
    os.mkdir(save_dir)

for S, name, in_name, n_p in zip(Ss, names, in_names, nports):
    fig = plt.figure()
    for p in range(n_p):
        plt.plot(
            wavelengths,
            10 * np.log10(np.abs(S["out{}".format(p + 1), in_name]) ** 2),
            "-",
            label="out{}".format(p + 1),
        )
    plt.xlabel("Wavelengths [nm]")
    plt.ylabel("Transmission [dB]")
    plt.title("{} - Transmission".format(name))
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.show()
    fig.savefig(os.path.join(save_dir, "{}.png".format(name)), bbox_inches="tight")
    plt.close(fig)

print("done")
