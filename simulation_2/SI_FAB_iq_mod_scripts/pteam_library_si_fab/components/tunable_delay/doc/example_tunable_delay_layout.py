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

from si_fab import technology
from pteam_library_si_fab.components.tunable_delay.pcell.cell import TunableDelayLine


delay_time = 1.4

tunable_delay = TunableDelayLine(delay_time=delay_time, n_o_loops=10, x_distance_spiral=750)
tunable_delay_lv = tunable_delay.Layout()
tunable_delay_lv.visualize()
