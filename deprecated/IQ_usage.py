from IQ_modulator import IQModulator
import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3

if __name__ == '__main__':
    iq_mod = IQModulator()
    gc = asp.GRATING_COUPLER_TE1550_RIBZ()

    iq_mod.Layout().visualize()