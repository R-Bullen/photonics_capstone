import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3
import numpy as np
import pylab as plt

from deprecated.mzm_custom import MZModulator1x1 as CustomMZModulator1x1


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
    # pad = i3.ChildCellProperty(doc="the pad type")
    # wire = i3.ChildCellProperty(doc="wire template")
    # gc = i3.ChildCellProperty(doc="grating coupler")

    spacing_x = i3.PositiveNumberProperty(default=425.0, doc="Horizontal spacing between the splitter levels.")
    spacing_y = i3.PositiveNumberProperty(default=250.0, doc="Vertical spacing between the splitters in each level.")

    def _default_splitter(self):
        return asp.MMI1X2_TE1550_RIB()

    def _default_combiner(self):
        return asp.MMI2X1_TE1550_RIB()

    def _default_ps(self):
        return asp.PhaseShifter()

    # def _default_pad(self):
    #     return asp.ELECTRICAL_PAD_100100()

    # def _default_wire(self):
    #     return asp.MetalWireTemplate()

    # def _default_gc(self):
    #     return asp.GRATING_COUPLER_TE1550_RIBZ()

    def _default_insts(self):
        mzm_top = CustomMZModulator1x1(with_delays=True, bend_to_phase_shifter_dist=500)
        mzm_bottom = CustomMZModulator1x1(with_delays=False)

        insts = {
            "splitter_0": self.splitter,
            "combiner_0": self.combiner,
            "splitter_1": self.splitter,
            "combiner_1": self.combiner,
            "mzm_0": mzm_top,
            "mzm_1": mzm_bottom,
            # "gc_in": self.gc,
            # "gc_out": self.gc,
            "ps": self.ps,
            # "pad_0": self.pad, # GND pad
            # "pad_1": self.pad, # pad for top mzm
            # "pad_2": self.pad, # pad for bottom mzm
        }

        return insts

    def _default_specs(self):
        specs = [
            i3.Place("splitter_0:in", (0,0)),
            i3.Place("mzm_0:in", (self.spacing_x, self.spacing_y), relative_to="splitter_0:out1"),
            i3.FlipV("mzm_0"),
            i3.Place("mzm_1:out", (0, -self.spacing_y), relative_to="mzm_0:out"),
            i3.Place("combiner_0:in1", (self.spacing_x, self.spacing_y/2), relative_to="ps:out"),
            i3.Place("splitter_1:in", (self.spacing_x, -self.spacing_y), relative_to="splitter_0:out2"),
            # i3.Place("pad_0:m1", (5000, -750)), # left pad
            # i3.Place("pad_1:m1", (5500, -750)), # middle pad
            # i3.Place("pad_2:m1", (6000, -750)), # right pad
            # i3.Place("gc_in:out", (5000, 1100), angle=-90),
            # i3.Place("gc_out:out", (6000, 1100), angle=-90),
            i3.Join([
                ("mzm_1:out", "ps:in"),
                ("splitter_1:out1", "combiner_1:in1"),
                ("splitter_1:out2", "combiner_1:in2"),
            ]),
            i3.ConnectBend([
                ("splitter_0:out1", "mzm_0:in"),
                ("splitter_0:out2", "splitter_1:in"),
                ("combiner_1:out", "mzm_1:in"),
                ("mzm_0:out", "combiner_0:in1"),
                ("ps:out", "combiner_0:in2"),
            ]),
            # i3.ConnectManhattan([
            #     ("gc_in:out", "splitter_0:in"),
            #     ("gc_out:out", "combiner_0:out"),
            #     ],
            #     control_points=[i3.H(800)]
            # ),
            # i3.ConnectElectrical(
            #     [("mzm_1:m1_1", "pad_0:m1")],
            #     trace_template=self.wire,
            #     start_angle=-90,
            #     end_angle=0,
            #     control_points=[i3.H(-400)],
            # ),
            # i3.ConnectElectrical(
            #     [("mzm_1:m1_2", "pad_1:m1")],
            #     trace_template=self.wire,
            #     start_angle=-90,
            #     end_angle=90,
            #     control_points=[i3.H(-300)],
            # ),
            # i3.ConnectElectrical(
            #     [("ps:m1", "pad_1:m1")],
            #     trace_template=self.wire,
            #     start_angle=-90,
            #     end_angle=90,
            #     control_points=[i3.H(-300)],
            # ),
            # i3.ConnectElectrical(
            #     [("ps:m2", "pad_2:m1")],
            #     trace_template=self.wire,
            #     start_angle=-90,
            #     end_angle=180,
            #     control_points=[i3.H(-400)],
            # ),
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

    circuit = IQModulator()
    # circuit.Layout(centre_width=500).visualize(annotate=True)

    circuit_model = circuit.CircuitModel()

    # frequency sweep simulation
    wavelengths = np.linspace(1.5, 1.6, 501)

    S_model = circuit_model.get_smatrix(wavelengths=wavelengths)

    plt.plot(wavelengths, i3.signal_power_dB(S_model["out", "in"]), linewidth=2, label="out")
    plt.xlabel(r"Wavelength [$\mu$m]", fontsize=16)  # add a label to the x-axis
    plt.ylabel("Transmission [dB]", fontsize=16)
    plt.legend(fontsize=14)  # create a legend from the plt.plot labels
    plt.show()  # show the graph
