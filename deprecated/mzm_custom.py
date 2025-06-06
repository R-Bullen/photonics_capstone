
import ipkiss3.all as i3
from ipkiss3.pcell.layout.netlist_extraction.netlist_extraction import extract_netlist
from ipkiss3.pcell.netlist.instance import InstanceTerm

from asp_sin_lnoi_photonics.components.waveguides.rib import SiNRibWaveguideTemplate, RWG1000, RoundedRibWaveguide
from asp_sin_lnoi_photonics.components.mmi.pcell import MMI1X2_TE1550_RIB, MMI2X1_TE1550_RIB, MMI2X2_TE1550_RIB
from asp_sin_lnoi_photonics.components.phase_shifter.pcell import PhaseShifter
from asp_sin_lnoi_photonics.compactmodels.all import PushPullModulatorModel

from asp_sin_lnoi_photonics.components.modulator.mzm.pcell.connector import bend_connector

__all__ = ["MZModulator1x1", "MZModulator1x2", "MZModulator2x2"]


class CPWElectrode(i3.PCell):
    """
    CPW travelling electrode
    """

    class Layout(i3.LayoutView):
        layer = i3.LayerProperty(default=i3.PPLayer(process=i3.TECH.PROCESS.RF, purpose=i3.TECH.PURPOSE.DRAWING),
                                 doc="electrode layer")
        waveguide_cladding_layer = i3.LayerProperty(default=i3.TECH.PPLAYER.RWG.CLADDING,
                                                    doc="the optical waveguide cladding layer")
        electrode_length = i3.PositiveNumberProperty(default=100.0, doc="the length of the electrode")
        taper_length = i3.PositiveNumberProperty(default=100.0, doc="the length of the taper")
        hot_width = i3.PositiveNumberProperty(default=23.0, doc="width of the hot electrode")
        ground_width = i3.PositiveNumberProperty(default=100.0, doc="width of the ground planes")
        electrode_gap = i3.PositiveNumberProperty(default=7.0, doc="gap between hot electrode and ground plane")
        hot_taper_width = i3.PositiveNumberProperty(default=50.0, doc="width of the hot electrode at the end of the taper")
        taper_gap = i3.PositiveNumberProperty(default=20.0,
                                              doc="gap between hot electrode and ground plane at the end of the taper")
        taper_straight_length = i3.PositiveNumberProperty(default=10.0, doc="length of the straight section at the end of the taper")
        bend_radius = i3.PositiveNumberProperty(default=200.0,
                                                doc="minimum bend radius in routing")

        top_centre_line_shape = i3.ShapeProperty(locked=True, doc='top centre line between ground plane and hot electrode')
        bottom_centre_line_shape = i3.ShapeProperty(locked=True, doc='bottom centre line between ground plane and hot electrode')

        def _default_top_centre_line_shape(self):

            shape = i3.Shape([(-self.electrode_length * 0.5 - self.taper_length,
                               self.hot_taper_width * 0.5 + self.taper_gap * 0.5),
                              (-self.electrode_length * 0.5 - self.taper_length + self.taper_straight_length,
                               self.hot_taper_width * 0.5 + self.taper_gap * 0.5),
                              (-self.electrode_length * 0.5 - self.taper_straight_length,
                               self.hot_width * 0.5  + self.electrode_gap * 0.5),
                              (-self.electrode_length * 0.5,
                               self.hot_width * 0.5  + self.electrode_gap * 0.5),
                              ])

            return shape + shape.h_mirror_copy().reverse()

        def _default_bottom_centre_line_shape(self):
            return self.top_centre_line_shape.v_mirror_copy()

        def _generate_elements(self, elems):
            # Hot electrode
            #elems += i3.Rectangle(self.layer, center=(0.0, 0.0), box_size=(self.electrode_length, self.hot_width))

            he_taper_shape2 = i3.ShapeRound(original_shape=[(-self.electrode_length * 0.5 - self.taper_length,
                                                             self.hot_taper_width * 0.5),
                                                            (-self.electrode_length * 0.5 - self.taper_length + self.taper_straight_length,
                                                             self.hot_taper_width * 0.5),
                                                            (-self.electrode_length * 0.5 - self.taper_straight_length,
                                                             self.hot_width * 0.5),
                                                            (-self.electrode_length * 0.5,
                                                             self.hot_width * 0.5),
                                                            ],
                                            radius=self.bend_radius)



            he_taper_shape = he_taper_shape2 + he_taper_shape2.h_mirror_copy().reverse() + he_taper_shape2.h_mirror_copy().v_mirror_copy() + he_taper_shape2.v_mirror_copy().reverse()

            #he_taper_shape = he_taper_shape1 + he_taper_shape2 + he_taper_shape2.h_mirror_copy().reverse() + he_taper_shape1.h_mirror_copy().reverse()
            he_taper_shape.close()
            elems += i3.Boundary(layer=self.layer, shape=he_taper_shape)

            # Top ground plane
            grnd_taper_shape1 = i3.ShapeRound(original_shape=[(-self.electrode_length * 0.5, self.hot_width * 0.5 + self.electrode_gap),
                                                              (-self.electrode_length * 0.5 - self.taper_straight_length,
                                                               self.hot_width * 0.5 + self.electrode_gap),
                                                              (
                                                                  -self.electrode_length * 0.5 - self.taper_length + self.taper_straight_length,
                                                                  self.taper_gap + self.hot_taper_width * 0.5),
                                                              (-self.electrode_length * 0.5 - self.taper_length,
                                                               self.taper_gap + self.hot_taper_width * 0.5)
                                                              ],
                                              radius=self.bend_radius)

            grnd_taper_shape2 = i3.Shape(points=[(-self.electrode_length * 0.5 - self.taper_length,
                                                  self.hot_width * 0.5 + self.electrode_gap + self.ground_width),
                                                 (-self.electrode_length * 0.5,
                                                  self.hot_width * 0.5 + self.electrode_gap + self.ground_width)])

            top_grnd_taper_shape = grnd_taper_shape1 + grnd_taper_shape2 +  grnd_taper_shape2.h_mirror_copy().reverse() + grnd_taper_shape1.h_mirror_copy().reverse()
            top_grnd_taper_shape.close()
            elems += i3.Boundary(layer=self.layer, shape=top_grnd_taper_shape)

            # Bottom ground plane

            elems += i3.Boundary(layer=self.layer, shape=top_grnd_taper_shape.v_mirror_copy())

            # Expand the waveguide cladding region under the electrode
            elems += i3.Rectangle(self.waveguide_cladding_layer, center=(0.0, 0.0),
                                  box_size=(self.electrode_length + self.taper_length * 2,
                                            self.hot_width + self.electrode_gap * 2 + self.ground_width * 2))

            # Electrode openning windows
            elems += i3.Rectangle(i3.TECH.PPLAYER.VIA,
                                  center=(-self.electrode_length * 0.5 - self.taper_length + 25, 0),
                                  box_size = (55, self.hot_taper_width + 4)
                                  )

            elems += i3.Rectangle(i3.TECH.PPLAYER.VIA,
                                  center=(-self.electrode_length * 0.5 - self.taper_length + 50,
                                          (self.hot_taper_width / 2 + self.taper_gap + self.hot_width / 2 + self.electrode_gap + self.ground_width) /2 ),
                                  box_size = (105, self.hot_width / 2 + self.electrode_gap + self.ground_width - self.hot_taper_width / 2 - self.taper_gap + 4)
                                  )

            elems += i3.Rectangle(i3.TECH.PPLAYER.VIA,
                                  center=(-self.electrode_length * 0.5 - self.taper_length + 50,
                                          -(self.hot_taper_width / 2 + self.taper_gap + self.hot_width / 2 + self.electrode_gap + self.ground_width) /2 ),
                                  box_size = (105, self.hot_width / 2 + self.electrode_gap + self.ground_width - self.hot_taper_width / 2 - self.taper_gap + 4)
                                  )

            elems += i3.Rectangle(i3.TECH.PPLAYER.VIA,
                                  center=(self.electrode_length * 0.5 + self.taper_length - 25, 0),
                                  box_size = (55, self.hot_taper_width + 4)
                                  )

            elems += i3.Rectangle(i3.TECH.PPLAYER.VIA,
                                  center=(self.electrode_length * 0.5 + self.taper_length - 50,
                                          (self.hot_taper_width / 2 + self.taper_gap + self.hot_width / 2 + self.electrode_gap + self.ground_width) /2 ),
                                  box_size = (105, self.hot_width / 2 + self.electrode_gap + self.ground_width - self.hot_taper_width / 2 - self.taper_gap + 4)
                                  )

            elems += i3.Rectangle(i3.TECH.PPLAYER.VIA,
                                  center=(self.electrode_length * 0.5 + self.taper_length - 50,
                                          -(self.hot_taper_width / 2 + self.taper_gap + self.hot_width / 2 + self.electrode_gap + self.ground_width) /2 ),
                                  box_size = (105, self.hot_width / 2 + self.electrode_gap + self.ground_width - self.hot_taper_width / 2 - self.taper_gap + 4)
                                  )

            return elems

        def _generate_ports(self, ports):
            ports += i3.ElectricalPort(
                name="signal",
                position=(-self.electrode_length * 0.5 - self.taper_length + self.taper_straight_length, 0),
                layer=self.layer
            )
            ports += i3.ElectricalPort(
                name="bottom_ground",
                position=(-self.electrode_length * 0.5 - self.taper_length + self.taper_straight_length,
                          -(self.hot_taper_width / 2 + self.taper_gap + self.hot_width / 2 + self.electrode_gap + self.ground_width) /2 ),
                layer=self.layer
            )
            ports += i3.ElectricalPort(
                name="top_ground",
                position=(-self.electrode_length * 0.5 - self.taper_length + self.taper_straight_length,
                          (self.hot_taper_width / 2 + self.taper_gap + self.hot_width / 2 + self.electrode_gap + self.ground_width) /2 ),
                layer=self.layer
            )

            return ports

    class Netlist(i3.NetlistFromLayout):
        pass


class CPWElectrodeWithWaveguides(i3.PCell):
    """
    CPW travelling wave electrodes with two waveguide in the electrode gaps
    """

    trace_template = i3.TraceTemplateProperty(doc="the waveguide trace template")

    def _default_trace_template(self):
        return RWG1000()

    class Layout(i3.LayoutView):

        electrode_length = i3.PositiveNumberProperty(default=7000.0, doc="the length of the electrode")
        hot_width = i3.PositiveNumberProperty(default=23.0, doc="width of the hot electrode")
        ground_width = i3.PositiveNumberProperty(default=150.0, doc="width of the ground planes")
        electrode_gap = i3.PositiveNumberProperty(default=6.0, doc="gap between hot electrode and ground plane")
        taper_length = i3.PositiveNumberProperty(default=200.0, doc="the length of the taper")
        hot_taper_width = i3.PositiveNumberProperty(default=50.0,
                                                    doc="width of the hot electrode at the end of the taper")
        taper_gap = i3.PositiveNumberProperty(default=20.0,
                                              doc="gap between hot electrode and ground plane at the end of the taper")
        taper_straight_length = i3.PositiveNumberProperty(default=50.0,
                                                          doc="length of the straight section at the end of the taper")
        bend_radius = i3.PositiveNumberProperty(default=150.0,
                                                doc="minimum bend radius in routing")

        def _generate_instances(self, insts):
            rf_electrode = CPWElectrode(name="electrode")
            rf_electrode_lo = rf_electrode.Layout(electrode_length=self.electrode_length,
                                                  taper_length=self.taper_length,
                                                  hot_width=self.hot_width,
                                                  ground_width=self.ground_width,
                                                  electrode_gap=self.electrode_gap,
                                                  hot_taper_width=self.hot_taper_width,
                                                  taper_gap=self.taper_gap,
                                                  taper_straight_length=self.taper_straight_length,
                                                  bend_radius=self.bend_radius,
                                                  waveguide_cladding_layer=i3.PPLayer(self.trace_template.cladding_process, self.trace_template.cladding_purpose)
                                                  )

            top_waveguide = RoundedRibWaveguide(trace_template=self.trace_template, name="top_wg")
            top_waveguide_lo = top_waveguide.Layout(shape=rf_electrode_lo.top_centre_line_shape, bend_radius=self.bend_radius, angle_step=0.1)
            bottom_waveguide = RoundedRibWaveguide(trace_template=self.trace_template, name="bottom_wg")
            bottom_waveguide_lo = bottom_waveguide.Layout(shape=rf_electrode_lo.bottom_centre_line_shape, bend_radius=self.bend_radius, angle_step=0.1)

            insts += i3.SRef(rf_electrode, position=(0, 0), name="electrode")
            insts += i3.SRef(top_waveguide, position=(0, 0), name="top_wg")
            insts += i3.SRef(bottom_waveguide, position=(0, 0), name="bottom_wg")

            return insts

        def _generate_ports(self, ports):
            return i3.expose_ports(self.instances,
                                   {'top_wg:in': 'top_in',
                                    'top_wg:out': 'top_out',
                                    'bottom_wg:in': 'bottom_in',
                                    'bottom_wg:out': 'bottom_out',
                                    'electrode:signal': 'signal',
                                    'electrode:bottom_ground': 'bottom_ground',
                                    'electrode:top_ground': 'top_ground',
                                    })

    class Netlist(i3.NetlistFromLayout):
        pass

    class CircuitModel(i3.CircuitModelView):
        vpi_l = i3.PositiveNumberProperty(default=5.0, doc="VpiL product of the single-drive phase modulator in V*cm")
        voltage = i3.NumberProperty(default=0, doc='voltage applied to the electrode in V')
        bandwidth = i3.PositiveNumberProperty(default=40e9, doc="electrial bandwidth of the modulator in Hz")

        def _generate_model(self):
            wg_tmpl_cm = self.cell.trace_template.get_default_view(i3.CircuitModelView)
            lv = self.cell.get_default_view(i3.LayoutView)
            top_wg_length = lv.instances['top_wg'].reference.trace_length()
            bottom_wg_length = lv.instances['bottom_wg'].reference.trace_length()
            return PushPullModulatorModel(
                n_g=wg_tmpl_cm.n_g,
                n_eff=wg_tmpl_cm.n_eff,
                center_wavelength=wg_tmpl_cm.center_wavelength,
                loss_dB_m=wg_tmpl_cm.loss_dB_m,
                top_wg_length=top_wg_length,
                bottom_wg_length=bottom_wg_length,
                electrode_length=lv.electrode_length,
                vpi_l=self.vpi_l,
                voltage=self.voltage,
                bandwidth=self.bandwidth
            )


class _MZM(i3.PCell):
    """Mach-Zehnder modulator with CPW travelling wave electrode.

    Delays with different length can be placed on both arms of the modulator to set the biasing point by changing the wavelength.
    These delays can be placed at the intput or output sides by setting parameter delay_at_input
    """

    _name_prefix = "MZM"
    splitter = i3.ChildCellProperty(doc="the splitter")
    combiner = i3.ChildCellProperty(doc="the combiner")
    trace_template = i3.TraceTemplateProperty(doc="the trace template")
    top_phase_shifter = i3.ChildCellProperty(locked=True, doc="top phase shifter for DC bias")
    bottom_phase_shifter = i3.ChildCellProperty(locked=True, doc="bottom phase shifter for DC bias")
    with_delays = i3.BoolProperty(default=True, doc="if including fixed length difference between two arms")
    fsr_nm = i3.PositiveNumberProperty(default=5, doc='fsr in nm') # default 5
    delay_at_input = i3.BoolProperty(default=True,
                                     doc="if True, the delays are at the input side, else at the output side")

    bend_to_phase_shifter_dist = i3.NonNegativeNumberProperty(default=0,
                                                           doc="distance between the delay bends and the phase shifter")

    phase_modulator=i3.ChildCellProperty(locked=True, doc="the rf electrode with two waveguides in the gaps")

    def _default_splitter(self):
        return MMI1X2_TE1550_RIB()

    def _default_combiner(self):
        return MMI2X1_TE1550_RIB()

    def _default_trace_template(self):
        return RWG1000()

    def _default_top_phase_shifter(self):
        ps = PhaseShifter(trace_template=self.trace_template, name="top_ps")
        return ps

    def _default_bottom_phase_shifter(self):
        ps = PhaseShifter(trace_template=self.trace_template, name="bottom_ps")
        return ps

    def _default_phase_modulator(self):
        rf_electrode_with_wgs = CPWElectrodeWithWaveguides(name="pm")
        return rf_electrode_with_wgs

    class Layout(i3.LayoutView):

        electrode_length = i3.PositiveNumberProperty(default=7000.0, doc="the length of the electrode")
        hot_width = i3.PositiveNumberProperty(default=23.0, doc="width of the hot electrode")
        ground_width = i3.PositiveNumberProperty(default=150.0, doc="width of the ground planes")
        electrode_gap = i3.PositiveNumberProperty(default=6.0, doc="gap between hot electrode and ground plane")
        taper_length = i3.PositiveNumberProperty(default=200.0, doc="the length of the taper")
        hot_taper_width = i3.PositiveNumberProperty(default=50.0,
                                                    doc="width of the hot electrode at the end of the taper")
        taper_gap = i3.PositiveNumberProperty(default=20.0,
                                              doc="gap between hot electrode and ground plane at the end of the taper")
        taper_straight_length = i3.PositiveNumberProperty(default=50.0,
                                                          doc="length of the straight section at the end of the taper")
        bend_length = i3.PositiveNumberProperty(default=160,
                                                doc="length of the waveguide bend connecting the splitter or comibiner with active section")
        phase_shifter_electrode_separation = i3.PositiveNumberProperty(default=20, doc="distance between phase shifter output and RF electrode")
        bend_radius = i3.PositiveNumberProperty(default=150.0,
                                                doc="minimum bend radius in routing")

        def _default_phase_modulator(self):
            rf_electrode_with_wgs_lo = self.cell.phase_modulator.get_default_view(self)
            rf_electrode_with_wgs_lo.set(electrode_length=self.electrode_length,
                                         taper_length=self.taper_length,
                                         hot_width=self.hot_width,
                                         ground_width=self.ground_width,
                                         electrode_gap=self.electrode_gap,
                                         hot_taper_width=self.hot_taper_width,
                                         taper_gap=self.taper_gap,
                                         taper_straight_length=self.taper_straight_length,
                                         bend_radius=self.bend_radius
                                         )
            return rf_electrode_with_wgs_lo

        def _generate_instances(self, insts):

            straight_stub_length = 10  # A straight section to connect between waveguides

            # instances
            instances = {
                'splitter': self.splitter,
                'combiner': self.combiner,
                'phase_modulator': self.phase_modulator,
                'top_phase_shifter': self.top_phase_shifter,
                'bottom_phase_shifter': self.bottom_phase_shifter,
            }

            if self.with_delays:
                # Calulte the length difference
                env = i3.Environment(wavelength=1.55)
                tt_cm = self.trace_template.cell.get_default_view(i3.CircuitModelView)
                n_g = tt_cm.get_n_g(environment=env)
                delta_l = 1.55 ** 2 / (self.fsr_nm * 1e-3 * n_g)

                if self.delay_at_input:
                    delta_y =  -self.splitter.ports['out2'].position[1] + self.phase_modulator.ports['top_in'].position[1]
                else:
                    delta_y =  self.combiner.ports['in2'].position[1] - self.phase_modulator.ports['top_out'].position[1]

                top_bend = bend_connector(delta_y= delta_y,
                                          trace_template=self.trace_template,
                                          bend_radius=self.bend_radius,
                                          length_delta=0,
                                          direction='up',
                                          name=self.name + "top_bend")

                if self.delay_at_input:
                    delta_y = -self.splitter.ports['out1'].position[1] + self.phase_modulator.ports['bottom_in'].position[1]
                else:
                    delta_y = self.combiner.ports['in1'].position[1] - self.phase_modulator.ports['bottom_out'].position[1]

                bottom_bend = bend_connector(delta_y = delta_y,
                                             trace_template=self.trace_template,
                                             bend_radius=self.bend_radius,
                                             length_delta=delta_l,
                                             direction='down',
                                             name=self.name + "bottom_bend")
                instances.update({'top_bend': top_bend,
                                  'bottom_bend': bottom_bend})

            phase_shifter_pos_x = self.phase_modulator.ports['top_in'].position[0] - self.phase_shifter_electrode_separation - \
                                  self.top_phase_shifter.ports['out'].position[0]


            if self.with_delays:
                if self.delay_at_input:
                    combiner_pos_x = self.phase_modulator.ports['top_out'].position[0] + self.bend_length - \
                                     self.combiner.ports['in1'].position[0]

                    splitter_pos_x = phase_shifter_pos_x - self.top_phase_shifter.ports['in'].position[0] - self.bend_radius * 4 - \
                                     self.splitter.ports['out1'].position[0] - straight_stub_length - self.bend_to_phase_shifter_dist
                else:
                    combiner_pos_x = self.phase_modulator.ports['top_out'].position[0] + self.bend_radius * 4 + straight_stub_length * 2 - \
                                     self.combiner.ports['in1'].position[0]

                    splitter_pos_x = phase_shifter_pos_x - self.top_phase_shifter.ports['in'].position[0] - self.bend_length - \
                                     self.splitter.ports['out1'].position[0] - straight_stub_length - self.bend_to_phase_shifter_dist

            else:
                combiner_pos_x = self.phase_modulator.ports['top_out'].position[0] + self.bend_length - \
                                 self.combiner.ports['in1'].position[0]

                splitter_pos_x = phase_shifter_pos_x - self.top_phase_shifter.ports['in'].position[0] - self.bend_length - \
                                 self.splitter.ports['out1'].position[0] - straight_stub_length




            specs=[
                i3.Place('phase_modulator', (0, 0)),
                i3.Place('top_phase_shifter', (phase_shifter_pos_x, self.phase_modulator.ports['top_in'].position[1])),
                i3.Place('bottom_phase_shifter', (phase_shifter_pos_x, self.phase_modulator.ports['bottom_in'].position[1]), ),
                i3.FlipV('bottom_phase_shifter'),
                i3.Place('splitter', (splitter_pos_x, 0)),
                i3.Place('combiner', (combiner_pos_x, 0)),

                #i3.Join("splitter:out1", "bottom_bend:in"),
                #i3.Join("splitter:out2", "top_bend:in"),

                #i3.Place('bottom_bend', (splitter_pos_x + self.splitter.ports['out1'].position[0] + 10, self.splitter.ports['out1'].position[1])),
                #i3.Place('top_bend', (splitter_pos_x + self.splitter.ports['out2'].position[0] + 10, self.splitter.ports['out2'].position[1])),


                i3.ConnectBend([
                    ("bottom_phase_shifter:out", "phase_modulator:bottom_in"),
                    ("top_phase_shifter:out", "phase_modulator:top_in"),
                ],
                    bend_radius=self.bend_radius
                )
            ]

            if self.with_delays:
                if self.delay_at_input:
                    bottom_bend_pos = (splitter_pos_x + self.splitter.ports['out1'].position[0] + straight_stub_length, self.splitter.ports['out1'].position[1])
                    top_bend_pos = (splitter_pos_x + self.splitter.ports['out2'].position[0] + straight_stub_length, self.splitter.ports['out2'].position[1])

                    specs.append(i3.ConnectBend([("splitter:out1", "bottom_bend:in"),
                                                 ("splitter:out2", "top_bend:in"),
                                                 ("bottom_bend:out", "bottom_phase_shifter:in"),
                                                 ("top_bend:out", "top_phase_shifter:in"),
                                                 ],

                                                bend_radius=self.bend_radius))

                    specs.append(i3.ConnectBend([("phase_modulator:bottom_out", "combiner:in1"),
                                                 ("phase_modulator:top_out", "combiner:in2"),
                                                 ],
                                                start_straight=straight_stub_length,
                                                end_straight=straight_stub_length,
                                                bend_radius=self.bend_radius))

                else:
                    bottom_bend_pos = (self.phase_modulator.ports['bottom_out'].position[0] + straight_stub_length, self.phase_modulator.ports['bottom_out'].position[1])
                    top_bend_pos = (self.phase_modulator.ports['top_out'].position[0] + straight_stub_length, self.phase_modulator.ports['top_out'].position[1])

                    specs.append(i3.ConnectBend([("splitter:out1", "bottom_phase_shifter:in"),
                                                 ("splitter:out2", "top_phase_shifter:in"),
                                                 ],
                                                start_straight=straight_stub_length,
                                                end_straight=straight_stub_length,
                                                bend_radius=self.bend_radius))

                    specs.append(i3.ConnectBend([("phase_modulator:bottom_out", "bottom_bend:in"),
                                                 ("phase_modulator:top_out", "top_bend:in"),
                                                 ("bottom_bend:out", "combiner:in1"),
                                                 ("top_bend:out", "combiner:in2"),
                                                 ],

                                                bend_radius=self.bend_radius))

                specs.append(i3.Place('bottom_bend', bottom_bend_pos))
                specs.append(i3.Place('top_bend', top_bend_pos))

            else:
                specs.append(i3.ConnectBend([("splitter:out1", "bottom_phase_shifter:in"),
                                             ("splitter:out2", "top_phase_shifter:in"),
                                             ("phase_modulator:bottom_out", "combiner:in1"),
                                             ("phase_modulator:top_out", "combiner:in2"),
                                             ],
                                            start_straight=straight_stub_length,
                                            end_straight=straight_stub_length,
                                            bend_radius=self.bend_radius))

            insts += i3.place_and_route(instances, specs=specs)

            return insts

        def _generate_ports(self, ports):

            for p in self.splitter.in_ports:
                ports += i3.expose_ports(self.instances, {'splitter:{}'.format(p.name): p.name})

            for p in self.combiner.out_ports:
                ports += i3.expose_ports(self.instances, {'combiner:{}'.format(p.name): p.name})

            ports += i3.expose_ports(self.instances, {'bottom_phase_shifter:m1': 'm1_1'})
            ports += i3.expose_ports(self.instances, {'bottom_phase_shifter:m2': 'm1_2'})
            ports += i3.expose_ports(self.instances, {'top_phase_shifter:m1': 'm2_1'})
            ports += i3.expose_ports(self.instances, {'top_phase_shifter:m2': 'm2_2'})
            ports += i3.expose_ports(self.instances, {'phase_modulator:signal': 'signal',
                                                      'phase_modulator:bottom_ground': 'ground_1',
                                                      'phase_modulator:top_ground': 'ground_2'
                                                      })
            return ports


    class Netlist(i3.NetlistView):
        def _generate_netlist(self, netlist):
            # extract from layout
            netlist = extract_netlist(self.cell.get_default_view(i3.LayoutView))
            return netlist

    class CircuitModel(i3.CircuitModelView):
        vpi_l = i3.PositiveNumberProperty(default=5.0, doc="VpiL product of the phase modulator in V*cm")
        voltage = i3.NumberProperty(default=0, doc='voltage applied to the electrode in V')
        bandwidth = i3.PositiveNumberProperty(default=40e9, doc="electrial bandwidth of the modulator in Hz")

        def _default_phase_modulator(self):
            pm_cm = self.cell.phase_modulator.get_default_view(self)
            pm_cm.set(vpi_l=self.vpi_l,
                      voltage=self.voltage,
                      bandwidth=self.bandwidth
                      )
            return pm_cm

        def _generate_model(self):

            return i3.HierarchicalModel.from_netlistview(self.netlist_view)

class MZModulator1x1(_MZM):
    """1x1 Mach-Zehnder modulator with CPW travelling wave electrode.

    Delays with different length can be placed on both arms of the modulator to set the biasing point by changing the wavelength.
    These delays can be placed at the intput or output sides.

    """

    pass

class MZModulator1x2(_MZM):
    """1x1 Mach-Zehnder modulator with CPW travelling wave electrode.

    Delays with different length can be placed on both arms of the modulator to set the biasing point by changing the wavelength.
    These delays can be placed at the intput or output sides.

    """

    def _default_combiner(self):
        return MMI2X2_TE1550_RIB()


class MZModulator2x2(_MZM):
    """2x2 Mach-Zehnder modulator with CPW travelling wave electrode.

    Delays with different length can be placed on both arms of the modulator to set the biasing point by changing the wavelength.
    These delays can be placed at the intput or output sides.

    """

    def _default_splitter(self):
        return MMI2X2_TE1550_RIB()

    def _default_combiner(self):
        return MMI2X2_TE1550_RIB()

if __name__ == '__main__':
    mzm = MZModulator1x1()
    mzm.Layout().visualize(annotate=True)

