from tst_Circuit import *

class InitMain(Circuit):
    '''

    #Circuit(mmi=mmi, mzm1=mzm1, mzm2=mzm2, ps=ps, mmi2=mmi2, pad=pad)
    #def Layout_Display(self):
    #    Circuit.Layout().visualize(annotate=False)

    def __init__(self, mmi, mzm1, mzm2, ps, mmi2, pad):
    '''
    def __init__(self):
        return

if (__name__ == "__main__"):
    mmi = pdk.MMI1X2_TE1550_RIB()
    mzm1 = pdk.MZModulator1x1()
    mzm2 = pdk.MZModulator1x1(with_delays=False)
    ps = pdk.PhaseShifter()
    mmi2 = pdk.MMI2X1_TE1550_RIB()
    pad = pdk.ELECTRICAL_PAD_100100()  # 100 spacing

    obj = Circuit(mmi=mmi, mzm1=mzm1, mzm2=mzm2, ps=ps, mmi2=mmi2, pad=pad)
    obj.Layout().visualize(annotate=False)
    #obj = InitMain()
    #obj.Layout_Display()