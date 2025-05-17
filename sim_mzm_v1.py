import asp_sin_lnoi_photonics.all as pdk
import ipkiss3.all as i3
import pylab as plt
import numpy as np

class Circuit(i3.Circuit):
    mmi1 = i3.ChildCellProperty()
    mzm1 = i3.ChildCellProperty()
    mzm2 = i3.ChildCellProperty()

    def _default_insts(self):
        insts = {"mmi1": self.mmi1,
                 "mzm1": self.mzm1,
                 "mzm2": self.mzm2}
        '''
        insts = {"mmi1": self.mmi,
                 "mmi2": self.mmi}
        '''
        return insts

    def _default_specs(self):
        specs = [i3.Place("mmi1", (0,0)),
                 i3.Place("mzm1", (6000, 700)),
                 i3.Place("mzm2", (6000, -700)),
                 i3.ConnectBend("mmi1:out1", "mzm1:in"),
                 i3.ConnectBend("mmi1:out2", "mzm2:in")]
        '''
        specs = [i3.Place("mmi1",(0,0)),
                 i3.Place("mmi2",(400,0)),
                 i3.ConnectBend("mmi1:out1", "mmi2:in")]
        '''
        return specs

    #def _default_exposed_ports(self):
        #exposed_ports = {"mmi1:in": "in", "mmi2:out": "out"}
        #exposed_ports = {"mmi:in1": "in", "mmi:out1": "out"}
        #return exposed_ports

if (__name__ == "__main__"):
    mmi1 = pdk.MMI1X2_TE1550_RIB()
    mzm1 = pdk.MZModulator1x1()
    mzm2 = pdk.MZModulator1x1(with_delays=False)

    circuit = Circuit(mmi1=mmi1, mzm1=mzm1, mzm2=mzm2)

    circuit_layout = circuit.Layout()
    circuit_layout.visualize(annotate=True)

    circuit_model = circuit.CircuitModel()
    #wavelengths = np.linspace(1.5, 1.6, 501)
    wavelengths = np.linspace(1.5, 1.6, 501)
    S_total = circuit_model.get_smatrix(wavelengths=wavelengths, debug=True)

    transmission1 = S_total['mmi1_in', 'mzm1_out', :]
    transmission2 = S_total['mmi1_in', 'mzm2_out', :]
    reflection = S_total['mmi1_in', 'mmi1_in', :]
    #transmission = S_total['in', 'out', :]
    #plt.plot(wavelengths, np.abs(transmission) ** 2)
    plt.plot(wavelengths, i3.signal_power_dB(transmission1), color='blue', label='Delay=True')
    plt.plot(wavelengths, i3.signal_power_dB(transmission2), color='red', label='Delay=False')
    plt.plot(wavelengths, i3.signal_power_dB(reflection), color='green', label='reflection')
    plt.xlabel(r"Wavelength ($\mu$m)")
    plt.ylabel("Power (dBm)")
    plt.legend()
    plt.show()
