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
from ...mzi import MZI
from ipkiss3 import all as i3
from scipy.constants import speed_of_light


class TunableDelayLine(i3.Circuit):

    delay_time = i3.PositiveNumberProperty(
        default=2.1,
        doc="The total time delay of a pulse propagating through the delay line, in nm",
    )
    target_wavelength = i3.PositiveNumberProperty(
        default=1.55,
        doc="The wavelength at which the delay is implemented",
    )
    x_distance_spiral = i3.PositiveNumberProperty(
        default=875.0,
        doc="The distance along the x-dimension covered by an individual spiral",
    )
    n_o_loops = i3.PositiveIntProperty(
        default=13,
        doc="The number of loops in each spiral",
    )

    def _default_insts(self):

        trace_template = pdk.NWG900()
        trace_template_cm = trace_template.CircuitModel()

        coupler = pdk.SiNDirectionalCouplerSPower(
            power_fraction=0.5,
            target_wavelength=self.target_wavelength,
            name=self.name + "_dir_coupler",
        )

        phase_shifter = pdk.HeatedWaveguide(
            trace_template=trace_template,
            name=self.name + "_heated_waveguide",
        )
        phase_shifter.Layout(shape=[(0, 0), (30, 0)])

        mzi = MZI(
            coupler=coupler,
            phase_shifter=phase_shifter,
            x_separation=10,
            extra_y_separation=0,
            name=self.name + "_mzi",
        )

        group_index = trace_template_cm.get_n_g(environment=i3.Environment(wavelength=self.target_wavelength))
        delay_length = 0.001 * speed_of_light / group_index * self.delay_time

        spiral = pdk.FixedPortWithLengthSpiral(
            total_length=delay_length * 1.0 / 7.0 + self.x_distance_spiral,
            ports_distance=self.x_distance_spiral,
            offset_spiral_start=0.1,
            n_o_loops=self.n_o_loops,
            trace_template=trace_template,
            name=self.name + "_spiral",
        )
        spiral.Layout(
            bend_radius=i3.TECH.SINWG.BEND_RADIUS,
            spacing=i3.TECH.SINWG.SPACING,
        )

        insts = {
            "mzi1": mzi,
            "mzi2": mzi,
            "mzi3": mzi,
            "mzi4": mzi,
            "spiral1": spiral,
            "spiral2": spiral,
            "spiral3": spiral,
            "spiral4": spiral,
            "spiral5": spiral,
            "spiral6": spiral,
            "spiral7": spiral,
        }

        return insts

    def _default_specs(self):
        specs = [
            i3.Place("mzi1:in1", (0, 0)),
            i3.Join(
                [
                    ("mzi1:out2", "spiral1:in"),
                    ("spiral1:out", "mzi2:in2"),
                    ("mzi2:out2", "spiral2:in"),
                    ("spiral2:out", "spiral3:in"),
                    ("spiral3:out", "mzi3:in2"),
                    ("mzi3:out2", "spiral4:in"),
                    ("spiral4:out", "spiral5:in"),
                    ("spiral5:out", "spiral6:in"),
                    ("spiral6:out", "spiral7:in"),
                    ("spiral7:out", "mzi4:in2"),
                ]
            ),
            i3.ConnectManhattan(
                [
                    ("mzi1:out1", "mzi2:in1"),
                    ("mzi2:out1", "mzi3:in1"),
                    ("mzi3:out1", "mzi4:in1"),
                ]
            ),
        ]
        return specs

    def _default_exposed_ports(self):
        ep = {
            "mzi1:in1": "in1",
            "mzi1:in2": "in2",
            "mzi4:out1": "out1",
            "mzi4:out2": "out2",
            "mzi1:elec1": "elec11",
            "mzi1:elec2": "elec12",
            "mzi2:elec1": "elec21",
            "mzi2:elec2": "elec22",
            "mzi3:elec1": "elec31",
            "mzi3:elec2": "elec32",
            "mzi4:elec1": "elec41",
            "mzi4:elec2": "elec42",
        }
        return ep
