# Copyright (C) 2020-2024 Luceda Photonics

"""
Set up a testbench for an IQ modulator working in QAM modulation format.
"""

import random

import numpy as np

import ipkiss3.all as i3
from si_fab.benches.sources import random_bitsource, rand_normal


def simulate_modulation_PAM4(
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
    signal_q = i3.FunctionExcitation(
        port_domain=i3.ElectricalDomain, excitation_function=lambda t: f_mod_q(t) + rand_normal_dist(mod_noise_q)
    )
    # heater_i = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: v_heater_i)
    heater_q = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: v_heater_q)
    # mzm_left1 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: v_mzm_left1)
    # mzm_left2 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: v_mzm_left2)
    # mzm_right1 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: v_mzm_right1)
    mzm_right2 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: v_mzm_right2)
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
            "src_in": src_in,
            "out": i3.Probe(port_domain=i3.OpticalDomain),

            "ps_q_out": heater_q,
            "gnd1": gnd1,
            "ps_q_in": mzm_right2,

            "gnd2": gnd2,
            "sig_i": signal_i,
            "gnd3": gnd3,
            "sig_q": signal_q,
            "gnd4": gnd4,

            # unused gcs
            "gc_0": src_in,
            "gc_7": src_in,
            "gc_1": src_in,
            "gc_6": src_in,
            "gc_2": src_in,
            "gc_5": src_in,
        },
        links=[
            ("src_in:out", "DUT:in"),
            ("DUT:out", "out:in"),

            ("DUT:pad_ps_in", "ps_q_in:out"),
            ("DUT:pad_gnd", "gnd1:out"),
            ("DUT:pad_ps_out", "ps_q_out:out"),

            ("DUT:top_ground", "gnd2:out"),
            ("DUT:top_signal", "sig_i:out"),
            ("DUT:middle_ground", "gnd3:out"),
            ("DUT:bottom_signal", "sig_q:out"),
            ("DUT:bottom_ground", "gnd4:out"),

            # unused gcs
            ("DUT:gc_0", "gc_0:out"),
            ("DUT:gc_1", "gc_1:out"),
            ("DUT:gc_2", "gc_2:out"),
            ("DUT:gc_5", "gc_5:out"),
            ("DUT:gc_6", "gc_6:out"),
            ("DUT:gc_7", "gc_7:out"),
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

def result_modified_PAM4(result, samples_per_symbol=2**6, sampling_point=0.5):
    res_sample = result["out"][int(samples_per_symbol * (10 + sampling_point))::samples_per_symbol]

    return [res * np.exp(-1j * np.angle(res)) for res in res_sample]

