import asp_sin_lnoi_photonics.all as pdk
import ipkiss3.all as i3
import pylab as plt
import numpy as np

class Circuit(i3.Circuit):
    mmi1 = i3.ChildCellProperty()
    mzm1 = i3.ChildCellProperty()
    mzm2 = i3.ChildCellProperty()
    ps = i3.ChildCellProperty()
    mmi4 = i3.ChildCellProperty()

    def _default_insts(self):
        insts = {"mmi1": self.mmi1, "mzm1": self.mzm1, "mzm2": self.mzm2, "ps1": self.ps,
                 "mmi2": self.mmi1,
                 "mmi3": self.mmi1, "mzm3": self.mzm1, "mzm4": self.mzm2, "ps2": self.ps, "mmi4": self.mmi4}

        return insts

    def _default_specs(self):
        specs = [i3.Place("mmi1", (0,0)),
                 i3.Place("mzm1", (6000, 700)),
                 i3.Place("mzm2", (6000, -700)),
                 i3.Place("ps1", (10300, -700)),
                 i3.ConnectBend("mmi1:out1", "mzm1:in"),
                 i3.ConnectBend("mmi1:out2", "mzm2:in"),
                 i3.ConnectBend("mzm2:out", "ps1:in"),
                 i3.Place("mmi2", (0, 5000)),
                 i3.Place("mmi3", (0, 10000)),
                 i3.Place("mzm3", (6000, 700 + 10000)),
                 i3.Place("mzm4", (6000, -700 + 10000)),
                 i3.Place("ps2", (10300, 10000 - 700)),
                 i3.Place("mmi4", (11200, 10000)),
                 i3.ConnectBend("mmi3:out1", "mzm3:in"),
                 i3.ConnectBend("mmi3:out2", "mzm4:in"),
                 i3.ConnectBend("mzm4:out", "ps2:in"),
                 i3.ConnectBend("mzm3:out", "mmi4:in1"),
                 i3.ConnectBend("ps2:out", "mmi4:in2")]

        return specs

    #def _default_exposed_ports(self):
        #exposed_ports = {"mmi1:in": "in", "mmi2:out": "out"}
        #exposed_ports = {"mmi:in1": "in", "mmi:out1": "out"}
        #return exposed_ports

if (__name__ == "__main__"):
    mmi1 = pdk.MMI1X2_TE1550_RIB()
    mzm1 = pdk.MZModulator1x1()
    mzm2 = pdk.MZModulator1x1(with_delays=False)
    ps = pdk.PhaseShifter()
    mmi4 = pdk.MMI2X1_TE1550_RIB()

    circuit = Circuit(mmi1=mmi1, mzm1=mzm1, mzm2=mzm2, ps=ps, mmi4=mmi4)

    circuit_layout = circuit.Layout()
    circuit_layout.visualize(annotate=False)

    circuit_model = circuit.CircuitModel()
    wavelengths = np.linspace(1.5, 1.6, 501)
    S_total = circuit_model.get_smatrix(wavelengths=wavelengths, debug=True)

    transmission1 = S_total['mmi1_in', 'mzm1_out', :]
    transmission2 = S_total['mmi1_in', 'ps1_out', :]
    reflection1 = S_total['mmi1_in', 'mmi1_in', :]
    reflection2 = S_total['mmi2_in', 'mmi2_in', :]
    transmissionIQ = S_total['mmi3_in', 'mmi4_out', :]

    plt.subplot(3,1,1)
    plt.title("MZM")
    plt.plot(wavelengths, i3.signal_power_dB(transmission1), color='blue', label='Delay=True')
    plt.plot(wavelengths, i3.signal_power_dB(transmission2), color='red', label='Delay=False')
    plt.xlabel(r"Wavelength ($\mu$m)")
    plt.ylabel("Power (dBm)")
    plt.legend()

    plt.subplot(3,1,2)
    plt.title("Reflection")
    plt.plot(wavelengths, i3.signal_power_dB(reflection1), color='blue', label='IQ Modulator')
    plt.plot(wavelengths, i3.signal_power_dB(reflection2), color='red', label='MMI')
    plt.xlabel(r"Wavelength ($\mu$m)")
    plt.ylabel("Power (dBm)")
    plt.legend()

    plt.subplot(3,1,3)
    plt.plot(wavelengths, i3.signal_power_dB(transmissionIQ), color='blue')

    plt.show()
