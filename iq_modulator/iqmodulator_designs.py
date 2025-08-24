# Copyright (C) 2020-2024 Luceda Photonics

"""Instantiate a packaged IQ modulator."""

import ipkiss3.all as i3
import si_fab.all as pdk
from pteam_library_si_fab.components.mzm.pcell.cell import MZModulator
from si_fab.components.metal.via.pcell.cell import VIA_M1_M2


class IQModulator(i3.Circuit):
    """
    2 Mach-Zehnder modulators with single optical input and single optical output
    The optical input is separated with a splitter tree using MMIs.
    """

    splitter = i3.ChildCellProperty(doc="splitter and combiner")
    mzm = i3.ChildCellProperty(doc="mzm for IQ modulator")
    heater = i3.ChildCellProperty(doc="heater for generating pi/2")
    heater_length = i3.PositiveNumberProperty(default=100.0, doc="the length of heater")
    bend_radius = i3.PositiveNumberProperty(default=20, doc="Radius connecting waveguides")
    spacing_x = i3.PositiveNumberProperty(default=500.0, doc="horizontal spacing")
    spacing_y = i3.PositiveNumberProperty(default=50.0, doc="vertical spacing")
    straight_x = i3.PositiveNumberProperty(default=50.0, doc="horizontal waveguide length")
    straight_y = i3.PositiveNumberProperty(default=50.0, doc="vertical waveguide length")

    def _default_splitter(self):
        return pdk.MMI1x2Optimized1550()

    def _default_mzm(self):
        return MZModulator()

    def _default_heater(self):
        ht = pdk.HeatedWaveguide()
        ht.Layout(shape=[(0.0, 0.0), (self.heater_length, 0.0)])
        return ht

    def _default_insts(self):
        insts = dict()
        for cnt in range(2):
            insts[f"splitter{cnt}"] = self.splitter
            insts[f"mzm{cnt}"] = self.mzm
            insts[f"heater{cnt}"] = self.heater
        return insts

    def _default_specs(self):
        specs = [
            i3.Place("splitter0:in1", (0, 0), 90),
            i3.Place("mzm0:in", (-self.spacing_x, -5 * self.bend_radius), 90),
            i3.FlipV("mzm0"),
            i3.Place("mzm1:in", (self.spacing_x, -5 * self.bend_radius), 90),
            i3.FlipV("mzm1"),
            i3.Place("heater0:in", (self.spacing_x / 2, -3 * self.bend_radius), relative_to="mzm0:out"),
            i3.Place("heater1:in", (-self.spacing_x / 2, -3 * self.bend_radius), relative_to="mzm1:out"),
            i3.FlipH("heater1"),
            i3.Place("splitter1:in1", (self.spacing_x, -10 * self.bend_radius), -90, relative_to="mzm0:out"),
            i3.ConnectManhattan("splitter0:out1", "mzm0:in", bend_radius=self.bend_radius),
            i3.ConnectManhattan("splitter0:out2", "mzm1:in", bend_radius=self.bend_radius),
            i3.ConnectManhattan("splitter1:out1", "heater1:out", bend_radius=self.bend_radius),
            i3.ConnectManhattan("splitter1:out2", "heater0:out", bend_radius=self.bend_radius),
            i3.ConnectManhattan("mzm0:out", "heater0:in", bend_radius=self.bend_radius),
            i3.ConnectManhattan("mzm1:out", "heater1:in", bend_radius=self.bend_radius),
        ]
        return specs

    def _default_exposed_ports(self):
        exposed_ports = dict()
        for p_out in range(2):
            exposed_ports[f"splitter{p_out}:in1"] = f"sp{1 - p_out}"
            exposed_ports[f"heater{p_out}:elec2"] = f"hti{p_out}"
            exposed_ports[f"mzm{p_out}:ele1"] = f"mzmi{p_out}"
            exposed_ports[f"mzm{p_out}:ele2"] = f"mzmo{p_out}"
            exposed_ports[f"mzm{p_out}:G1_pad"] = f"mzmg1{p_out}"
            exposed_ports[f"mzm{p_out}:G2_pad"] = f"mzmg2{p_out}"
            exposed_ports[f"mzm{p_out}:G3_pad"] = f"mzmg3{p_out}"
            exposed_ports[f"mzm{p_out}:SR_pad"] = f"mzmsr{p_out}"
            exposed_ports[f"mzm{p_out}:SL_pad"] = f"mzmsl{p_out}"
        exposed_ports["heater0:elec1"] = "hg1"
        exposed_ports["heater1:elec1"] = "hg2"
        return exposed_ports


class PackagedIQModulator(i3.PCell):
    """
    The optical inputs and the outputs are routed towards the west side and using grating couplers.
    """

    dut = i3.ChildCellProperty(doc="iq modulator")
    packaging_frame = i3.ChildCellProperty(doc=" the packaging frame")
    gc = i3.ChildCellProperty(doc="grating coupler")
    heater = i3.ChildCellProperty(doc="heater for generating pi/2")
    bend_radius = i3.PositiveNumberProperty(default=20, doc="Radius connecting waveguides")
    couplers_pitch = i3.PositiveNumberProperty(default=127, doc="grating coupler pitch")
    pad_pitch = i3.PositiveNumberProperty(default=200.0, doc="bond pad pitch")
    heater_length = i3.PositiveNumberProperty(default=100.0, doc="the length of heater")
    bondpad = i3.ChildCellProperty(doc="PCell of the bondpads")

    def _default_bondpad(self):
        return pdk.BondPad(metal1_size=(100.0, 100.0), metal2_size=(125.0, 125.0), via_pitch=(5.0, 5.0))

    def _default_heater(self):
        ht = pdk.HeatedWaveguide()
        ht.Layout(shape=[(0.0, 0.0), (self.heater_length, 0.0)])
        return ht

    def _default_dut(self):
        return IQModulator(heater=self.heater)

    def _default_gc(self):
        return pdk.FC_TE_1550()

    def _default_packaging_frame(self):
        # Here we define the default packaging template we want to use to package the IQ modulator
        # We pass some parameters of the class to the package template, so that they can be changed afterwards
        # if needed.
        from phix.all import CharacterizationPackage

        return CharacterizationPackage(
            pic_length=5325,
            pic_width=4150,
            couplers_type=True,
            couplers_number=4,
            couplers_pitch=127,
            pad_number=12,
            pad_pitch=self.pad_pitch,
            pad=self.bondpad,
            marker_layer=i3.TECH.PPLAYER.M2,
            pad_to_edge=100,
            coupler=self.gc,
        )

    class Layout(i3.LayoutView):
        def generate(self, layout):
            # metal1 wiring template for positive electrode of heater
            tt_signal = i3.ElectricalWireTemplate()
            tt_signal.Layout(width=3, layer=i3.TECH.PPLAYER.M1)
            # metal2 wiring template for negative electrode of heater
            heater_m2_width = 5.0
            heater_m2_tt = i3.ElectricalWireTemplate()
            heater_m2_tt.Layout(width=heater_m2_width, layer=i3.TECH.PPLAYER.M2)
            # via array on the heaters
            via_width = VIA_M1_M2().get_default_view(i3.LayoutView).size_info().width
            num_via = 3
            heater_via_array = [
                i3.ARef(
                    reference=VIA_M1_M2(),
                    origin=(-(num_via - 1) / 2 * via_width, -via_width),
                    period=(via_width, via_width),
                    n_o_periods=(3, 3),
                ),
                i3.Rectangle(layer=i3.TECH.PPLAYER.M2, box_size=(heater_m2_width, 5 * via_width)),
            ]
            # Add DUT and packaging frame to insts dictionary
            instances = dict()
            instances["dut"] = self.dut
            instances["packaging_frame"] = self.packaging_frame

            # Add place specifications for packaging frame and dut
            specs = [
                i3.Place("packaging_frame", (0, 0)),
                i3.Place("dut:mzmg30", (0, 0), relative_to="packaging_frame:north_m2_2"),
            ]
            specs += [
                i3.ConnectElectrical(
                    "packaging_frame:south_m1_4",
                    "dut:mzmo0",
                    start_angle=90,
                    end_angle=0,
                    trace_template=tt_signal,
                    control_points=[i3.H(i3.START + 500), i3.V(i3.END + 100)],
                ),
                i3.ConnectElectrical(
                    "packaging_frame:south_m1_5",
                    "dut:mzmi0",
                    start_angle=90,
                    end_angle=0,
                    trace_template=tt_signal,
                ),
                i3.ConnectElectrical(
                    "packaging_frame:south_m1_6",
                    "dut:hti0",
                    start_angle=90,
                    end_angle=0,
                    trace_template=tt_signal,
                ),
                i3.ConnectElectrical(
                    "packaging_frame:south_m1_7",
                    "dut:hti1",
                    start_angle=90,
                    end_angle=180,
                    trace_template=tt_signal,
                ),
                i3.ConnectElectrical(
                    "packaging_frame:south_m1_8",
                    "dut:mzmo1",
                    start_angle=90,
                    end_angle=180,
                    trace_template=tt_signal,
                ),
                i3.ConnectElectrical(
                    "packaging_frame:south_m1_9",
                    "dut:mzmi1",
                    start_angle=90,
                    end_angle=180,
                    trace_template=tt_signal,
                    control_points=[i3.H(i3.START + 500), i3.V(i3.END - 100)],
                ),
            ]
            # Connect grating couplers to the optical inputs and outputs of the dut
            # When connecting to the grating couplers, we refer to "west_in_xx" as port name.
            # This is because couplers port names are renamed inside the packaging template
            for cnt1 in range(2):
                specs += [
                    i3.ConnectManhattan(
                        f"dut:sp{cnt1}",
                        f"packaging_frame:west_in_{cnt1 + 1}",
                        end_straight=200.0,
                        bend_radius=self.bend_radius,
                    ),
                ]
            layout += i3.place_and_route(insts=instances, specs=specs)
            # heater electrodes connected to common ground.
            heater_m1_length = self.cell.heater.m1_length
            po_mzmi0 = layout["dut"].ports["mzmi0"].position
            po_mzmo1 = layout["dut"].ports["mzmo1"].position
            elec1 = i3.ElectricalPort(
                name="ground1",
                position=po_mzmi0 + (0, self.heater_length - heater_m1_length),
                angle=0,
                trace_template=heater_m2_tt,
            )
            elec2 = i3.ElectricalPort(
                name="ground2",
                position=po_mzmo1 + (0, self.heater_length - heater_m1_length),
                angle=180,
                trace_template=heater_m2_tt,
            )
            layout = i3.place_and_route(
                insts=layout,
                specs=[
                    i3.ConnectElectrical(
                        "dut:hg1",
                        elec1,
                        start_angle=90.0,
                        end_angle=0.0,
                        control_points=[i3.VIA(i3.START, layout=heater_via_array, trace_template=heater_m2_tt)],
                    ),
                    i3.ConnectElectrical(
                        "dut:hg2",
                        elec2,
                        start_angle=90.0,
                        end_angle=180.0,
                        control_points=[i3.VIA(i3.START, layout=heater_via_array, trace_template=heater_m2_tt)],
                    ),
                ],
            )
            return layout
