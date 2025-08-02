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

"""In this simulation program, PPC loads a linear change voltage"""

from ipkiss3 import all as i3
import numpy as np


def simulate_ppc_unit_linear_voltages(
    cell,
    v_start=0.0,
    v_end=5.0,
    v_num=1000,
    center_wavelength=1.55,
    debug=False,
):
    dt = 1e-12  # time step
    t0 = 0e-12  # start time
    t1 = v_num * 1e-12  # end time

    # define optical source
    optical_in = i3.FunctionExcitation(
        port_domain=i3.OpticalDomain,
        excitation_function=lambda t: 1,
    )

    # define electrical source
    def linear_ramp(t):
        return v_end * t / t1 + v_start * (t1 - t) / t1

    electrical_in = i3.FunctionExcitation(
        port_domain=i3.ElectricalDomain,
        excitation_function=linear_ramp,
    )
    gnd = i3.FunctionExcitation(
        port_domain=i3.ElectricalDomain,
        excitation_function=lambda t: 0,
    )
    # Define the child cells and links (direct connections)
    child_cells = {
        "DUT": cell,
        "optical_in": optical_in,
        "ht": electrical_in,
        "gnd": gnd,
        "out1": i3.Probe(port_domain=i3.OpticalDomain),
        "out2": i3.Probe(port_domain=i3.OpticalDomain),
    }
    links = [
        ("optical_in:out", "DUT:in1"),
        ("ht:out", "DUT:ht1"),
        ("gnd:out", "DUT:ht2"),
        ("out1:in", "DUT:out1"),
        ("out2:in", "DUT:out2"),
    ]
    testbench = i3.ConnectComponents(
        child_cells=child_cells,
        links=links,
    )
    # get time simulation results
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


def get_volts_for_specific_transmission(trans_search, v_start, v_end, raw_volts, raw_trans):
    from scipy import interpolate
    from scipy.optimize import minimize
    from scipy.signal import argrelextrema

    # remove the singular point
    volts = raw_volts
    trans = raw_trans
    max_trans = max(trans)
    min_trans = min(trans)

    if min_trans < trans_search < max_trans:
        target = trans_search

    # search maximum transmission fix
    elif i3.isclose(trans_search, max_trans):
        target = trans_search - 0.0001

    # search minimum transmission fix
    elif i3.isclose(trans_search, min_trans):
        target = trans_search + 0.0001

    else:
        raise ValueError("The transmission you needed is out of the region, please try again!")

    # find the index of peak and dip in transmission list
    peak_index = argrelextrema(trans, np.greater)
    dip_index = argrelextrema(trans, np.less)

    v_peak = [volts[index] for index in peak_index]
    v_dip = [volts[index] for index in dip_index]
    v_total = [v_start] + v_peak[0].tolist() + v_dip[0].tolist() + [v_end]
    v_total.sort()  # ascending order

    bounds_lst = [(v_total[i - 1], v_total[i]) for i in range(1, len(v_total))]
    f = interpolate.interp1d(volts, trans, kind=3)

    # search the volts for specific transmission
    cons = {"type": "ineq", "fun": lambda x: f(x) - target}  # set the optimization condition
    res_lst = []
    # find the index of the trans which is closed to the trans_search, the index same with the volts
    temp_index = np.where((target - 0.1 < trans) & (trans < target + 0.1))

    for bound in bounds_lst:
        # to find the approximate volt in each bound so that make sure the optimization result correctly
        temp_volts = []
        for tmpidx in temp_index[0]:
            if bound[0] <= volts[tmpidx] <= bound[1]:
                temp_volts.append(volts[tmpidx])
        x0 = max(temp_volts)

        # optimization
        res = minimize(f, x0=x0, bounds=[bound], constraints=cons, tol=1e-12)
        res_lst.append(res.x[0])

    return res_lst


def get_volts_for_min_mid_max(raw_volts, raw_trans, clip_points):
    from scipy import interpolate
    from scipy.signal import find_peaks

    volts = raw_volts[clip_points::]
    trans = raw_trans[clip_points::]

    f = interpolate.interp1d(volts, trans, kind=3)

    # find the indices of peaks and dips in transmission list
    v_peak = [volts[index] for index in find_peaks(trans)[0]]
    v_dip = [volts[index] for index in find_peaks(-trans)[0]]

    v_dip_fine = []
    for v_center in v_dip:
        v_delta = volts[1] - volts[0]
        v_0 = v_center
        v_0_diff = 1.0
        counter = 0
        while v_0_diff > 1e-8 and counter <= 100:
            v_interp = v_0 + v_delta * np.linspace(-1.0, 1.0, 1001)
            f_interp = f(v_interp)
            v_0_old = v_interp[np.where(f_interp == np.min(f_interp))[0][0]]
            v_0_diff = np.abs(v_0 - v_0_old)
            v_0 = v_0_old
            counter += 1
        if counter < 100:
            v_dip_fine.append(v_0)

    v_peak_fine = []
    for v_center in v_peak:
        v_delta = volts[1] - volts[0]
        v_0 = v_center
        v_0_diff = 1.0
        counter = 0
        while v_0_diff > 1e-8 and counter <= 100:
            v_interp = v_0 + v_delta * np.linspace(-1.0, 1.0, 1001)
            f_interp = f(v_interp)
            v_0_old = v_interp[np.where(f_interp == np.max(f_interp))[0][0]]
            v_0_diff = np.abs(v_0 - v_0_old)
            v_0 = v_0_old
            counter += 1
        if counter < 100:
            v_peak_fine.append(v_0)

    v_total = v_peak_fine + v_dip_fine
    v_total.sort()
    f_vals = f(v_total[0:2])
    if f_vals[1] > f_vals[0]:
        f_min, f_max = f_vals[0], f_vals[1]
        v_min, v_max = v_total[0], v_total[1]
    else:
        f_min, f_max = f_vals[1], f_vals[0]
        v_min, v_max = v_total[1], v_total[0]

    v_delta = (v_total[1] - v_total[0]) * 0.5
    v_0 = (v_total[0] + v_total[1]) * 0.5
    v_0_diff = 1.0
    while v_0_diff > 1e-8:
        v_interp = v_0 + v_delta * np.linspace(-1.0, 1.0, 1001)
        f_interp = f(v_interp)
        value_mid = np.abs(f_interp - 0.5 * (f_max + f_min))
        v_0_old = v_interp[np.where(value_mid == np.min(value_mid))[0][0]]
        v_0_diff = np.abs(v_0 - v_0_old)
        v_0 = v_0_old

    v_mid = v_0
    f_mid = f(v_mid)

    return [v_min, v_mid, v_max], [f_min, f_mid, f_max]
