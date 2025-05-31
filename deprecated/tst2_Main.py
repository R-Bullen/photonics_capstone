# Based on photonics_capstone/iq_modulator_time_domain_test.p
from dateutil.utils import within_delta

import asp_sin_lnoi_photonics.all as asp    # IQ Modulator Components
import ipkiss3.all as i3                    # i3 ipkiss class
import numpy as np
import matplotlib.pylab as plt      # For plotting

from tst2_IQModulator import IQModulator

iq_mod = IQModulator()
lv = iq_mod.Layout()
lv.visualize()

