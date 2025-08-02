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


class MZI(i3.Circuit):
    """A tunable Mach-Zehnder interferometer with a phase shifter in one of the arms. By default, silicon directional
    couplers are used as 50:50 power splitters and a heated waveguide is used as a phase shifter.
    """

    coupler = i3.ChildCellProperty(doc="The coupler used for the MZI")
    phase_shifter = i3.ChildCellProperty(doc="The class used for the phase shifter")
    x_separation = i3.PositiveNumberProperty(default=20, doc="The separation between the couplers and the heater")
    extra_y_separation = i3.NonNegativeNumberProperty(
        default=25,
        doc="The additional y-separation between the branches compared to if the couplers were directly connected",
    )

    def _default_coupler(self):
        return pdk.SiDirectionalCouplerSPower(name=self.name + "_coupler")

    def _default_phase_shifter(self):
        phase_shifter = pdk.HeatedWaveguide(name=self.name + "_phase_shifter")
        phase_shifter.Layout(shape=[(0, 0), (30, 0)])
        return phase_shifter

    def _default_insts(self):
        return {
            "coupler_in": self.coupler,
            "coupler_out": self.coupler,
            "phase_shifter": self.phase_shifter,
        }

    def _default_specs(self):
        return [
            i3.Place("coupler_in:in1", (0, 0)),
            i3.PlaceRelative(
                "phase_shifter:in",
                "coupler_in:out1",
                (self.x_separation, -0.5 * self.extra_y_separation),
            ),
            i3.PlaceRelative(
                "coupler_out:in1",
                "phase_shifter:out",
                (self.x_separation, 0.5 * self.extra_y_separation),
            ),
            i3.ConnectManhattan(
                "phase_shifter:in",
                "coupler_in:out1",
                min_straight=0,
            ),
            i3.ConnectManhattan(
                "phase_shifter:out",
                "coupler_out:in1",
                min_straight=0,
            ),
            i3.ConnectManhattan(
                "coupler_in:out2",
                "coupler_out:in2",
                control_points=[i3.H(i3.START + 0.5 * self.extra_y_separation)],
                min_straight=0,
            ),
        ]

    def _default_exposed_ports(self):
        return {
            "coupler_in:in1": "in1",
            "coupler_in:in2": "in2",
            "coupler_out:out1": "out1",
            "coupler_out:out2": "out2",
            "phase_shifter:elec1": "elec1",
            "phase_shifter:elec2": "elec2",
        }
