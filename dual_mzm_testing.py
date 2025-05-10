import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3

from dual_mzm import DualMZM2x2


if __name__ == '__main__':
    dual_mzm = DualMZM2x2()
    dual_mzm.Layout().visualize(annotate=True)
