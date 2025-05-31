import asp_sin_lnoi_photonics.all as pdk
import ipkiss3.all as i3
import pylab as plt
import numpy as np

mmi = pdk.MMI1X2_TE1550_RIB()
mzm1 = pdk.MZModulator1x1()
mzm2 = pdk.MZModulator1x1(with_delays=False)
ps = pdk.PhaseShifter()
mmi2 = pdk.MMI2X1_TE1550_RIB()
##pad = pdk.ELECTRICAL_PAD_100100()   # 100 spacing

circuit = (i3.Circuit
    (
    insts =
    {
        "mmi1": mmi,
        "mzm1": mzm1,
        "mzm2": mzm2,
        "ps1": ps,
        "mmi2": mmi2,
    ##    "pad1": pad,
    ##    "pad2": pad,
    ##    "pad3": pad
    },
    specs =
        [
            i3.Place("mmi1", (0,0)),
            i3.Place("mzm1", (6000,700)),
            i3.Place("mzm2", (6000,-700)),
            i3.Place("ps1", (10300,-700)),
            i3.Place("mmi2", (11200,0)),
            ##i3.Place("pad1", (2000+4000, -1500)),
            ##i3.Place("pad2", (2400+4000, -1500)),
            ##i3.Place("pad3", (2800+4000, -1500)),
            i3.ConnectBend("mmi1:out2", "mzm1:in"),
            i3.ConnectBend("mmi1:out1", "mzm2:in"),
            i3.ConnectBend("mzm2:out", "ps1:in"),
            i3.ConnectBend("mzm1:out", "mmi2:in2"),
            i3.ConnectBend("ps1:out", "mmi2:in1")
            #i3.ConnectElectrical("mzm2:m1_1", "pad1:m1",start_angle=0, end_angle=0),
            ##i3.ConnectElectrical("mzm2:m1_1", "pad1:m1",start_angle=-90, end_angle=0),
            #i3.ConnectElectrical("mzm2:m1_2", "pad2:m1",start_angle=0, end_angle=0),
            ##i3.ConnectElectrical("mzm2:m1_2", "pad2:m1",start_angle=-90, end_angle=0, control_points=[(i3.H(-1200))]),
            #i3.ConnectElectrical("pad1:m1", "ps1:m1",start_angle=0, end_angle=0),
            ##i3.ConnectElectrical("pad2:m1", "ps1:m1",start_angle=-90, end_angle=0, control_points=[(i3.H(-1200))]),
            ##i3.ConnectElectrical("pad3:m1", "ps1:m2",start_angle=0, end_angle=0),
        ],
    exposed_ports =
        {
            "mmi1:in": "in",
            "mmi2:out": "out"
        }
    )
)

circuit_layout = circuit.Layout()
circuit_layout.visualize(annotate=True)

# Circuit Model
circuit_model = circuit.CircuitModel()
wavelengths = np.linspace(1.5, 1.6, 501)
#print(wavelengths)
S = circuit_model.get_smatrix(wavelengths=wavelengths,debug=True)
#S = circuit_model.calculate_smatrix(wavelengths=wavelengths)

transmission = S['mmi_in', 'mmi_out1', :]
#plt.plot(wavelengths, np.abs(transmission) ** 2)
#plt.show()

#transmission = S['in', 'out', :]
#plt.plot(wavelengths, np.abs(transmission) ** 2)
#plt.show()


# Plot Simulation
#plt.plot(wavelengths, i3.signal_power_dB(S["out", "in"]), linewidth=2, label="out")
#plt.legend(fontsize=14, loc=4)
#plt.show()
