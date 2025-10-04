# Test circuit for LNOI IQ modulator design with electrical pads and grating couplers

import ipkiss3.all as i3
from iq_modulator_design import IQModulator
from asp_sin_lnoi_photonics.all import GRATING_COUPLER_TE1550_RIBZ, ELECTRICAL_PAD_100100

class IQModulatorTestCircuit(i3.Circuit):
    def _default_insts(self):
        # define the iq modulator and layout
        electrode_length = 8000
        iq_mod = IQModulator(with_delays=True, delay_at_input=True)
        iq_mod.Layout(electrode_length=electrode_length, hot_width=50, electrode_gap=9)

        # mode for grating couplers and pads
        gc = GRATING_COUPLER_TE1550_RIBZ()
        pad = ELECTRICAL_PAD_100100()

        insts = {
            'iq_mod': iq_mod,
            'pad_ps_in' : pad,
            'pad_ps_out' : pad,
            'pad_gnd' : pad,
            'gc_0' : gc,
            'gc_1' : gc,
            'gc_2' : gc,
            'gc_3' : gc,
            'gc_4' : gc,
            'gc_5' : gc,
            'gc_6' : gc,
            'gc_7' : gc,
        }

        return insts

    def _default_specs(self):
        specs = {
            i3.Place('iq_mod', (0, 0)),
        }

        return specs

    def _default_exposed_ports(self):
        ports = {
            'iq_mod:in' : 'in'
        }

        return ports
