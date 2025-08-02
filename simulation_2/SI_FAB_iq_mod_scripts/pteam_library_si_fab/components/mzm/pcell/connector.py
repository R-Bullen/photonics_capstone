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

from ipkiss3 import all as i3
from ipkiss3.pcell.cell.pcell import PCell
from si_fab.components.metal.wire.trace import M1WireTemplate, M2WireTemplate
import numpy as np


def sbend_delay(delta_x, delta_y, trace_template, bend_radius=5.0, length_delta=0.0, name="waveguide"):
    """Generates a Manhattan S-bend with a given delta in x and y, that adds an extra length section
    according to the value specified in length_delta. This is used to create two arms of a Mach-Zender interferometer
    with slightly different length.

    Parameters
    ----------
    delta_x: float
        displacement in x
    delta_y: float
        displacement in y
    trace_template : WaveguideTemplate
        trace template to use
    bend_radius : float
        Radius of the bend.
    length_delta : float
        Extra length to be added to the S-bend.
    name : str
        Name of the waveguide PCell that is returned by this function.

    Returns
    -------
    wav : i3.RoundedWaveguide
        Waveguide PCell

    """
    points = [
        (0.0, 0.0),
        (2 * bend_radius + length_delta / 2.0, 0.0),
        (2 * bend_radius + length_delta / 2.0, np.sign(delta_y) * 2 * bend_radius),
        (0.0, np.sign(delta_y) * 2 * bend_radius),
        (0.0, delta_y),
        (delta_x, delta_y),
    ]
    wav = i3.RoundedWaveguide(trace_template=trace_template, name=name)
    wav.Layout(bend_radius=bend_radius, shape=points)
    return wav


class ElectricalConnector(i3.Connector):
    @staticmethod
    def _verify_input(start_port, end_port):
        if start_port.domain != i3.ElectricalDomain:
            raise TypeError("Start port is not an electrical port.")
        if end_port.domain != i3.ElectricalDomain:
            raise TypeError("End port is not an electrical port.")


class M1Connector(ElectricalConnector):
    width = i3.PositiveNumberProperty(default=5.0, doc="width of the m1 line")
    start_angle = i3.PositiveNumberProperty(
        default=None,
        allow_none=True,
        doc="starting angle (overrides the start port angle, if any)",
    )
    end_angle = i3.PositiveNumberProperty(
        default=None,
        allow_none=True,
        doc="ending angle (overrides the end port angle, if any)",
    )

    def _connect(self, start_port, end_port, name=None):
        trace_template = M1WireTemplate()
        trace_template.Layout(width=self.width)
        start_angle = self.start_angle if self.start_angle is not None else start_port.angle
        end_angle = self.end_angle if self.end_angle is not None else end_port.angle
        sp = start_port.modified_copy(angle=start_angle)
        ep = end_port.modified_copy(angle=end_angle)
        route = i3.RouteManhattan(start_port=sp, end_port=ep)
        if name is None:
            cell = i3.ElectricalWire(trace_template=trace_template)
        else:
            cell = i3.ElectricalWire(trace_template=trace_template, name=name)
        cell.Layout(shape=route)
        return cell


class M1M2Connection(i3.PCell):
    width = i3.PositiveNumberProperty()
    route = i3.ShapeProperty()
    start_vias = i3.ListProperty(allow_none=True)
    end_vias = i3.ListProperty(allow_none=True)

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            tt = M2WireTemplate(name="{}_tmpl".format(self.name))
            tt.Layout(width=self.width)
            cell = i3.ElectricalWire(trace_template=tt, name="{}_m2".format(self.name))
            cell.Layout(shape=self.route)
            insts += i3.SRef(cell)
            return insts

    class Netlist(i3.NetlistView):
        def _generate_netlist(self, netlist):
            netlist += i3.ElectricalTerm(name="m1")
            netlist += i3.ElectricalTerm(name="m2")
            netlist.link("m1", "m2")
            return netlist


class M2Connector(ElectricalConnector):
    width = i3.PositiveNumberProperty(default=5.0, doc="width of the m1 line")
    start_angle = i3.PositiveNumberProperty(
        default=None,
        allow_none=True,
        doc="starting angle (overrides the start port angle, if any)",
    )
    end_angle = i3.PositiveNumberProperty(
        default=None,
        allow_none=True,
        doc="ending angle (overrides the end port angle, if any)",
    )
    start_vias = i3.ListProperty(allow_none=True)
    end_vias = i3.ListProperty(allow_none=True)

    def _connect(self, start_port, end_port, name=None):
        start_angle = self.start_angle if self.start_angle is not None else start_port.angle
        end_angle = self.end_angle if self.end_angle is not None else end_port.angle
        sp = start_port.modified_copy(angle=start_angle)
        ep = end_port.modified_copy(angle=end_angle)
        route = i3.RouteManhattan(start_port=sp, end_port=ep)
        start_vias = self.start_vias
        end_vias = self.end_vias
        if name is None:
            cell = M1M2Connection(width=self.width, route=route, start_vias=start_vias, end_vias=end_vias)
        else:
            cell = M1M2Connection(width=self.width, name=name, route=route, start_vias=start_vias, end_vias=end_vias)
        return cell
