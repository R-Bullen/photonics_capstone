import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3

from deprecated.mzm_custom import MZModulator1x1 as CustomMZModulator1x1

# MMI1x2 -> MZM           -> MMI2x1
#        -> MZM (shifted) ->

class MZMTesting(i3.Circuit):
    """
    MZM testing class
    """
    spacing_x = i3.PositiveNumberProperty(default=425.0, doc="Horizontal spacing between the splitter levels.")
    spacing_y = i3.PositiveNumberProperty(default=125.0, doc="Vertical spacing between the splitters in each level.")

    def _default_insts(self):
        mzm_top = CustomMZModulator1x1(with_delays=True, bend_to_phase_shifter_dist=1000)

        insts = {
            "mzm_0": mzm_top,
        }

        return insts

    def _default_specs(self):
        specs = [
            i3.Place("mzm_0:in", (0, 0)),
            i3.FlipV("mzm_0"),
        ]

        return specs


# mzm = pdk.MZModulator1x1()
# mzm.Layout().visualize(annotate=True)
if __name__ == '__main__':
    test_mzm = MZMTesting()
    test_mzm.Layout().visualize(annotate=True)
