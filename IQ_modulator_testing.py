from matplotlib.pyplot import annotate

import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3
import numpy as np
import pylab as plt

from asp_sin_lnoi_photonics.components.grating_couplers.pcell import GRATING_COUPLER_TE1550_RIBZ
from iq_modulator_design import IQModulator

class TestCircuit(i3.Circuit):
    # parameters
    gc_x_spacing = i3.PositiveNumberProperty(default=100.0, doc="x spacing between grating couplers")
    pad_x_spacing = i3.NumberProperty(default=200.0, doc="x spacing between electrical pads")
    wire_spacing = i3.PositiveNumberProperty(default=50.0, doc="spacing between electrical wires and each other (and modulator)")

    # components
    iq_modulator = i3.ChildCellProperty(doc="the iq modulator being tested")

    def _default_iq_modulator(self):
        iq_modulator = IQModulator(with_delays=True)
        # set iq modulator layout parameters if required
        # self.iq_modulator.Layout(centre_width=500)
        return iq_modulator

    def _default_insts(self):
        gc = GRATING_COUPLER_TE1550_RIBZ()
        # pad = asp.ELECTRICAL_PAD_100100()

        insts = {
            "iq_modulator": self.iq_modulator,
            # "gc_1": gc,
            # "gc_2": gc,
            # "pad_1": pad,
            # "pad_2": pad,
            # "pad_3": pad,
        }

        return insts

    def _default_specs(self):
        iq = self.iq_modulator.Layout()
        iq_mod_width = iq.ground_width*2 + iq.electrode_gap*4 + iq.hot_width*2 + iq.centre_width

        pad_y_pos = -(iq_mod_width/2 + self.wire_spacing*2 + 50)

        specs = [
            i3.Place("iq_modulator", (0, 0)),
            # i3.Place("gc_1", (-self.gc_x_spacing/2, iq_mod_width/2 + 100), angle=270.0),
            # i3.Place("gc_2", (self.gc_x_spacing/2, iq_mod_width/2 + 100), angle=270.0),
            # i3.Place("pad_1", (-self.pad_x_spacing, pad_y_pos)),
            # i3.Place("pad_2", (0, pad_y_pos)),
            # i3.Place("pad_3", (self.pad_x_spacing, pad_y_pos)),
        ]
        return specs

    def _default_exposed_ports(self):
        ports = {
            "iq_modulator:in": "in",
            "iq_modulator:out": "out",
        }
        return ports

if __name__ == '__main__':


    circuit = TestCircuit()
    # circuit.Layout().visualize(annotate=True)

    circuit_model = circuit.CircuitModel()

    # frequency sweep simulation
    wavelengths = np.linspace(1.5, 1.6, 501)

    S_model = circuit_model.get_smatrix(wavelengths=wavelengths)

    plt.plot(wavelengths, i3.signal_power_dB(S_model["out", "in"]), linewidth=2, label="out")
    plt.xlabel(r"Wavelength [$\mu$m]", fontsize=16)  # add a label to the x-axis
    plt.ylabel("Transmission [dB]", fontsize=16)
    plt.legend(fontsize=14)  # create a legend from the plt.plot labels
    plt.show()  # show the graph
