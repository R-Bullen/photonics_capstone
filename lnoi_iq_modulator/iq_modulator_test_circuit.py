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

        GC_W = 42
        GC_GAP = 127 + GC_W
        GC_X = -507 - (GC_GAP / 2)
        GC_Y = 2000
        BEND_RADIUS = 150

        specs = [
            # iq modulator placement
            i3.Place('iq_mod', (0, 0)),

            # Grating Coupler Placement
            i3.Place('gc_0', (GC_X, GC_Y), -90),
            i3.Place('gc_1', (GC_X + GC_GAP, GC_Y), -90),
            i3.Place('gc_2', (GC_X + 2 * GC_GAP, GC_Y), -90),
            i3.Place('gc_3', (GC_X + 3 * GC_GAP, GC_Y), -90),
            i3.Place('gc_4', (GC_X + 4 * GC_GAP, GC_Y), -90),
            i3.Place('gc_5', (GC_X + 5 * GC_GAP, GC_Y), -90),
            i3.Place('gc_6', (GC_X + 6 * GC_GAP, GC_Y), -90),
            i3.Place('gc_7', (GC_X + 7 * GC_GAP, GC_Y), -90),

            # Grating Coupler Connections
            i3.ConnectManhattan([('gc_0:out', 'gc_7:out')], control_points=[i3.H(GC_Y - BEND_RADIUS - 50), i3.V(GC_X - BEND_RADIUS*2 - 50),
                    i3.H(GC_Y + BEND_RADIUS*2 - 100), i3.V(-(GC_X - BEND_RADIUS*2 - 50)), i3.H(GC_Y - BEND_RADIUS - 50)], bend_radius=BEND_RADIUS),
            i3.ConnectManhattan([('gc_1:out', 'gc_6:out')], control_points=[i3.H(GC_Y - BEND_RADIUS - 100), i3.V(GC_X - BEND_RADIUS*2 - 100),
                    i3.H(GC_Y + BEND_RADIUS*2 - 50), i3.V(-(GC_X - BEND_RADIUS*2 - 100)), i3.H(GC_Y - BEND_RADIUS - 100)], bend_radius=BEND_RADIUS),
            i3.ConnectManhattan([('gc_2:out', 'gc_5:out')], control_points=[i3.H(GC_Y - BEND_RADIUS - 150), i3.V(GC_X - BEND_RADIUS*2 - 150),
                    i3.H(GC_Y + BEND_RADIUS*2), i3.V(-(GC_X - BEND_RADIUS*2 - 150)), i3.H(GC_Y - BEND_RADIUS - 150)], bend_radius=BEND_RADIUS),

            i3.ConnectManhattan([('gc_3:out', 'iq_mod:in')], control_points=[i3.H(700)], bend_radius=BEND_RADIUS),
            i3.ConnectManhattan([('gc_4:out', 'iq_mod:out')], control_points=[i3.H(700)], bend_radius=BEND_RADIUS),

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
        """
        Ports:

        OPTICAL
            in - optical input
            out - optical output

        PADS
            pad_ps_in - pad going to bottom heater on input side
            pad_gnd - pad acting as ground
            pad_ps_out - pad going to bottom arm heater at output

        PROBE LOCATIONS ON MODULATOR
            top_ground - top ground on modulator
            top_signal - top signal on modulator
            middle_ground - middle ground on modulator
            bottom_signal - bottom signal on modulator
            bottom_ground - bottom ground on modulator

        Returns
        ------- Set of exposed ports

        """

        ports = {
            'gc_3:vertical_in' : 'in',
            'gc_4:vertical_in' : 'out',

            'pad_ps_in:m1' : 'pad_ps_in',
            'pad_gnd:m1': 'pad_gnd',
            'pad_ps_out:m1' : 'pad_ps_out',

            'iq_mod:top_ground' : 'top_ground',
            'iq_mod:top_signal' : 'top_signal',
            'iq_mod:middle_ground' : 'middle_ground',
            'iq_mod:bottom_signal' : 'bottom_signal',
            'iq_mod:bottom_ground' : 'bottom_ground',

            # unused gcs
            'gc_0:vertical_in' : 'gc_0',
            'gc_1:vertical_in' : 'gc_1',
            'gc_2:vertical_in' : 'gc_2',
            'gc_5:vertical_in' : 'gc_5',
            'gc_6:vertical_in' : 'gc_6',
            'gc_7:vertical_in' : 'gc_7',
        }

        return ports
