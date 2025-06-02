# Adapt from Luceda Academy design example

"""
Set up a testbench for an 1x1 MZM.
"""

import random

import numpy as np

import ipkiss3.all as i3
from simulation.benches.sources import random_bitsource, rand_normal

def simulate_modulation_mzm(
    cell,
    mod_amplitude=None,
    mod_noise=None,
    opt_amplitude=None,
    opt_noise=None,
    v_mzm1=None,
    v_mzm2=None,
    bit_rate=10e9,
    n_bytes=100,
    steps_per_bit=50,
    center_wavelength=1.5,
    debug=False,
):
    """
    Simulation recipe to simulate an MZ modulator.

    Parameters
    ----------
    cell : i3.PCell
        pcells of the IQ modulator to be simulated.
    mod_amplitude : float
        Amplitude of the modulator.
    mod_noise : float
        Amplitude of the noise of the modulator signal.
    opt_amplitude : float
        Amplitude of the input optical signal.
    opt_noise : float
        Amplitude of the noise at the optical input.
    v_mzm1 : float
        Voltage on the first heater (left) [V].
    v_mzm2 : float
        Voltage on the second heater (left) [V].
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
    f_mod = random_bitsource(
        bitrate=bit_rate,
        amplitude=mod_amplitude,
        n_bytes=n_bytes,
    )
    rand_normal_dist = rand_normal()
    src_in = i3.FunctionExcitation(
        port_domain=i3.OpticalDomain, excitation_function=lambda t: opt_amplitude + rand_normal_dist(opt_noise)
    )
    signal = i3.FunctionExcitation(
        port_domain=i3.ElectricalDomain, excitation_function=lambda t: f_mod(t) + rand_normal_dist(mod_noise)
    )
    
    mzm1 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: v_mzm1)
    mzm2 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: v_mzm2)
    mzm1_gnd = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    mzm2_gnd = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd1 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd2 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    
    t0 = 0.0
    t1 = n_bytes / bit_rate
    dt = t1 / n_bytes / steps_per_bit
    # Testbench
    testbench = i3.ConnectComponents(
        child_cells={
            "DUT": cell,
            "out": i3.Probe(port_domain=i3.OpticalDomain),
            "src_in": src_in,
            "sig": signal,
            "gnd1": gnd1,
            "gnd2": gnd2,
            "mzm1": mzm1,
            "mzm2": mzm2,
            "mzm1_gnd": mzm1_gnd,
            "mzm2_gnd": mzm2_gnd,
        },
        links=[
            ("src_in:out", "DUT:in"),
            ("DUT:out", "out:in"),
            ("DUT:m1_1", "mzm1:out"),
            ("DUT:m1_2", "mzm1_gnd:out"),
            ("DUT:m2_1", "mzm2:out"),
            ("DUT:m2_2", "mzm2_gnd:out"),
            ("DUT:signal", "sig:out"),
            ("DUT:ground_1", "gnd1:out"),
            ("DUT:ground_2", "gnd2:out")
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



def simulate_modulation_PAM4(
    cell,
    mod_amplitude=None,
    mod_noise=None,
    opt_amplitude=None,
    opt_noise=None,
    v_mzm1=None,
    v_mzm2=None,
    symbol_rate=10e9,
    n_bytes=100,
    steps_per_symbol=50,
    center_wavelength=1.5,
    debug=False,
):
    """
    Simulation recipe to simulate an MZ modulator.

    Parameters
    ----------
    cell : i3.PCell
        pcells of the IQ modulator to be simulated.
    mod_amplitude : float
        Amplitude of the modulator.
    mod_noise : float
        Amplitude of the noise of the modulator signal.
    opt_amplitude : float
        Amplitude of the input optical signal.
    opt_noise : float
        Amplitude of the noise at the optical input.
    v_mzm1 : float
        Voltage on the first heater (left) [V].
    v_mzm2 : float
        Voltage on the second heater (left) [V].
    symbol_rate : float
        symbol rate of the signal in Baud
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
    f_mod = random_bitsource(
        bitrate=symbol_rate,
        amplitude=mod_amplitude,
        n_bytes=n_bytes,
    )

    f_mod_2 = random_bitsource(
        bitrate=symbol_rate,
        amplitude=mod_amplitude / 2,
        n_bytes=n_bytes,
    )

    rand_normal_dist = rand_normal()
    src_in = i3.FunctionExcitation(
        port_domain=i3.OpticalDomain, excitation_function=lambda t: opt_amplitude + rand_normal_dist(opt_noise)
    )
    signal = i3.FunctionExcitation(
        port_domain=i3.ElectricalDomain, excitation_function=lambda t: f_mod(t) + f_mod_2(t) + rand_normal_dist(mod_noise)
    )
    
    mzm1 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: v_mzm1)
    mzm2 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: v_mzm2)
    mzm1_gnd = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    mzm2_gnd = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd1 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    gnd2 = i3.FunctionExcitation(port_domain=i3.ElectricalDomain, excitation_function=lambda t: 0.0)
    
    t0 = 0.0
    t1 = n_bytes / symbol_rate
    dt = t1 / n_bytes / steps_per_symbol
    # Testbench
    testbench = i3.ConnectComponents(
        child_cells={
            "DUT": cell,
            "out": i3.Probe(port_domain=i3.OpticalDomain),
            "src_in": src_in,
            "sig": signal,
            "gnd1": gnd1,
            "gnd2": gnd2,
            "mzm1": mzm1,
            "mzm2": mzm2,
            "mzm1_gnd": mzm1_gnd,
            "mzm2_gnd": mzm2_gnd,
        },
        links=[
            ("src_in:out", "DUT:in"),
            ("DUT:out", "out:in"),
            ("DUT:m1_1", "mzm1:out"),
            ("DUT:m1_2", "mzm1_gnd:out"),
            ("DUT:m2_1", "mzm2:out"),
            ("DUT:m2_2", "mzm2_gnd:out"),
            ("DUT:signal", "sig:out"),
            ("DUT:ground_1", "gnd1:out"),
            ("DUT:ground_2", "gnd2:out")
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



def result_modified_BPSK(result, samples_per_symbol, sampling_point=0.5):
    results_rotation = []
    res_sample = result["out"][int(samples_per_symbol * (10 + sampling_point))::samples_per_symbol]  # Ignore the first 10 symbols
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


def result_modified_OOK(result, samples_per_symbol, sampling_point=0.5):
    res_sample = result["out"][int(samples_per_symbol * (10 + sampling_point))::samples_per_symbol]  # Ignore the first 10 symbols
    
    return [res * np.exp(-1j * np.angle(res)) for res in res_sample]
