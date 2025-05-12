import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3

from dual_mzm import DualMZM1x1


if __name__ == '__main__':
    dual_mzm = DualMZM1x1(bend_to_phase_shifter_dist=500, with_delays=True)
    dual_mzm.Layout().visualize(annotate=True)
