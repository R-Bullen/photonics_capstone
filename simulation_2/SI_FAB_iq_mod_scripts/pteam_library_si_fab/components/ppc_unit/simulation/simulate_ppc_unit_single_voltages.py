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

"""In this simulation program, ppu unit loads a fixed voltage"""
from ipkiss3 import all as i3


def simulate_ppc_unit_single_voltages(cell, volts=5, center_wavelength=1.55, debug=False):
    dt = 1e-12  # time step
    t0 = 0e-12  # start time
    t1 = 50 * 1e-12  # end time

    # Define optical source
    optical_in = i3.FunctionExcitation(
        port_domain=i3.OpticalDomain,
        excitation_function=lambda t: 1.0,
    )

    # Define electrical source
    electrical_in = i3.FunctionExcitation(
        port_domain=i3.ElectricalDomain,
        excitation_function=lambda t: volts,
    )

    # Define the child cells and links (direct connections)
    child_cells = {
        "DUT": cell,
        "optical_in": optical_in,
        "ht": electrical_in,
        "out1": i3.Probe(port_domain=i3.OpticalDomain),
        "out2": i3.Probe(port_domain=i3.OpticalDomain),
    }
    links = [("optical_in:out", "DUT:in1"), ("ht:out", "DUT:ht1"), ("out1:in", "DUT:out1"), ("out2:in", "DUT:out2")]

    # Build the testbench and run the time simulation
    testbench = i3.ConnectComponents(
        child_cells=child_cells,
        links=links,
    )
    cm = testbench.CircuitModel()
    results = cm.get_time_response(
        t0=t0,
        t1=t1,
        dt=dt,
        center_wavelength=center_wavelength,
        debug=debug,
    )
    results.timesteps = results.timesteps[8:]
    results.data = results.data[0:, 8:]
    return results
