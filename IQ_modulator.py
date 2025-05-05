import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3

from mzm_custom import MZModulator1x1 as CustomMZModulator1x1

# MMI1x2 -> MZM           -> MMI2x1
#        -> MZM (shifted) ->

class IQModulator(i3.Circuit):
    """
    IQ modulator class
    """
    # gc = i3.ChildCellProperty(doc="Grating coupler used.")
    splitter = i3.ChildCellProperty(doc="the splitter")
    combiner = i3.ChildCellProperty(doc="the combiner")
    ps = i3.ChildCellProperty(doc="the phase shifter")
    pad = i3.ChildCellProperty(doc="the pad type")

    spacing_x = i3.PositiveNumberProperty(default=425.0, doc="Horizontal spacing between the splitter levels.")
    spacing_y = i3.PositiveNumberProperty(default=125.0, doc="Vertical spacing between the splitters in each level.")

    def _default_splitter(self):
        return asp.MMI1X2_TE1550_RIB()

    def _default_combiner(self):
        return asp.MMI2X1_TE1550_RIB()

    def _default_ps(self):
        return asp.PhaseShifter()

    def _default_pad(self):
        return asp.ELECTRICAL_PAD_100100()


    def _default_insts(self):
        mzm_top = CustomMZModulator1x1(with_delays=True, bend_to_phase_shifter_dist=500)
        mzm_bottom = CustomMZModulator1x1(with_delays=False)

        insts = {
            "splitter": self.splitter,
            "combiner": self.combiner,
            "mzm_0": mzm_top,
            "mzm_1": mzm_bottom,
            # "gc_in": self.gc,
            # "gc_out": self.gc,
            "ps": self.ps,
            "pad_0": self.pad, # GND pad
            "pad_1": self.pad, # pad for top mzm
            "pad_2": self.pad, # pad for bottom mzm
        }

        return insts

    def _default_specs(self):
        specs = [
            i3.Place("splitter:in", (0,0)),
            i3.Place("mzm_0:in", (self.spacing_x, self.spacing_y), relative_to="splitter:out1"),
            i3.FlipV("mzm_0"),
            i3.Place("mzm_1:out", (0, -self.spacing_y), relative_to="mzm_0:out"),
            i3.Place("combiner:in1", (self.spacing_x, -self.spacing_y), relative_to="mzm_0:out"),
            i3.Place("pad_0:m1", (self.spacing_x * 3, -self.spacing_y * 4), relative_to="mzm_1:in"),
            i3.Place("pad_1:m1", (self.spacing_x * 2, -self.spacing_y * 4), relative_to="mzm_1:in"),
            i3.Place("pad_2:m1", (self.spacing_x * 4, -self.spacing_y * 4), relative_to="mzm_1:in"),
            # i3.ConnectManhattan([
            #     ("mmi1x2:out1", "mzm_0:in"),
            #     ("mmi1x2:out2", "mzm_1:in"),
            #     ("mzm_0:out", "mmi2x1:in1"),
            #     ("ps:out", "mmi2x1:in2"),
            # ]),
            i3.Join([
                # ("gc_in:out", "mmi1x2:in"),
                ("mzm_1:out", "ps:in"),
                # ("mmi2x1:out", "gc_out:out"),
            ]),
        ]

        return specs

    def _default_exposed_ports(self):
        exposed_ports = {
            "splitter:in": "in",
            "combiner:out": "out",
        }

        return exposed_ports

# mzm = pdk.MZModulator1x1()
# mzm.Layout().visualize(annotate=True)
if __name__ == '__main__':
    iq_modulator = IQModulator()
    iq_modulator.Layout().visualize(annotate=True)
