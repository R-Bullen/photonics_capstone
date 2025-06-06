# Copyright (C) 2020-2024 Luceda Photonics

"""
Set up a testbench for an IQ modulator.
"""

import random

import numpy as np

import ipkiss3.all as i3
from simulation.benches.sources import random_bitsource, rand_normal


def simulate_modulation_iqmod(
    cell,
    mod_amplitude_i=None,
    mod_noise_i=None,
    mod_amplitude_q=None,
    mod_noise_q=None,
    opt_amplitude=None,
    opt_noise=None,
    v_heater_i=None,
    v_heater_q=None,
    v_mzm_left1=None,
    v_mzm_left2=None,
    v_mzm_right1=None,
    v_mzm_right2=None,
    bit_rate=10e9,
    n_bytes=100,
    steps_per_bit=50,
    center_wavelength=1.5,
    debug=False,
):
    """
    Simulation recipe to simulate an IQ modulator.

    Parameters
    ----------
    cell : i3.PCell
        pcells of the IQ modulator to be simulated.
    mod_amplitude_i : float
        Amplitude of the modulator.
    mod_noise_i : float
        Amplitude of the noise of the modulator signal.
    mod_amplitude_q : float
        Amplitude of the modulator.
    mod_noise_q : float
        Amplitude of the noise of the modulator signal.
    opt_amplitude : float
        Amplitude of the input optical signal.
    opt_noise : float
        Amplitude of the noise at the optical input.
    v_heater_i : float
        Voltage on the left heater [V].
    v_heater_q : float
        Voltage on the right heater [V].
    v_mzm_left1 : float
        Voltage on the first heater (left) [V].
    v_mzm_left2 : float
        Voltage on the second heater (left) [V].
    v_mzm_right1 : float
        Voltage on the first heater (right) [V].
    v_mzm_right2 : float
        Voltage on the second heater (right) [V].
    bit_rate : float
        Bit rate of the signal.
    n_bytes : int
        Number of bytes of the simulation.
    steps_per_bit : int
        Number of time steps per bit.
    center_wavelength : float
        Center wavelength of the optical carrier.
    debug : bool
        If True, the simulation is run in debug mode.

    Returns
    -------
    Dictionary of simulated signals.

    """

    # Define the excitations with noise on the electrical
    f_mod_i = random_bitsource(
        bitrate=bit_rate,
        amplitude=mod_amplitude_i,
        n_bytes=n_bytes,
    )
    f_mod_q = random_bitsource(
        bitrate=bit_rate,
        amplitude=mod_amplitude_q,
        n_bytes=n_bytes,
    )
    rand_normal_dist = rand_normal()
    src_in = i3.FunctionExcitation(
        port_domain=i3.OpticalDomain, excitation_function=lambda t: opt_amplitude + rand_normal_dist(opt_noise)
    )
    signal_i = i3.FunctionExcitation(
        port_domain=i3.ElectricalDomain, excitation_function=lambda t: f_mod_i(t) + rand_normal_dist(mod_noise_i)
    )
    revsignal_i = i3.FunctionExcitation(
        port_domain=i3.ElectricalDomain, excitation_function=lambda t: -f_mod_i(t) - rand_normal_dist(mod_noise_i)
    )
    signal_q = i3.FunctionExcitation(
        port_domain=i3.ElectricalDomain, excitation_function=lambda t: f_mod_q(t) + rand_normal_dist(mod_noise_q)
    )
    revsignal_q = i3.FunctionExcitation(
        port_domain=i3.ElectricalDomain, excitation_function=lambda t: -f_mod_q(t) - rand_normal_dist(mod_noise_q)
    )
    heater_i = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: v_heater_i)
    heater_q = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: v_heater_q)
    mzm_left1 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: v_mzm_left1)
    mzm_left2 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: v_mzm_left2)
    mzm_right1 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: v_mzm_right1)
    mzm_right2 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: v_mzm_right2)
    gnd1 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd2 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd3 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd4 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd5 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd6 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)

    t0 = 0.0
    t1 = n_bytes / bit_rate
    dt = t1 / n_bytes / steps_per_bit

    testbench = i3.ConnectComponents(
        child_cells={
            "DUT": cell,
            "out": i3.Probe(port_domain=i3.OpticalDomain),
            "src_in": src_in,
            "sig_i": signal_i,
            "revsig_i": revsignal_i,
            "sig_q": signal_q,
            "revsig_q": revsignal_q,
            "gnd1": gnd1,
            "gnd2": gnd2,
            "gnd3": gnd3,
            "gnd4": gnd4,
            "gnd5": gnd5,
            "gnd6": gnd6,
            "ht_i": heater_i,
            "ht_q": heater_q,
            # "mzm_left1": mzm_left1,
            # "mzm_left2": mzm_left2,
            # "mzm_right1": mzm_right1,
            # "mzm_right2": mzm_right2,
        },
        links=[
            ("src_in:out", "DUT:in"),
            ("DUT:out", "out:in"),
            ("DUT:in2_m2_1", "ht_i:out"),
            ("DUT:out_m2_1", "ht_q:out"),
            # ("DUT:mzmi0", "mzm_left1:out"),
            # ("DUT:mzmo0", "mzm_left2:out"),
            # ("DUT:mzmi1", "mzm_right1:out"),
            # ("DUT:mzmo1", "mzm_right2:out"),
            ("DUT:top_signal", "sig_i:out"),
            # ("DUT:top_signal", "revsig_i:out"),
            ("DUT:bottom_signal", "sig_q:out"),
            # ("DUT:bottom_signal", "revsig_q:out"),
            # ("DUT:in2_m2_2", "gnd1:out"),
            ("DUT:out_m2_2", "gnd2:out"),
            ("DUT:top_ground", "gnd3:out"),
            ("DUT:middle_ground", "gnd4:out"),
            # ("DUT:middle_ground", "gnd5:out"),
            ("DUT:bottom_ground", "gnd6:out"),
        ],
    )

    testbench_model = testbench.CircuitModel()
    results = testbench_model.get_time_response(
        t0=t0,
        t1=t1,
        dt=dt,
        center_wavelength=center_wavelength,
        debug=debug,
    )
    return results


def result_modified_QPSK(result):
    results_rotation = []
    res_sample = random.sample(list(result["out"]), 200)
    for res in res_sample:
        if np.angle(res) > 0 and np.angle(res) < np.pi / 2:
            results_rotation.append(res * np.exp(1j * (np.pi / 4 - np.angle(res))))
        elif np.angle(res) > np.pi / 2 and np.angle(res) < np.pi:
            results_rotation.append(res * np.exp(1j * (np.pi * 3 / 4 - np.angle(res))))
        elif np.angle(res) > -np.pi and np.angle(res) < -np.pi / 2:
            results_rotation.append(res * np.exp(1j * (np.pi * 5 / 4 - np.angle(res))))
        elif np.angle(res) > -np.pi / 2 and np.angle(res) < 0:
            results_rotation.append(res * np.exp(1j * (-np.pi / 4 - np.angle(res))))

    return results_rotation


def result_modified_PAM4(result):
    res_sample = random.sample(list(result["out"]), 200)

    return [res * np.exp(-1j * np.angle(res)) for res in res_sample]
