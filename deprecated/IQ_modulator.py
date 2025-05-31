import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3

from deprecated.mzm_custom import MZModulator1x1 as CustomMZModulator1x1


# MMI1x2 -> MZM           -> MMI2x1
#        -> MZM (shifted) ->

class IQModulator(i3.Circuit):
    """
    IQ modulator class
    """

    splitter = i3.ChildCellProperty(doc="the splitter")
    combiner = i3.ChildCellProperty(doc="the combiner")
    ps = i3.ChildCellProperty(doc="the phase shifter")
    pad = i3.ChildCellProperty(doc="the pad type")
    wire = i3.ChildCellProperty(doc="wire template")

    spacing_x = i3.PositiveNumberProperty(default=425.0, doc="Horizontal spacing between the splitter levels.")
    spacing_y = i3.PositiveNumberProperty(default=215.0, doc="Vertical spacing between the splitters in each level.")

    def _default_splitter(self):
        return asp.MMI1X2_TE1550_RIB()

    def _default_combiner(self):
        return asp.MMI2X1_TE1550_RIB()

    def _default_ps(self):
        return asp.PhaseShifter()

    def _default_pad(self):
        return asp.ELECTRICAL_PAD_100100()

    def _default_wire(self):
        return asp.MetalWireTemplate()

    def _default_insts(self):
        mzm_top = CustomMZModulator1x1(with_delays=True, bend_to_phase_shifter_dist=500)
        mzm_bottom = CustomMZModulator1x1(with_delays=False)

        insts = {
            "splitter_0": self.splitter,
            "combiner_0": self.combiner,
            "mzm_0": mzm_top,
            "mzm_1": mzm_bottom,
            "ps_0": self.ps,
            "ps_1": self.ps,
            "pad_0": self.pad, # GND pad
            "pad_1": self.pad, # pad for top mzm
            "pad_2": self.pad, # pad for bottom mzm
        }

        return insts

    def _default_specs(self):
        specs = [
            i3.Place("splitter_0:in", (0,0)),
            i3.Place("mzm_0:in", (self.spacing_x, self.spacing_y), relative_to="splitter_0:out1"),
            i3.FlipV("mzm_0"),
            i3.Place("mzm_1:out", (0, -self.spacing_y), relative_to="mzm_0:out"),
            i3.Place("combiner_0:in1", (self.spacing_x, self.spacing_y/2), relative_to="ps_1:out"),
            i3.Place("pad_0:m1", (5000, -750)), # left pad
            i3.Place("pad_1:m1", (5500, -750)), # middle pad
            i3.Place("pad_2:m1", (6000, -750)), # right pad
            i3.Join([
                ("mzm_0:out", "ps_0:in"),
                ("mzm_1:out", "ps_1:in"),
            ]),
            i3.ConnectBend([
                ("ps_0:out", "combiner_0:in1"),
                ("ps_1:out", "combiner_0:in2"),
            ]),
            i3.ConnectElectrical(
                [("mzm_1:m1_1", "pad_0:m1")],
                trace_template=self.wire,
                start_angle=-90,
                end_angle=0,
                control_points=[i3.H(-400), i3.V(5000)],
            ),
            i3.ConnectElectrical(
                [("mzm_1:m1_2", "pad_1:m1")],
                trace_template=self.wire,
                start_angle=-90,
                end_angle=90,
                control_points=[i3.H(-300), i3.V(5500)],
            ),
            i3.ConnectElectrical(
                [("ps_1:m1", "pad_1:m1")],
                trace_template=self.wire,
                start_angle=-90,
                end_angle=90,
                control_points=[i3.H(-300), i3.V(5500)],
            ),
            i3.ConnectElectrical(
                [("ps_1:m2", "pad_2:m1")],
                trace_template=self.wire,
                start_angle=-90,
                end_angle=180,
                control_points=[i3.H(-400), i3.V(6000)],
            ),
        ]

        return specs

    def _default_exposed_ports(self):
        exposed_ports = {
            "splitter_0:in": "in",
            "combiner_0:out": "out",
        }

        return exposed_ports

# mzm = pdk.MZModulator1x1()
# mzm.Layout().visualize(annotate=True)
if __name__ == '__main__':
    iq_modulator = IQModulator()
    iq_modulator.Layout().visualize(annotate=True)

    iq_modulator.Layout().write_gdsii('iq_mod.gds')
