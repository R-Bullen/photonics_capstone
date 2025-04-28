import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3

# MMI1x2 -> MZM           -> MMI2x1
#        -> MZM (shifted) ->

class IQModulator(i3.Circuit):
    """
    IQ modulator class
    """
    gc = i3.ChildCellProperty(doc="Grating coupler used.")

    spacing_x = i3.PositiveNumberProperty(default=425.0, doc="Horizontal spacing between the splitter levels.")
    spacing_y = i3.PositiveNumberProperty(default=425.0, doc="Vertical spacing between the splitters in each level.")

    def _default_gc(self):
        return asp.GRATING_COUPLER_TE1550_RIBY()

    def _default_insts(self):
        splitter_1x2 = asp.MMI1X2_TE1550_RIB()
        splitter_2x1 = asp.MMI2X1_TE1550_RIB()
        mzm_top = asp.MZModulator1x1()
        mzm_bottom = asp.MZModulator1x1(delay_at_input=False)

        insts = {
            "mmi1x2": splitter_1x2,
            "mmi2x1": splitter_2x1,
            "mzm_0": mzm_top,
            "mzm_1": mzm_bottom,
            "gc_in": self.gc,
            "gc_out": self.gc,
        }

        return insts

    def _default_specs(self):
        specs = [
            i3.Place("mmi1x2:in", (0,0)),
            i3.Place("mzm_0:in", (self.spacing_x, self.spacing_y), relative_to="mmi1x2:out1"),
            i3.Place("mzm_1:in", (self.spacing_x, -self.spacing_y), relative_to="mmi1x2:out2"),
            i3.Place("mmi2x1:in1", (self.spacing_x, -self.spacing_y), relative_to="mzm_0:out"),
            i3.ConnectManhattan([
                ("mmi1x2:out1", "mzm_0:in"),
                ("mmi1x2:out2", "mzm_1:in"),
                ("mzm_0:out", "mmi2x1:in1"),
                ("mzm_1:out", "mmi2x1:in2"),
            ]),
            i3.Join([
                ("gc_in:out", "mmi1x2:in"),
                ("mmi2x1:out", "gc_out:out"),
            ]),
        ]

        return specs

    def _default_exposed_ports(self):
        exposed_ports = {
            "gc_in:vertical_in": "in",
            "gc_out:vertical_in": "out",
        }

        return exposed_ports

# mzm = pdk.MZModulator1x1()
# mzm.Layout().visualize(annotate=True)
if __name__ == '__main__':
    iq_modulator = IQModulator()
    iq_modulator.Layout().visualize(annotate=True)
