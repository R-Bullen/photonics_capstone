# Based on photonics_capstone/iq_modulator_design.py

import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3
import numpy as np
import matplotlib.pylab as plt

from asp_sin_lnoi_photonics.components.mmi.pcell import MMI1X2_TE1550_RIB


class IQModulator(i3.PCell):
    splitter = i3.ChildCellProperty(doc="the splitter")

    def _default_splitter(self):
        return MMI1X2_TE1550_RIB()

    class Layout(i3.LayoutView):

        def _generate_instances(self, insts):
            instances = {
                "splitter": self.splitter
            }


