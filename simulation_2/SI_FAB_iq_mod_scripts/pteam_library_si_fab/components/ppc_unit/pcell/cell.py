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


class PPCUnit(i3.Circuit):
    """This creates a ppc basic unit, made of tunable MZI.
    Users can specify the length of heater in one of MZI arm，
    They can also specify the length differences between the arms.
    """

    _name_prefix = "PPCUnit"
    dc = i3.ChildCellProperty(doc="Directional coupler in circuit")
    heater = i3.ChildCellProperty(doc="Heater in circuit ")
    waveguide = i3.ChildCellProperty(doc="Waveguide in circuit ")
    wg_buffer_dx = i3.PositiveNumberProperty(default=10.0, doc="Extra non-heated waveguide length around heater")
    heater_length = i3.LockedProperty(doc="Length of heater in arm")
    two_arm_length_difference = i3.NumberProperty(default=0, doc="The length difference between two arm")
    bend_radius = i3.PositiveNumberProperty(default=50, doc="The bend radius of the routing waveguide")
    trace_template = i3.TraceTemplateProperty(
        default=pdk.NWG900(), doc="The trace template for waveguide and heater", locked=True
    )
    v_bias_dc = i3.NumberProperty(default=0.0, doc="DC voltage bias on the MZI (for S-matrix only)")

    def _default_dc(self):
        return pdk.SiNDirectionalCouplerSPower(power_fraction=0.5, target_wavelength=1.55)

    # Set the default value for the heater
    def _default_heater(self):
        ht = pdk.HeatedWaveguide(trace_template=self.trace_template)
        ht.Layout(shape=[(0.0, 0.0), (100.0, 0.0)])
        ht.CircuitModel(v_bias_dc=self.v_bias_dc)
        return ht

    # Set the default value for the parallel waveguide
    def _default_waveguide(self):
        wg = i3.Waveguide(trace_template=self.trace_template)
        wg.Layout(shape=[(0.0, 0.0), (self.heater_length, 0.0)])
        return wg

    def _default_heater_length(self):
        if hasattr(self.heater, "heater_length"):
            return self.heater.heater_length
        else:
            heater_size = self.heater.get_default_view(i3.LayoutView).size_info()
            return heater_size.width

    def _default_insts(self):
        insts = {"dc_1": self.dc, "dc_2": self.dc, "ht": self.heater, "rg": self.waveguide}
        return insts

    def _default_specs(self):
        r = self.bend_radius
        dx = self.wg_buffer_dx
        specs = [
            i3.Place("dc_1:in1", (0.0, 0.0)),
            i3.PlaceRelative("ht:in", "dc_1:out2", (2.0 * r + dx, 2.0 * r)),
            i3.PlaceRelative("rg:in", "dc_1:out1", (2.0 * r + dx, -2.0 * r - self.two_arm_length_difference / 2)),
            i3.PlaceRelative("dc_2:in2", "ht:out", (2.0 * r + dx, -2.0 * r)),
            i3.ConnectManhattan("ht:in", "dc_1:out2", bend_radius=r, min_straight=0),
            i3.ConnectManhattan("rg:in", "dc_1:out1", bend_radius=r, min_straight=0),
            i3.ConnectManhattan("ht:out", "dc_2:in2", bend_radius=r, min_straight=0),
            i3.ConnectManhattan("rg:out", "dc_2:in1", bend_radius=r, min_straight=0),
        ]
        return specs

    def _default_exposed_ports(self):
        exposed_ports = {
            "dc_1:in1": "in1",
            "dc_1:in2": "in2",
            "dc_2:out1": "out1",
            "dc_2:out2": "out2",
            "ht:elec1": "ht1",
            "ht:elec2": "ht2",
        }
        return exposed_ports
