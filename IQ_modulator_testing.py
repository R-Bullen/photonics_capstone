from matplotlib.pyplot import annotate

import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3

from iq_modulator_design import IQModulator

if __name__ == '__main__':
    iq_modulator = IQModulator(with_delays=True)
    iq_modulator.Layout().visualize(annotate=True)