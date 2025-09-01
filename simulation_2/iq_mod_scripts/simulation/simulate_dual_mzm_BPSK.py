# Copyright (C) 2020-2024 Luceda Photonics

"""
Set up a testbench for an IQ modulator working in QAM modulation format.
"""

import random

import numpy as np

import ipkiss3.all as i3
from si_fab.benches.sources import random_bitsource, rand_normal


def simulate_dual_mzm_BPSK(
    cell,
    mod_amplitude_i=None,
    mod_noise_i=None,
    mod_amplitude_q=None,
    mod_noise_q=None,
    opt_amplitude=None,
    opt_noise=None,
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
    src_in_1 = i3.FunctionExcitation(
        port_domain=i3.OpticalDomain, excitation_function=lambda t: opt_amplitude + rand_normal_dist(opt_noise)
    )
    src_in_2 = i3.FunctionExcitation(
        port_domain=i3.OpticalDomain, excitation_function=lambda t: opt_amplitude + rand_normal_dist(opt_noise)
    )
    src_in_3 = i3.FunctionExcitation(
        port_domain=i3.OpticalDomain, excitation_function=lambda t: opt_amplitude + rand_normal_dist(opt_noise)
    )
    src_in_4 = i3.FunctionExcitation(
        port_domain=i3.OpticalDomain, excitation_function=lambda t: opt_amplitude + rand_normal_dist(opt_noise)
    )
    signal_i = i3.FunctionExcitation(
        port_domain=i3.ElectricalDomain, excitation_function=lambda t: f_mod_i(t) + rand_normal_dist(mod_noise_i)
    )
    signal_q = i3.FunctionExcitation(
        port_domain=i3.ElectricalDomain, excitation_function=lambda t: f_mod_q(t) + rand_normal_dist(mod_noise_q)
    )
    gnd1 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd2 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd3 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd4 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd5 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd6 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd7 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd8 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd9 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)

    t0 = 0.0
    t1 = n_bytes / bit_rate
    dt = t1 / n_bytes / steps_per_bit

    testbench = i3.ConnectComponents(
        child_cells={
            "DUT": cell,
            "out_1": i3.Probe(port_domain=i3.OpticalDomain),
            "out_2": i3.Probe(port_domain=i3.OpticalDomain),
            "out_3": i3.Probe(port_domain=i3.OpticalDomain),
            "out_4": i3.Probe(port_domain=i3.OpticalDomain),
            "src_in_1": src_in_1,
            "src_in_2": src_in_2,
            "src_in_3": src_in_3,
            "src_in_4": src_in_4,
            "sig_i": signal_i,
            "sig_q": signal_q,
            "gnd7": gnd6,
            "gnd8": gnd8,
            "gnd9": gnd9,
        },
        links=[
            ("src_in_1:out", "DUT:top_in"),
            ("src_in_2:out", "DUT:bottom_in"),
            ("src_in_3:out", "DUT:top_in_2"),
            ("src_in_4:out", "DUT:bottom_in_2"),
            ("DUT:top_out", "out_1:in"),
            ("DUT:bottom_out", "out_2:in"),
            ("DUT:top_out_2", "out_3:in"),
            ("DUT:bottom_out_2", "out_4:in"),
            ("DUT:top_signal", "sig_i:out"),
            ("DUT:bottom_signal", "sig_q:out"),
            ("DUT:top_ground", "gnd7:out"),
            ("DUT:middle_ground", "gnd8:out"),
            ("DUT:bottom_ground", "gnd9:out"),
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

def result_modified_BPSK_1(result):
    results_rotation = []
    res_sample = random.sample(list(result["out_1"]), 200)
    for res in res_sample:
        if np.angle(res) > 0 and np.angle(res) < np.pi / 2:
            results_rotation.append(res * np.exp(-1j * np.angle(res)))
        elif np.angle(res) > np.pi / 2 and np.angle(res) < np.pi:
            results_rotation.append(res * np.exp(-1j * (np.angle(res) - np.pi)))
        elif np.angle(res) > -np.pi and np.angle(res) < -np.pi / 2:
            results_rotation.append(res * np.exp(-1j * (np.angle(res) - np.pi)))
        elif np.angle(res) > -np.pi / 2 and np.angle(res) < 0:
            results_rotation.append(res * np.exp(-1j * np.angle(res)))

    return results_rotation

def result_modified_BPSK_2(result):
    results_rotation = []
    res_sample = random.sample(list(result["out_2"]), 200)
    for res in res_sample:
        if np.angle(res) > 0 and np.angle(res) < np.pi / 2:
            results_rotation.append(res * np.exp(-1j * np.angle(res)))
        elif np.angle(res) > np.pi / 2 and np.angle(res) < np.pi:
            results_rotation.append(res * np.exp(-1j * (np.angle(res) - np.pi)))
        elif np.angle(res) > -np.pi and np.angle(res) < -np.pi / 2:
            results_rotation.append(res * np.exp(-1j * (np.angle(res) - np.pi)))
        elif np.angle(res) > -np.pi / 2 and np.angle(res) < 0:
            results_rotation.append(res * np.exp(-1j * np.angle(res)))

    return results_rotation

def result_modified_BPSK_3(result):
    results_rotation = []
    res_sample = random.sample(list(result["out_3"]), 200)
    for res in res_sample:
        if np.angle(res) > 0 and np.angle(res) < np.pi / 2:
            results_rotation.append(res * np.exp(-1j * np.angle(res)))
        elif np.angle(res) > np.pi / 2 and np.angle(res) < np.pi:
            results_rotation.append(res * np.exp(-1j * (np.angle(res) - np.pi)))
        elif np.angle(res) > -np.pi and np.angle(res) < -np.pi / 2:
            results_rotation.append(res * np.exp(-1j * (np.angle(res) - np.pi)))
        elif np.angle(res) > -np.pi / 2 and np.angle(res) < 0:
            results_rotation.append(res * np.exp(-1j * np.angle(res)))

    return results_rotation

def result_modified_BPSK_4(result):
    results_rotation = []
    res_sample = random.sample(list(result["out_4"]), 200)
    for res in res_sample:
        if np.angle(res) > 0 and np.angle(res) < np.pi / 2:
            results_rotation.append(res * np.exp(-1j * np.angle(res)))
        elif np.angle(res) > np.pi / 2 and np.angle(res) < np.pi:
            results_rotation.append(res * np.exp(-1j * (np.angle(res) - np.pi)))
        elif np.angle(res) > -np.pi and np.angle(res) < -np.pi / 2:
            results_rotation.append(res * np.exp(-1j * (np.angle(res) - np.pi)))
        elif np.angle(res) > -np.pi / 2 and np.angle(res) < 0:
            results_rotation.append(res * np.exp(-1j * np.angle(res)))

    return results_rotation
