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

import ipkiss3.all as i3
from ipkiss3.pcell.layout.netlist_extraction.netlist_extraction import extract_netlist
from ipkiss3.pcell.netlist.instance import InstanceTerm
from si_fab.components.phase_shifter.pcell.cell import PhaseShifterWaveguide
from si_fab.components.heater.pcell.cell import HeatedWaveguide
from si_fab.components.mmi.pcell.cell import MMI1x2Optimized1550
from si_fab.components.metal.rf.pcell.cell import ProbePad
from si_fab.components.metal.via.pcell.cell import VIA_M1_M2
from si_fab.components.metal.bondpad.pcell.cell import BondPad
from si_fab.components.waveguides.rib.transition import LinearWireRibTransition
from si_fab.components.resistor.pcell.cell import Resistor
from .electrical import ElHub
from .connector import sbend_delay, M2Connector, M1M2Connection
import numpy as np
import copy


class MZModulator(i3.PCell):
    """Mach-Zehnder modulator with PN phase shifters in each arm.

    Based on a Mach-Zehnder interferometer (MZI) with a phase shifter on each arm.
    The MZI is imbalanced to the quadrature point (pi/2), for maximum extinction, on a specified delay order.
    thus maximum extinction ratio at this wavelength of operation. Both arms are equipped with waveguide heaters
    for finetuning of the optical bias.

    The modulator works in a differential push-pull configuration driven by a single GSGSG line.
    The GSGSG lines are terminated by a load resistance placed resistance_spacing after transmission line end.
    """

    _name_prefix = "MZM"
    center_wavelength = i3.PositiveNumberProperty(default=1.55, doc="Center wavelength of the modulator")
    phaseshifter = i3.ChildCellProperty(doc="Phase shifter")
    splitter = i3.ChildCellProperty(doc="Splitter used")
    taper = i3.ChildCellProperty(doc="Taper attached to the phaseshifter")
    heater = i3.ChildCellProperty(doc="Heater Waveguide")
    delay_order = i3.IntProperty(default=10, doc="Order of the delay line")
    spacing_y = i3.PositiveNumberProperty(doc="y spacing between the modulators", locked=True)
    rf_pitch_in = i3.PositiveNumberProperty(default=150.0, doc="Pitch of the GSGSG pad")
    rf_pitch_out = i3.PositiveNumberProperty(default=150.0, doc="Pitch of the GSGSG pad")
    rf_pad_length = i3.PositiveNumberProperty(default=75.0, doc="Length of the RF pads")
    rf_pad_width = i3.PositiveNumberProperty(default=75.0, doc="Width of the RF pads")
    rf_signal_width = i3.PositiveNumberProperty(default=5.0, doc="Width of the signal path")
    rf_ground_width = i3.PositiveNumberProperty(default=20.0, doc="Width of the ground path")
    rf_taper_length = i3.PositiveNumberProperty(default=100.0, doc="Length of the RF tapering section")
    resistor = i3.ChildCellProperty(doc="Resistor used between the GSGSG lines")
    bend_radius = i3.PositiveNumberProperty(default=10.0, doc="Bend radius of the connecting waveguides")
    gsgsg_in = i3.ChildCellProperty(locked=True, doc="RF pad")
    gsgsg_out = i3.ChildCellProperty(locked=True, doc="RF pad")

    def _default_splitter(self):
        return MMI1x2Optimized1550()

    def _default_heater(self):
        cell = HeatedWaveguide(name=self.name + "_heater")
        cell.Layout(shape=[(0.0, 0.0), (100.0, 0.0)])
        return cell

    def _default_taper(self):
        # by default taper from the phase shifter to the splitter's port waveguide type
        tt1 = self.splitter.get_default_view(i3.LayoutView).ports["in1"].trace_template.cell
        tt2 = self.phaseshifter.trace_template
        taper = LinearWireRibTransition(
            name=self.name + "_taper",
            start_trace_template=tt1,
            end_trace_template=tt2,
        )
        taper.Layout(
            start_position=(0.0, 0.0),
            end_position=(20.0, 0.0),
        )
        return taper

    def _default_resistor(self):
        res = Resistor(
            length=self.rf_pitch_out - 0.5 * self.rf_pad_width,
            resistance=100,
            name=self.name + "_R",
        )
        return res

    def _default_spacing_y(self):
        return 2 * self.rf_pitch_out

    def _default_gsgsg_out(self):
        m2_offset = self.phaseshifter.m2_offset
        ps_len = self.phaseshifter.length
        rf_pad_len = self.rf_pad_length
        signal_center = self.spacing_y / 2.0 + m2_offset + self.rf_signal_width / 2.0
        mod_grnd_center = self.spacing_y / 2.0 - m2_offset - self.rf_ground_width / 2.0
        mod_grnd_center_out = signal_center + (signal_center - mod_grnd_center)

        rf = ProbePad(
            name=self.name + "_HGSGSGH_out",
            start_widths=[self.rf_pad_width] * 6,
            start_centers=np.array([-2, -1, 0, 0, 1, 2]) * self.rf_pitch_out,
            start_lengths=[rf_pad_len] * 6,
            end_widths=[
                self.rf_ground_width,
                self.rf_signal_width,
                self.rf_ground_width,
                self.rf_ground_width,
                self.rf_signal_width,
                self.rf_ground_width,
            ],
            end_centers=[
                -mod_grnd_center_out,
                -signal_center,
                -mod_grnd_center,
                +mod_grnd_center,
                signal_center,
                mod_grnd_center_out,
            ],
            end_lengths=[0.5 * ps_len] * 6,
            distance=rf_pad_len + self.rf_taper_length + 0.5 * ps_len,
            port_names=["G1", "SL", "G2b", "G2", "SR", "G3"],
        )
        return rf

    def _default_gsgsg_in(self):
        m2_offset = self.phaseshifter.m2_offset
        rf_pad_len = self.rf_pad_length
        rf_ground_width = self.rf_ground_width
        rf_signal_width = self.rf_signal_width
        ps_len = self.phaseshifter.length
        signal_center = self.spacing_y / 2.0 + m2_offset + self.rf_signal_width / 2.0
        mod_grnd_center = self.spacing_y / 2.0 - m2_offset - self.rf_ground_width / 2.0
        mod_grnd_center_out = signal_center + (signal_center - mod_grnd_center)

        rf = ProbePad(
            name=self.name + "_HGSGSGH_in",
            start_widths=[self.rf_pad_width] * 6,
            start_centers=np.array([-2, -1, 0, 0, 1, 2]) * self.rf_pitch_in,
            start_lengths=[rf_pad_len] * 6,
            end_widths=[
                rf_ground_width,
                rf_signal_width,
                rf_ground_width,
                rf_ground_width,
                rf_signal_width,
                rf_ground_width,
            ],
            end_centers=[
                -mod_grnd_center_out,
                -signal_center,
                -mod_grnd_center,
                +mod_grnd_center,
                signal_center,
                mod_grnd_center_out,
            ],
            end_lengths=[0.5 * ps_len] * 6,
            distance=1.5 * rf_pad_len + 1.5 * self.rf_taper_length + 0.5 * ps_len,
            port_names=["G1", "SL", "G2b", "G2", "SR", "G3"],
        )
        return rf

    def _default_phaseshifter(self):
        return PhaseShifterWaveguide(name=self.name + "mod", length=100.0)

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            splitter = self.splitter
            ps = self.phaseshifter
            ps_len = ps.length
            rf_taper_len = self.rf_taper_length
            rf_pad_len = self.rf_pad_length
            taper = self.taper
            gsgsg_in = self.gsgsg_in
            gsgsg_out = self.gsgsg_out
            resistor = self.resistor
            ht = self.heater
            spacing_y = self.spacing_y
            bend_radius = self.bend_radius
            rf_pitch_out = self.rf_pitch_out
            center_wl = self.center_wavelength

            # some calculations
            taper_len = taper.end_position.x - taper.start_position.x
            ht_len = ht.size_info().width
            splitter_len = abs(splitter.ports["out1"].x - splitter.ports["in1"].x)
            ht_taper_sep = rf_taper_len + rf_pad_len + 50.0
            min_straight = 10.0
            resistor_x = ps_len + rf_taper_len + 0.5 * rf_pad_len
            rf_x = -rf_taper_len - rf_pad_len

            trace_template = splitter.ports["in1"].trace_template.cell
            env = i3.Environment(wavelength=center_wl)
            tt_cm = trace_template.get_default_view(i3.CircuitModelView)
            n_eff = tt_cm.get_n_eff(environment=env)
            length_pi = center_wl / (2 * n_eff)

            sbend1 = sbend_delay(
                delta_x=min_straight + 2 * bend_radius,
                delta_y=+spacing_y / 2.0 - splitter.ports["out2"].y,
                length_delta=(self.delay_order * 2 + 0.5) * length_pi,
                trace_template=trace_template,
                name="{}_sbend1".format(self.name),
            )
            sbend2 = sbend_delay(
                delta_x=min_straight + 2 * bend_radius,
                delta_y=-spacing_y / 2.0 - splitter.ports["out1"].y,
                length_delta=0.0,
                trace_template=trace_template,
                name="{}_sbend2".format(self.name),
            )

            wg = i3.Waveguide(trace_template=trace_template)
            wg.Layout(shape=[(0.0, 0.0), (1000.0, 0.0)])
            # instances
            instances = {
                "splitter": splitter,
                "combiner": splitter,
                "modulator1": ps,
                "modulator2": ps,
                "sbend1": sbend1,
                "sbend2": sbend2,
                "tm1in": taper,
                "tm1out": taper,
                "tm2in": taper,
                "tm2out": taper,
                "rfin": gsgsg_in,
                "rfout": gsgsg_out,
                "r1": resistor,
                "r2": resistor,
                "r3": resistor,
                "r4": resistor,
                "h1": ht,
                "h2": ht,
            }

            # placement and routing
            specs = [
                i3.Place("splitter:in1", (-splitter_len - 3 * taper_len - min_straight - 2 * bend_radius, 0)),
                i3.Place("modulator1:in", (0, -spacing_y / 2.0)),
                i3.Place("modulator2:in", (0, +spacing_y / 2.0)),
                i3.Place(
                    "combiner:in1",
                    (ps_len + taper_len + min_straight + ht_taper_sep + ht_len + 2 * bend_radius + splitter_len, 0.0),
                ),
                i3.FlipH("combiner"),
                i3.Join("combiner:out1", "sbend1:in"),
                i3.Join("combiner:out2", "sbend2:in"),
                i3.FlipV("modulator2"),
                i3.Place("rfin", (1.5 * rf_x, 0)),
                i3.Place("rfout", (ps_len + rf_taper_len + rf_pad_len, 0)),
                i3.FlipH("rfout"),
                i3.Place("r1", (resistor_x, -1.5 * rf_pitch_out), angle=90.0),
                i3.Place("r2", (resistor_x, -0.5 * rf_pitch_out), angle=90.0),
                i3.Place("r3", (resistor_x, 0.5 * rf_pitch_out), angle=90.0),
                i3.Place("r4", (resistor_x, 1.5 * rf_pitch_out), angle=90.0),
                i3.FlipH("h1"),
                i3.FlipH("h2"),
                i3.Place("h1:in", (ps_len + ht_len + ht_taper_sep, -spacing_y / 2.0)),
                i3.Place("h2:in", (ps_len + ht_len + ht_taper_sep, +spacing_y / 2.0)),
                i3.Join(
                    [
                        ("modulator1:in", "tm1in:out"),
                        ("modulator2:in", "tm2in:out"),
                        ("modulator1:out", "tm1out:out"),
                        ("modulator2:out", "tm2out:out"),
                    ]
                ),
                # split the connectors with different trace templates
                i3.ConnectManhattan(
                    [
                        ("h1:out", "tm1out:in"),
                        ("h2:out", "tm2out:in"),
                    ],
                    bend_radius=bend_radius,
                ),
                i3.ConnectManhattan(
                    [
                        ("tm1in:in", "splitter:out1"),
                        ("tm2in:in", "splitter:out2"),
                    ],
                    bend_radius=bend_radius,
                ),
                i3.ConnectManhattan(
                    [
                        ("h1:in", "sbend1:out"),
                        ("h2:in", "sbend2:out"),
                    ],
                    bend_radius=bend_radius,
                ),
            ]

            insts += i3.place_and_route(instances, specs=specs)

            # electrical connections
            m2_connector = M2Connector()

            insts += i3.SRef(
                m2_connector.connect(
                    insts["h1"].ports["elec2"],
                    insts["rfout"].ports["G2_pad"],
                    name=self.name + "_h1_to_rfout",
                )
            )
            insts += i3.SRef(
                m2_connector.connect(
                    insts["h2"].ports["elec2"],
                    insts["rfout"].ports["G2_pad"],
                    name=self.name + "_h2_to_rfout",
                )
            )

            # add the VIA on the overlapped area of m1 and m2 in ht

            heater_m1_length = self.cell.heater.m1_length

            h1_elec2_pos = insts["h1"].ports["elec2"].position
            h2_elec2_pos = insts["h2"].ports["elec2"].position

            via_width = VIA_M1_M2().get_default_view(i3.LayoutView).size_info().width
            num_via = heater_m1_length / via_width

            insts += i3.ARef(
                reference=VIA_M1_M2(),
                origin=(h1_elec2_pos[0] - 0.5 * (num_via - 1) * via_width, h1_elec2_pos[1]),
                period=(via_width, +via_width),
                n_o_periods=(int(num_via), 2),
            )
            insts += i3.ARef(
                reference=VIA_M1_M2(),
                origin=(h2_elec2_pos[0] - 0.5 * (num_via - 1) * via_width, h2_elec2_pos[1]),
                period=(via_width, -via_width),
                n_o_periods=(int(num_via), 2),
            )

            return insts

        def _generate_ports(self, ports):
            ports += self.instances["splitter"].ports["in1"].modified_copy(name="in")
            ports += self.instances["combiner"].ports["in1"].modified_copy(name="out")
            ports += self.instances["h1"].ports["elec1"].modified_copy(name="ele1", angle=0.0)
            ports += self.instances["h2"].ports["elec1"].modified_copy(name="ele2", angle=0.0)
            for pn in self.gsgsg_in.port_names:
                if "G2b" not in pn:
                    ports += self.instances["rfin"].ports["{}_pad".format(pn)]

            return ports

    class Netlist(i3.NetlistView):
        def _generate_netlist(self, netlist):
            # extract from layout
            netlist = extract_netlist(self.cell.get_default_view(i3.LayoutView))

            # remove electrical connections and components which were extracted but we can't use
            instances = copy.copy(netlist.instances)
            for instname in instances:
                instref = instances[instname].reference
                if isinstance(instref.cell, (Resistor, BondPad, ProbePad, i3.ElectricalWire, M1M2Connection)):
                    netlist.instances.pop(instname)
                    remove_nets = set()
                    for net in netlist.nets.values():
                        for term in net.terms:
                            if isinstance(term, InstanceTerm) and term.instance.name == instname:
                                remove_nets.add(net.name)
                    for net_name in remove_nets:
                        netlist.nets.pop(net_name)

            netlist += i3.ElectricalTerm(name="H1_pad")
            netlist += i3.ElectricalTerm(name="H2_pad")
            el_hub = ElHub()
            el_hul_nl = el_hub.Netlist()
            netlist += i3.Instance(reference=el_hul_nl, name="hub")

            electrical_links = [
                ("SL_pad", "hub:SL_pad"),
                ("G1_pad", "hub:G1_pad"),
                ("G2_pad", "hub:G2_pad"),
                ("SR_pad", "hub:SR_pad"),
                ("G3_pad", "hub:G3_pad"),
                ("H1_pad", "hub:H1_pad"),
                ("H2_pad", "hub:H2_pad"),
                ("modulator1:anode", "hub:pmod1_anode"),
                ("modulator1:cathode", "hub:pmod1_cathode"),
                ("modulator2:anode", "hub:pmod2_anode"),
                ("modulator2:cathode", "hub:pmod2_cathode"),
                ("h1:elec2", "hub:h1_elec2"),
                ("h2:elec2", "hub:h2_elec2"),
            ]

            for t1, t2 in electrical_links:
                netlist.link(t1, t2)

            return netlist

    class CircuitModel(i3.CircuitModelView):
        def _generate_model(self):
            return i3.HierarchicalModel.from_netlistview(self.netlist_view)
