# Direct copy from si_fab example
#
# Copyright (C) 2020-2024 Luceda Photonics
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

from collections.abc import Callable
import numpy as np


def random_bitsource(bitrate: float, amplitude: float, n_bytes: int = 100, seed=None):
    """Create a random bit source function f(t) with a given bitrate, end time and amplitude.

    Parameters
    ----------
    bitrate : float
        Bitrate [bit/s].
    amplitude : float
    n_bytes : int
    seed : int
        Seed used for random number generation.

    Returns
    -------
    f_prbs :
        PRBS function as a function of time.

    """
    from numba import njit

    if seed is not None:
        np.random.seed(seed)

    data = (np.random.randint(0, 2, n_bytes) - 0.5) * 2

    @njit()
    def f_rbs(t):
        idx = int(t * bitrate)
        if idx >= n_bytes:
            idx = n_bytes - 1
        return amplitude * data[idx]

    return f_rbs


def step_function(amplitude_0: float, amplitude_1: float, t_step: float) -> Callable[[float], float]:
    """Create a step function f_step(t) between amplitude_0 and amplitude_1 at t_step.

    Parameters
    ----------
    amplitude_0 : float
    amplitude_1 : float
    t_step : float

    Returns
    -------
    f_step :
        Step as a function of time.

    """

    def f_step(t: float) -> float:
        if t >= t_step:
            return amplitude_1
        return amplitude_0

    return f_step


def rand_normal() -> Callable[[float], float]:
    """Returns a numba jitted function that returns a float based on a normal distribution.

    Parameters
    ----------
    sigma : float
        Standard deviation.

    Returns
    -------
    Function that returns a random floating point number from a normal distribution around 0 with sigma deviation.

    """
    from numba import njit

    @njit()
    def rand_normal_jitted(sigma: float) -> float:
        return np.random.normal(0, sigma)

    return rand_normal_jitted
