from tst_Circuit import *

class InitMain(Circuit):
    mmi = pdk.MMI1X2_TE1550_RIB()
    mzm1 = pdk.MZModulator1x1()
    mzm2 = pdk.MZModulator1x1(with_delays=False)
    ps = pdk.PhaseShifter()
    mmi2 = pdk.MMI2X1_TE1550_RIB()
    pad = pdk.ELECTRICAL_PAD_100100()  # 100 spacing

    def __init__(self):
        super().__init__(mmi=mmi, mzm1=mzm1, mzm2=mzm2, ps=ps, mmi2=mmi2, pad=pad)

    def DisplayLayout(self):
        super().Layout().visualize(annotate=True)

    def Simulation(self):
        return

if (__name__ == "__main__"):
    mmi = pdk.MMI1X2_TE1550_RIB()
    mzm1 = pdk.MZModulator1x1()
    mzm2 = pdk.MZModulator1x1(with_delays=False)
    ps = pdk.PhaseShifter()
    mmi2 = pdk.MMI2X1_TE1550_RIB()
    pad = pdk.ELECTRICAL_PAD_100100()  # 100 spacing

    obj = InitMain()
    obj.DisplayLayout()
