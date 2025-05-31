import asp_sin_lnoi_photonics.all as pdk
import ipkiss3.all as i3
import pylab as plt
import numpy as np

class Circuit(i3.Circuit):
    mmi = i3.ChildCellProperty()
    ps = i3.ChildCellProperty()

    def _default_insts(self):
        insts = {"mmi": self.mmi,
                 "ps": self.ps}
        return insts

    def _default_specs(self):
        specs = [i3.Place("mmi",(0,0)),
                 i3.Place("ps", (200,-10)),
                 i3.ConnectBend("mmi:out1", "ps:in")]
        return specs

    #def _default_exposed_ports(self):
        #exposed_ports = {"mmi1:in": "in", "mmi2:out": "out"}
        #exposed_ports = {"mmi:in1": "in", "mmi:out1": "out"}
        #return exposed_ports

if (__name__ == "__main__"):
    mmi = pdk.MMI1X2_TE1550_RIB()
    ps = pdk.PhaseShifter().CircuitModel(vpi_l=1, voltage=5)

    circuit = Circuit(mmi=mmi, ps=ps)

    circuit_layout = circuit.Layout()
    circuit_layout.visualize(annotate=True)

    circuit_model = circuit.CircuitModel()
    wavelengths = np.linspace(1.5, 1.6, 501)
    S_total = circuit_model.get_smatrix(wavelengths=wavelengths, debug=True)

    # mmi_out1 - bottom output.
    transmission1 = S_total['mmi_in', 'mmi_out2', :]    # Phase Shifter
    transmission2 = S_total['mmi_in', 'ps_out', :]
    power = S_total['ps_m1', 'ps_m2', :]

    plt.plot(wavelengths, i3.signal_power_dB(transmission1), color='blue', label='mmi o/p')
    plt.plot(wavelengths, i3.signal_power_dB(transmission2), color='red', label='ps o/p')
    plt.plot(wavelengths, np.abs(power) ** 2, color='green', label='ps metal')
    plt.legend()
    plt.show()

