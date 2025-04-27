import asp_sin_lnoi_photonics.all as pdk
import ipkiss3.all as i3

mmi = pdk.MMI1X2_TE1550_RIB()
mzm = pdk.MZModulator1x1()
ps = pdk.PhaseShifter()
mmi2 = pdk.MMI2X1_TE1550_RIB()

circuit = (i3.Circuit
    (
    insts = {"mmi1": mmi, "mzm1": mzm, "mzm2": mzm, "ps1": ps, "mmi2": mmi2},
    specs =
        [
            i3.Place("mmi1", (0,0)),
            i3.Place("mzm1", (6000,700)),
            i3.Place("mzm2", (6000,-700)),
            i3.Place("ps1", (10300,-700)),
            i3.Place("mmi2", (11200,0)),
            i3.ConnectBend("mmi1:out2", "mzm1:in"),
            i3.ConnectBend("mmi1:out1", "mzm2:in"),
            i3.ConnectBend("mzm2:out", "ps1:in"),
            i3.ConnectBend("mzm1:out", "mmi2:in2"),
            i3.ConnectBend("ps1:out", "mmi2:in1")
        ]
    )
)

circuit_layout = circuit.Layout()
circuit_layout.visualize(annotate=True)
#lv = ps.Layout()
#lv.visualize(annotate=True)
#lv.write_gdsii('mmi_1x2.gds')
