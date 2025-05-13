SI_FAB = False

if (SI_FAB==True):
    from si_fab import all as pdk
else:
    import asp_sin_lnoi_photonics.all as pdk

#import asp_sin_lnoi_photonics.all as pdk
#from si_fab import all as pdk
import ipkiss3.all as i3
import pylab as plt
import numpy as np



class Circuit(i3.Circuit):
    mmi = i3.ChildCellProperty()

    def _default_insts(self):
        insts = {"mmi": self.mmi}
        return insts

    def _default_specs(self):
        specs = [i3.Place("mmi",(0,0))]
        return specs

    #def _default_exposed_ports(self):
        #exposed_ports = {"mmi1:in": "in", "mmi2:out": "out"}
        #exposed_ports = {"mmi:in1": "in", "mmi:out1": "out"}
        #return exposed_ports

if (__name__ == "__main__"):
    if(SI_FAB == True):
        mmi = pdk.MMI1x2Optimized1550()

        circuit = Circuit(mmi=mmi)

        circuit_layout = circuit.Layout()
        circuit_layout.visualize(annotate=True)

        circuit_model = circuit.CircuitModel()
        wavelengths = np.linspace(1.5, 1.6, 501)
        S_total = circuit_model.get_smatrix(wavelengths=wavelengths, debug=True)

        transmission = S_total['mmi_in1', 'mmi_out1', :]
        # transmission = S_total['in', 'out', :]
        plt.plot(wavelengths, np.abs(transmission) ** 2)
        plt.show()

    else:
        mmi = pdk.MMI1X2_TE1550_RIB()

        circuit = Circuit(mmi=mmi)

        circuit_layout = circuit.Layout()
        circuit_layout.visualize(annotate=True)

        circuit_model = circuit.CircuitModel()
        wavelengths = np.linspace(1.5, 1.6, 501)
        S_total = circuit_model.get_smatrix(wavelengths=wavelengths, debug=True)

        transmission = S_total['mmi_in', 'mmi_out1', :]
        #transmission = S_total['in', 'out', :]
        plt.plot(wavelengths, np.abs(transmission) ** 2)
        plt.show()
    #endif
