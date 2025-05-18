
import ipkiss3.all as i3
from ipkiss3.pcell.layout.netlist_extraction.netlist_extraction import extract_netlist
from ipkiss3.pcell.netlist.instance import InstanceTerm

from asp_sin_lnoi_photonics.components.waveguides.rib import SiNRibWaveguideTemplate, RWG1000, RoundedRibWaveguide
from asp_sin_lnoi_photonics.components.mmi.pcell import MMI1X2_TE1550_RIB, MMI2X1_TE1550_RIB, MMI2X2_TE1550_RIB
from asp_sin_lnoi_photonics.components.phase_shifter.pcell import PhaseShifter
from asp_sin_lnoi_photonics.compactmodels.all import PushPullModulatorModel

from asp_sin_lnoi_photonics.components.modulator.mzm.pcell.connector import bend_connector

__all__ = ["IQModulator"]


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

        centre_width = i3.PositiveNumberProperty(default=100.0, doc="width of the centre ground electrode")

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
            elems += i3.Boundary(layer=self.layer, shape=he_taper_shape,
                                 transformation=i3.Translation((0, (self.hot_width + self.electrode_gap * 2 + self.centre_width)/2)))

            # boundary for bottom signal electrode
            elems += i3.Boundary(layer=self.layer, shape=he_taper_shape,
                                 transformation=i3.Translation((0,-(self.hot_width + self.electrode_gap * 2 + self.centre_width)/2)))

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

            top_grnd_taper_shape = (grnd_taper_shape1 + grnd_taper_shape2 +
                                    grnd_taper_shape2.h_mirror_copy().reverse() +
                                    grnd_taper_shape1.h_mirror_copy().reverse())
            top_grnd_taper_shape.close()

            # top ground plane
            elems += i3.Boundary(layer=self.layer, shape=top_grnd_taper_shape,
                                 transformation=i3.Translation((0, (self.hot_width + self.electrode_gap * 2 + self.centre_width)/2)))

            # bottom ground plane
            elems += i3.Boundary(layer=self.layer, shape=top_grnd_taper_shape.v_mirror_copy(),
                                 transformation=i3.Translation((0,-(self.hot_width + self.electrode_gap * 2 + self.centre_width)/2)))

            # the shape of the end of the middle gnd electrode
            grnd_taper_shape3 = ( grnd_taper_shape1 +
                            grnd_taper_shape1.translate_copy(
                                (0,-(self.centre_width + self.electrode_gap * 2 + self.hot_width))).v_mirror_copy().reverse()
                            )

            # shape combining the two ends of the middle gnd electrode into one shape
            middle_grnd_taper_shape = (grnd_taper_shape3 +
                                       grnd_taper_shape3.translate_copy((0, -(self.centre_width + self.electrode_gap * 2 + self.hot_width))).h_mirror_copy().v_mirror_copy())
            middle_grnd_taper_shape.close()

            # middle ground plane
            elems += i3.Boundary(layer=self.layer, shape=middle_grnd_taper_shape,
                                 transformation=i3.Translation(
                                     (0, -(self.centre_width + self.electrode_gap * 2 + self.hot_width)/2)))

            # CLADDING
            # Expand the waveguide cladding region under the electrode
            elems += i3.Rectangle(self.waveguide_cladding_layer,
                                  center=(0.0, 0.0),
                                  box_size=(self.electrode_length + self.taper_length * 2,
                                            self.hot_width * 2 + self.electrode_gap * 4 + self.ground_width * 2 + self.centre_width))

            ## Electrode opening windows


            # width and location of the top and bottom ground electrode windows
            ground_electrode_width = self.ground_width + self.hot_width/2 + self.electrode_gap - self.hot_taper_width/2 - self.taper_gap + 4
            ground_electrode_centre_y = (self.centre_width + self.electrode_gap*2 + self.hot_width + self.hot_taper_width + self.taper_gap*2 + ground_electrode_width-4)/2

            # location of signal electrode windows
            signal_electrode_centre_y = (self.centre_width + self.hot_width + self.electrode_gap * 2) / 2

            # width of centre ground electrode windows
            centre_ground_electrode_width = self.centre_width - 2*(self.taper_gap + (self.hot_taper_width/2 - self.hot_width/2 - self.electrode_gap)) + 4

            # left top ground
            elems += i3.Rectangle(i3.TECH.PPLAYER.VIA,
                                  center=(-self.electrode_length * 0.5 - self.taper_length + 50,
                                          ground_electrode_centre_y),
                                  box_size = (105,  ground_electrode_width)
                                  )

            # left top signal
            elems += i3.Rectangle(i3.TECH.PPLAYER.VIA,
                                  center=(-self.electrode_length * 0.5 - self.taper_length + 25,
                                          signal_electrode_centre_y),
                                  box_size=(55, self.hot_taper_width + 4)
                                  )

            # left middle ground
            elems += i3.Rectangle(i3.TECH.PPLAYER.VIA,
                                  center=(-self.electrode_length * 0.5 - self.taper_length + 50, 0),
                                  box_size=(105, centre_ground_electrode_width)
                                  )

            # left bottom signal
            elems += i3.Rectangle(i3.TECH.PPLAYER.VIA,
                                  center=(-self.electrode_length * 0.5 - self.taper_length + 25,
                                          -signal_electrode_centre_y),
                                  box_size=(55, self.hot_taper_width + 4)
                                  )

            # left bottom ground
            elems += i3.Rectangle(i3.TECH.PPLAYER.VIA,
                                  center=(-self.electrode_length * 0.5 - self.taper_length + 50,
                                          -ground_electrode_centre_y),
                                  box_size = (105,ground_electrode_width)
                                  )

            # right top ground
            elems += i3.Rectangle(i3.TECH.PPLAYER.VIA,
                                  center=(self.electrode_length * 0.5 + self.taper_length - 50,
                                          ground_electrode_centre_y),
                                  box_size = (105, ground_electrode_width)
                                  )

            # right top signal
            elems += i3.Rectangle(i3.TECH.PPLAYER.VIA,
                                  center=(self.electrode_length * 0.5 + self.taper_length - 25,
                                          signal_electrode_centre_y),
                                  box_size=(55, self.hot_taper_width + 4)
                                  )

            # right middle ground
            elems += i3.Rectangle(i3.TECH.PPLAYER.VIA,
                                  center=(self.electrode_length * 0.5 + self.taper_length - 50, 0),
                                  box_size=(105, centre_ground_electrode_width)
                                  )

            # right bottom signal
            elems += i3.Rectangle(i3.TECH.PPLAYER.VIA,
                                  center=(self.electrode_length * 0.5 + self.taper_length - 25,
                                          -signal_electrode_centre_y),
                                  box_size=(55, self.hot_taper_width + 4)
                                  )

            # right bottom ground
            elems += i3.Rectangle(i3.TECH.PPLAYER.VIA,
                                  center=(self.electrode_length * 0.5 + self.taper_length - 50,
                                          -ground_electrode_centre_y),
                                  box_size = (105, ground_electrode_width)
                                  )

            return elems

        def _generate_ports(self, ports):
            # width and location of the top and bottom ground electrode windows
            ground_electrode_width = self.ground_width + self.hot_width / 2 + self.electrode_gap - self.hot_taper_width / 2 - self.taper_gap + 4
            ground_electrode_centre_y = (self.centre_width + self.electrode_gap * 2 + self.hot_width + self.hot_taper_width + self.taper_gap * 2 + ground_electrode_width - 4) / 2

            ports += i3.ElectricalPort(
                name="top_ground",
                position=(-self.electrode_length * 0.5 - self.taper_length + self.taper_straight_length,
                          ground_electrode_centre_y),
                layer=self.layer
            )
            ports += i3.ElectricalPort(
                name="top_signal",
                position=(-self.electrode_length * 0.5 - self.taper_length + self.taper_straight_length,
                          (self.hot_width + self.electrode_gap * 2 + self.centre_width) / 2),
                layer=self.layer
            )
            ports += i3.ElectricalPort(
                name="middle_ground",
                position=(-self.electrode_length * 0.5 - self.taper_length + self.taper_straight_length, 0),
                layer=self.layer
            )
            ports += i3.ElectricalPort(
                name="bottom_signal",
                position=(-self.electrode_length * 0.5 - self.taper_length + self.taper_straight_length,
                          -(self.hot_width + self.electrode_gap * 2 + self.centre_width) / 2),
                layer=self.layer
            )
            ports += i3.ElectricalPort(
                name="bottom_ground",
                position=(-self.electrode_length * 0.5 - self.taper_length + self.taper_straight_length,
                          -ground_electrode_centre_y),
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
        ground_width = i3.PositiveNumberProperty(default=50.0, doc="width of the ground planes")

        centre_width = i3.PositiveNumberProperty(default=100.0, doc="width of the centre ground electrode")

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
                                                  centre_width=self.centre_width,
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

            top_waveguide_2 = RoundedRibWaveguide(trace_template=self.trace_template, name="top_wg_2")
            top_waveguide_lo_2 = top_waveguide_2.Layout(shape=rf_electrode_lo.top_centre_line_shape,
                                                    bend_radius=self.bend_radius, angle_step=0.1)
            bottom_waveguide_2 = RoundedRibWaveguide(trace_template=self.trace_template, name="bottom_wg_2")
            bottom_waveguide_lo_2 = bottom_waveguide_2.Layout(shape=rf_electrode_lo.bottom_centre_line_shape,
                                                          bend_radius=self.bend_radius, angle_step=0.1)

            insts += i3.SRef(rf_electrode, position=(0, 0), name="electrode")
            insts += i3.SRef(top_waveguide,
                             position=(0, (self.hot_width + self.electrode_gap * 2 + self.centre_width)/2), name="top_wg")
            insts += i3.SRef(bottom_waveguide,
                             position=(0, (self.hot_width + self.electrode_gap * 2 + self.centre_width)/2), name="bottom_wg")
            insts += i3.SRef(top_waveguide_2,
                             position=(0, -(self.hot_width + self.electrode_gap * 2 + self.centre_width)/2), name="top_wg_2")
            insts += i3.SRef(bottom_waveguide_2,
                             position=(0, -(self.hot_width + self.electrode_gap * 2 + self.centre_width)/2), name="bottom_wg_2")

            return insts

        def _generate_ports(self, ports):
            return i3.expose_ports(self.instances,
                                   {'top_wg:in': 'top_in',
                                    'top_wg:out': 'top_out',
                                    'bottom_wg:in': 'bottom_in',
                                    'bottom_wg:out': 'bottom_out',
                                    'top_wg_2:in': 'top_in_2',
                                    'top_wg_2:out': 'top_out_2',
                                    'bottom_wg_2:in': 'bottom_in_2',
                                    'bottom_wg_2:out': 'bottom_out_2',
                                    'electrode:top_ground': 'top_ground',
                                    'electrode:top_signal': 'top_signal',
                                    'electrode:middle_ground': 'middle_ground',
                                    'electrode:bottom_signal': 'bottom_signal',
                                    'electrode:bottom_ground': 'bottom_ground',
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


class IQModulator(i3.PCell):
    """
    Modified MZM into an IQ modulator
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

    bend_to_phase_shifter_dist = i3.NonNegativeNumberProperty(default=500.0,
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

        centre_width = i3.PositiveNumberProperty(default=150.0, doc="width of the centre ground electrode")

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
                                         centre_width=self.centre_width,
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
                'splitter_2': self.splitter,
                'splitter_main': self.splitter,
                'combiner': self.combiner,
                'combiner_2': self.combiner,
                'combiner_main': self.combiner,
                'phase_modulator': self.phase_modulator,
                'top_phase_shifter': self.top_phase_shifter,
                'bottom_phase_shifter': self.bottom_phase_shifter,
                'top_phase_shifter_2': self.top_phase_shifter,
                'bottom_phase_shifter_2': self.bottom_phase_shifter,
                'top_output_phase_shifter': self.top_phase_shifter,
                'bottom_output_phase_shifter': self.bottom_phase_shifter,
            }

            if self.with_delays:
                # Calulte the length difference
                env = i3.Environment(wavelength=1.55)
                tt_cm = self.trace_template.cell.get_default_view(i3.CircuitModelView)
                n_g = tt_cm.get_n_g(environment=env)
                delta_l = 1.55 ** 2 / (self.fsr_nm * 1e-3 * n_g)

                if self.delay_at_input:
                    delta_y =  -self.splitter.ports['out2'].position[1] + self.phase_modulator.ports['top_in'].position[1] - (self.hot_width + self.electrode_gap * 2 + self.centre_width)/2
                else:
                    delta_y =  self.combiner.ports['in2'].position[1] - self.phase_modulator.ports['top_out'].position[1] - (self.hot_width + self.electrode_gap * 2 + self.centre_width)/2

                top_bend = bend_connector(delta_y= delta_y,
                                          trace_template=self.trace_template,
                                          bend_radius=self.bend_radius,
                                          length_delta=delta_l,
                                          direction='up',
                                          name=self.name + "top_bend")

                if self.delay_at_input:
                    delta_y = -self.splitter.ports['out1'].position[1] + self.phase_modulator.ports['bottom_in'].position[1] - (self.hot_width + self.electrode_gap * 2 + self.centre_width)/2
                else:
                    delta_y = self.combiner.ports['in1'].position[1] - self.phase_modulator.ports['bottom_out'].position[1] - (self.hot_width + self.electrode_gap * 2 + self.centre_width)/2

                bottom_bend = bend_connector(delta_y = delta_y,
                                             trace_template=self.trace_template,
                                             bend_radius=self.bend_radius,
                                             length_delta=0,
                                             direction='down',
                                             name=self.name + "bottom_bend")
                instances.update({'top_bend': top_bend,
                                  'bottom_bend': bottom_bend})

            phase_shifter_pos_x = self.phase_modulator.ports['top_in'].position[0] - self.phase_shifter_electrode_separation - \
                                  self.top_phase_shifter.ports['out'].position[0]

            if self.with_delays:
                if self.delay_at_input:
                    # x position of top combiner and splitter
                    splitter_pos_x = phase_shifter_pos_x - self.top_phase_shifter.ports['in'].position[0] - self.bend_radius * 4 - \
                                     self.splitter.ports['out1'].position[0] - straight_stub_length - self.bend_to_phase_shifter_dist - (self.hot_taper_width-50)

                    # x position of bottom combiner and splitter
                    splitter_pos_x_2 = phase_shifter_pos_x - self.top_phase_shifter.ports['in'].position[
                        0] - self.bend_length - self.splitter.ports['out1'].position[0] - straight_stub_length - (self.hot_taper_width-50)

                    # x position of main splitter
                    splitter_pos_x_main = - self.top_phase_shifter.ports['in'].position[0]  - self.splitter.ports['out1'].position[0] - straight_stub_length
                else:
                    # x position of top splitter
                    splitter_pos_x = phase_shifter_pos_x - self.top_phase_shifter.ports['in'].position[0] - self.bend_length - \
                                     self.splitter.ports['out1'].position[0] - straight_stub_length - self.bend_to_phase_shifter_dist - (self.hot_taper_width-50)

                    # x position of bottom splitter
                    splitter_pos_x_2 = phase_shifter_pos_x - self.top_phase_shifter.ports['in'].position[
                        0] - self.bend_length - self.splitter.ports['out1'].position[0] - straight_stub_length - (self.hot_taper_width-50)

                    # x position of main splitter
                    splitter_pos_x_main = - self.top_phase_shifter.ports['in'].position[0] - self.splitter.ports['out1'].position[0] - straight_stub_length
            else:
                # x position of top splitter
                splitter_pos_x = phase_shifter_pos_x - self.top_phase_shifter.ports['in'].position[0] - self.bend_length - \
                                 self.splitter.ports['out1'].position[0] - straight_stub_length - (self.hot_taper_width-50)

                # x position of bottom splitter
                splitter_pos_x_2 = phase_shifter_pos_x - self.top_phase_shifter.ports['in'].position[
                    0] - self.bend_length - self.splitter.ports['out1'].position[0] - straight_stub_length - (self.hot_taper_width-50)

                # x position of main splitter
                splitter_pos_x_main = splitter_pos_x - self.splitter.ports['out1'].position[0] - self.centre_width - self.bend_length - self.hot_taper_width

            # x position of top and bottom combiners
            combiner_pos_x = self.phase_modulator.ports['top_out'].position[0] + self.bend_length - \
                             self.combiner.ports['in1'].position[0] + (self.hot_taper_width-50)

            combiner_pos_x_2 = self.phase_modulator.ports['top_out'].position[0] + self.bend_length - \
                               self.combiner.ports['in1'].position[0] + (self.hot_taper_width-50)

            # x position of main combiner
            combiner_pos_x_main = combiner_pos_x + self.bottom_phase_shifter.ports['out'].position[0] + self.centre_width + straight_stub_length + self.hot_taper_width + self.bend_length

            specs=[
                i3.Place('phase_modulator', (0, 0)),
                i3.Place('top_phase_shifter', (phase_shifter_pos_x, self.phase_modulator.ports['top_in'].position[1])),
                i3.Place('bottom_phase_shifter', (phase_shifter_pos_x, self.phase_modulator.ports['bottom_in'].position[1])),
                i3.FlipV('bottom_phase_shifter'),
                i3.Place('bottom_phase_shifter_2', (phase_shifter_pos_x, -self.phase_modulator.ports['top_in'].position[1])),
                i3.Place('top_phase_shifter_2', (phase_shifter_pos_x, -self.phase_modulator.ports['bottom_in'].position[1])),
                i3.FlipV('bottom_phase_shifter_2'),
                i3.Place('splitter', (splitter_pos_x, (self.hot_width + self.electrode_gap * 2 + self.centre_width)/2)),
                i3.Place('combiner', (combiner_pos_x, (self.hot_width + self.electrode_gap * 2 + self.centre_width)/2)),
                i3.Place('splitter_2', (splitter_pos_x_2, -(self.hot_width + self.electrode_gap * 2 + self.centre_width)/2)),
                i3.Place('combiner_2', (combiner_pos_x_2, -(self.hot_width + self.electrode_gap * 2 + self.centre_width)/2)),
                i3.FlipV('splitter_main'),
                i3.Place('combiner_main', (combiner_pos_x_main, 0)),
                i3.FlipV('combiner_main'),
                i3.FlipV("bottom_output_phase_shifter"),

                i3.Join([
                    ("combiner:out", "top_output_phase_shifter:in"),
                    ("combiner_2:out", "bottom_output_phase_shifter:in"),
                ]),
                i3.ConnectBend([
                    ("top_output_phase_shifter:out", "combiner_main:in1"),
                    ("bottom_output_phase_shifter:out", "combiner_main:in2"),
                    ],
                    bend_radius=self.bend_radius
                ),
                i3.ConnectBend([
                    ("bottom_phase_shifter:out", "phase_modulator:bottom_in"),
                    ("top_phase_shifter:out", "phase_modulator:top_in"),
                    ],
                    bend_radius=self.bend_radius
                ),
                i3.ConnectBend([
                    ("bottom_phase_shifter_2:out", "phase_modulator:bottom_in_2"),
                    ("top_phase_shifter_2:out", "phase_modulator:top_in_2"),
                ],
                    bend_radius=self.bend_radius
                )
            ]

            if self.with_delays:
                specs.append(i3.Place('splitter_main:out1', (splitter_pos_x_main, 0), relative_to='splitter:in'))
                specs.append(i3.ConnectManhattan([
                        ("splitter_main:out1", "splitter:in"),
                        ],
                        bend_radius=self.bend_radius
                    )
                )
                specs.append(i3.ConnectManhattan([
                        ("splitter_main:out2", "splitter_2:in")
                        ],
                        control_points=[i3.H(-2*self.bend_radius-10, relative_to="splitter_2:in")],
                        bend_radius=self.bend_radius
                    )
                )
            else:
                specs.append(i3.Place('splitter_main', (splitter_pos_x_main, 0)))
                specs.append(i3.ConnectBend([
                        ("splitter_main:out1", "splitter:in"),
                        ("splitter_main:out2", "splitter_2:in")
                        ],
                        bend_radius=self.bend_radius
                    )
                )

            if self.with_delays:
                if self.delay_at_input:
                    bottom_bend_pos = (splitter_pos_x + self.splitter.ports['out1'].position[0] + straight_stub_length, self.splitter.ports['out1'].position[1] + (self.hot_width + self.electrode_gap * 2 + self.centre_width)/2)
                    top_bend_pos = (splitter_pos_x + self.splitter.ports['out2'].position[0] + straight_stub_length, self.splitter.ports['out2'].position[1] + (self.hot_width + self.electrode_gap * 2 + self.centre_width)/2)

                    specs.append(i3.ConnectBend([("splitter:out1", "bottom_bend:in"),
                                                 ("splitter:out2", "top_bend:in"),
                                                 ("splitter_2:out1", "bottom_phase_shifter_2:in"),
                                                 ("splitter_2:out2", "top_phase_shifter_2:in"),
                                                 ("bottom_bend:out", "bottom_phase_shifter:in"),
                                                 ("top_bend:out", "top_phase_shifter:in"),
                                                 ],

                                                bend_radius=self.bend_radius))

                    specs.append(i3.ConnectBend([("phase_modulator:bottom_out", "combiner:in1"),
                                                 ("phase_modulator:top_out", "combiner:in2"),
                                                 ("phase_modulator:bottom_out_2", "combiner_2:in1"),
                                                 ("phase_modulator:top_out_2", "combiner_2:in2"),
                                                 ],
                                                start_straight=straight_stub_length,
                                                end_straight=straight_stub_length,
                                                bend_radius=self.bend_radius))

                else:
                    bottom_bend_pos = (self.phase_modulator.ports['bottom_out'].position[0] + straight_stub_length, self.phase_modulator.ports['bottom_out'].position[1] + (self.hot_width + self.electrode_gap * 2 + self.centre_width)/2)
                    top_bend_pos = (self.phase_modulator.ports['top_out'].position[0] + straight_stub_length, self.phase_modulator.ports['top_out'].position[1] + (self.hot_width + self.electrode_gap * 2 + self.centre_width)/2)

                    specs.append(i3.ConnectBend([("splitter:out1", "bottom_phase_shifter:in"),
                                                 ("splitter:out2", "top_phase_shifter:in"),
                                                 ("splitter_2:out1", "bottom_phase_shifter_2:in"),
                                                 ("splitter_2:out2", "top_phase_shifter_2:in"),
                                                 ],
                                                start_straight=straight_stub_length,
                                                end_straight=straight_stub_length,
                                                bend_radius=self.bend_radius))

                    specs.append(i3.ConnectBend([("phase_modulator:bottom_out", "bottom_bend:in"),
                                                 ("phase_modulator:top_out", "top_bend:in"),
                                                 ("bottom_bend:out", "combiner:in1"),
                                                 ("top_bend:out", "combiner:in2"),
                                                 ("phase_modulator:bottom_out_2", "combiner_2:in1"),
                                                 ("phase_modulator:top_out_2", "combiner_2:in2"),
                                                 ],

                                                bend_radius=self.bend_radius))

                specs.append(i3.Place('bottom_bend', bottom_bend_pos))
                specs.append(i3.Place('top_bend', top_bend_pos))

            else:
                specs.append(i3.ConnectBend([("splitter:out1", "bottom_phase_shifter:in"),
                                             ("splitter:out2", "top_phase_shifter:in"),
                                             ("splitter_2:out1", "bottom_phase_shifter_2:in"),
                                             ("splitter_2:out2", "top_phase_shifter_2:in"),
                                             ("phase_modulator:bottom_out", "combiner:in1"),
                                             ("phase_modulator:top_out", "combiner:in2"),
                                             ("phase_modulator:bottom_out_2", "combiner_2:in1"),
                                             ("phase_modulator:top_out_2", "combiner_2:in2"),
                                             ],
                                            start_straight=straight_stub_length,
                                            end_straight=straight_stub_length,
                                            bend_radius=self.bend_radius))

            insts += i3.place_and_route(instances, specs=specs)

            return insts

        def _generate_ports(self, ports):
            # main splitter
            ports += i3.expose_ports(self.instances, {'splitter_main:in': 'in'})

            # main combiner
            ports += i3.expose_ports(self.instances, {'combiner_main:out': 'out'})

            # top path input phase shifters
            ports += i3.expose_ports(self.instances, {'top_phase_shifter:m1': 'in1_m1_1'})
            ports += i3.expose_ports(self.instances, {'top_phase_shifter:m2': 'in1_m1_2'})
            ports += i3.expose_ports(self.instances, {'bottom_phase_shifter:m1': 'in1_m2_1'})
            ports += i3.expose_ports(self.instances, {'bottom_phase_shifter:m2': 'in1_m2_2'})

            # bottom path input phase shifters
            ports += i3.expose_ports(self.instances, {'top_phase_shifter_2:m1': 'in2_m1_1'})
            ports += i3.expose_ports(self.instances, {'top_phase_shifter_2:m2': 'in2_m1_2'})
            ports += i3.expose_ports(self.instances, {'bottom_phase_shifter_2:m1': 'in2_m2_1'})
            ports += i3.expose_ports(self.instances, {'bottom_phase_shifter_2:m2': 'in2_m2_2'})

            # output phase shifters
            ports += i3.expose_ports(self.instances, {'top_output_phase_shifter:m1': 'out_m1_1'})
            ports += i3.expose_ports(self.instances, {'top_output_phase_shifter:m2': 'out_m1_2'})
            ports += i3.expose_ports(self.instances, {'bottom_output_phase_shifter:m1': 'out_m2_1'})
            ports += i3.expose_ports(self.instances, {'bottom_output_phase_shifter:m2': 'out_m2_2'})

            # phase modulator (dual mzm)
            ports += i3.expose_ports(self.instances, {'phase_modulator:top_ground': 'top_ground',
                                                        'phase_modulator:top_signal': 'top_signal',
                                                        'phase_modulator:middle_ground': 'middle_ground',
                                                        'phase_modulator:bottom_signal': 'bottom_signal',
                                                        'phase_modulator:bottom_ground': 'bottom_ground',
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

