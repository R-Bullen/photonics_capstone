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
from ipkiss3 import all as i3
from .mzi_lattice_filter import MZILatticeFilterHeated
from .lattice_utils import get_mzi_delta_length_from_fsr, get_length_pi


class Mux2Heated(MZILatticeFilterHeated):
    """Two-way wavelength demultiplexer with a passband of 50% of the FSR at the center_wavelength.
    This component inherits from MZILatticeFilter.
    Power couplings are taken from 'Coarse Wavelength Division Multiplexer on Silicon-On-Insulator
    for 100 GbE': DOI:10.1109/group4.2015.7305928
    """

    _name_prefix = "MUX2HEATED"

    power_couplings = i3.LockedProperty(default=[0.5, 0.13, 0.12, 0.5, 0.25])
    delay_lengths = i3.LockedProperty()
    bend_radius = i3.LockedProperty()
    fsr = i3.PositiveNumberProperty(default=0.01, doc="Free spectral range of the MUX2")
    center_wavelength = i3.PositiveNumberProperty(default=1.55, doc="Center wavelength")

    def _default_directional_couplers(self):
        dir_couplers = [
            pdk.SiDirectionalCouplerSPower(
                name=self.name + "dc_{}".format(cnt),
                power_fraction=p,
                target_wavelength=self.center_wavelength,
            )
            for cnt, p in enumerate(self.power_couplings)
        ]
        return dir_couplers

    def _default_delay_lengths(self):
        tt = self.directional_couplers[0].get_default_view(i3.LayoutView).ports[0].trace_template.cell
        length = get_mzi_delta_length_from_fsr(
            center_wavelength=self.center_wavelength,
            fsr=self.fsr,
            trace_template=tt,
        )

        length_pi = get_length_pi(
            center_wavelength=self.center_wavelength,
            trace_template=tt,
        )

        delay_lengths = [length, 2 * length, -(2 * length + length_pi), -2 * length]
        return delay_lengths

    def _default_bend_radius(self):
        return 5.0
