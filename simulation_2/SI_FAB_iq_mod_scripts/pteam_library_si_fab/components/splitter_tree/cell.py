# Copyright (C) 2020 Luceda Photonics
# This version of Luceda Academy and related packages
# (hereafter referred to as Luceda Academy) is distributed under a proprietary License by Luceda
# It does allow you to develop and distribute add-ons or plug-ins, but does
# not allow redistribution of Luceda Academy  itself (in original or modified form).
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
#
# For the details of the licensing contract and the conditions under which
# you may use this software, we refer to the
# EULA which was distributed along with this program.
# It is located in the root of the distribution folder.

from si_fab import all as pdk
from ipkiss3 import all as i3


class SplitterTree(i3.Circuit):
    """This creates a splitter tree PCell, made of 1x2 splitter elements.

    Users can specify the number of tree levels as PCell parameter.
    """

    splitter = i3.ChildCellProperty(doc="Splitter used")
    levels = i3.IntProperty(default=3, doc="Number of levels")
    spacing_x = i3.PositiveNumberProperty(
        default=100.0, doc="Spacing between the splitters in x-direction in the last level"
    )
    spacing_y = i3.PositiveNumberProperty(default=50.0, doc="Spacing in y-direction")
    bend_radius = i3.PositiveNumberProperty()

    def _default_bend_radius(self):
        return 5.0

    def _default_splitter(self):
        return pdk.MMI1x2Optimized1550()

    def _default_insts(self):
        insts = dict()
        for level in range(self.levels):
            for sp in range(int(2**level)):
                insts["sp_{}_{}".format(level, sp)] = self.splitter

        return insts

    def _default_specs(self):
        specs = []
        for level in range(self.levels):
            for sp in range(int(2**level)):
                sp_y = self.spacing_y * 2 ** (self.levels - level - 1)
                specs.append(
                    i3.Place(
                        "sp_{}_{}".format(level, sp),
                        (level * self.spacing_x, -0.5 * (2**level - 1) * sp_y + sp * sp_y),
                    )
                )

        for level in range(1, self.levels):
            for sp in range(int(2**level)):
                if sp % 2 == 0:
                    in_port = "sp_{}_{}:out1".format(level - 1, int(sp / 2.0))
                else:
                    in_port = "sp_{}_{}:out2".format(level - 1, int(sp / 2.0))

                out_port = "sp_{}_{}:in1".format(level, sp)

                specs.append(i3.ConnectManhattan(in_port, out_port, bend_radius=self.bend_radius))

        return specs

    def _default_exposed_ports(self):
        exposed_ports = dict()
        cnt = 1
        level = self.levels - 1
        for sp in range(int(2**level)):
            exposed_ports["sp_{}_{}:out1".format(level, sp)] = "out{}".format(cnt)
            cnt = cnt + 1
            exposed_ports["sp_{}_{}:out2".format(level, sp)] = "out{}".format(cnt)
            cnt = cnt + 1

        exposed_ports["sp_{}_{}:in1".format(0, 0)] = "in"
        return exposed_ports
