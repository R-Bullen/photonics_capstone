# Test circuit for LNOI IQ modulator design with electrical pads and grating couplers

import ipkiss3.all as i3
from iq_modulator_design import IQModulator
from asp_sin_lnoi_photonics.all import GRATING_COUPLER_TE1550_RIBZ, ELECTRICAL_PAD_100100, MetalWireTemplate

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
        wire = MetalWireTemplate()

        pad_y = -500

        specs = [
            # iq modulator placement
            i3.Place('iq_mod', (0, 0)),

            # pad placement
            i3.Place('pad_ps_in', (-200, pad_y)),
            i3.Place('pad_ps_out', (200, pad_y)),
            i3.Place('pad_gnd', (0, pad_y)),

            # pad wiring
            i3.ConnectElectrical(
                [("iq_mod:mzm_2_ps_2_in", "pad_ps_in:m1")],
                trace_template=wire,
                start_angle=-90,
                end_angle=180,
                control_points=[i3.H(pad_y)],
            ),
            i3.ConnectElectrical(
                [("iq_mod:mzm_2_ps_2_gnd", "pad_gnd:m1")],
                trace_template=wire,
                start_angle=-90,
                end_angle=90,
                control_points=[i3.H(pad_y + 100)],
            ),
            i3.ConnectElectrical(
                [("iq_mod:mzm_2_ps_out_gnd", "pad_gnd:m1")],
                trace_template=wire,
                start_angle=-90,
                end_angle=90,
                control_points=[i3.H(pad_y + 100)],
            ),
            i3.ConnectElectrical(
                [("iq_mod:mzm_2_ps_out_in", "pad_ps_out:m1")],
                trace_template=wire,
                start_angle=-90,
                end_angle=0,
                control_points=[i3.H(pad_y)],
            ),
        ]

        return specs

    def _default_exposed_ports(self):
        ports = {
            'iq_mod:in' : 'in'
        }

        return ports
