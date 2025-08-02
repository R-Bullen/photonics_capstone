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

from ipkiss3 import all as i3

input_term_names = [
    "H1_pad",
    "G1_pad",
    "SL_pad",
    "G2_pad",
    "SR_pad",
    "G3_pad",
    "H2_pad",
]
output_term_names = [
    "pmod1_anode",
    "pmod1_cathode",
    "pmod2_anode",
    "pmod2_cathode",
    "h1_elec1",
    "h1_elec2",
    "h2_elec1",
    "h2_elec2",
]

term_names = input_term_names + output_term_names
term_list = [i3.ElectricalTerm(name=tn) for tn in term_names]


class ElHubModel(i3.CompactModel):
    """Model for the electrical hub."""

    terms = term_list

    def calculate_signals(parameters, env, output_signals, y, t, input_signals):
        output_signals["pmod1_cathode"] = input_signals["SL_pad"]
        output_signals["pmod2_cathode"] = input_signals["SR_pad"]
        output_signals["pmod1_anode"] = input_signals["G2_pad"]
        output_signals["pmod2_anode"] = input_signals["G2_pad"]
        output_signals["h1_elec1"] = input_signals["H1_pad"]
        output_signals["h1_elec2"] = input_signals["G2_pad"]
        output_signals["h2_elec1"] = input_signals["H2_pad"]
        output_signals["h2_elec2"] = input_signals["G2_pad"]


class ElHub(i3.PCell):
    """Electrical hub."""

    class Netlist(i3.NetlistView):
        def _generate_netlist(self, netlist):
            netlist += term_list
            return netlist

    class CircuitModel(i3.CircuitModelView):
        def _generate_model(self):
            return ElHubModel()
