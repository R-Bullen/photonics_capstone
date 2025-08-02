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

import numpy as np
from ipkiss3 import all as i3


def get_mzi_delta_length_from_fsr(center_wavelength, fsr, trace_template):
    """Calculate the arm length difference required to get the specified free spectral range.

    Returns the arm length difference in a Mach-Zehnder Interferometer required to get the specified free spectral
    range (fsr) while having a maximum constructive interference at center_wavelength.

    Parameters
    ----------
    center_wavelength : float
        center wavelength [um]
    fsr : float
        desired free spectral range [um]
    trace_template : TraceTemplate
        the trace template

    Returns
    -------
    float
        length difference
    """
    env = i3.Environment(wavelength=center_wavelength)
    tt_cm = trace_template.get_default_view(i3.CircuitModelView)
    n_g = tt_cm.get_n_g(environment=env)
    n_eff = tt_cm.get_n_eff(environment=env)
    center_wavelength = center_wavelength

    length_0 = center_wavelength**2 / n_g / fsr
    length = np.ceil(length_0 / center_wavelength * n_eff) * center_wavelength / n_eff

    return length


def get_length_pi(center_wavelength, trace_template):
    """Returns the length of waveguide with pi phaseshift at a specific wavelength

    Parameters
    ----------
    center_wavelength : float
        center_wavelength [um]
    trace_template : TraceTemplate
        trace template

    Returns
    -------
    float
        length giving a pi phase-shift
    """
    env = i3.Environment(wavelength=center_wavelength)
    tt_cm = trace_template.get_default_view(i3.CircuitModelView)
    n_eff = tt_cm.get_n_eff(environment=env)
    center_wavelength = center_wavelength
    length_pi = center_wavelength / (2 * n_eff)

    return length_pi


def flip_couplings_and_delays(couplings, delay_lengths, length_pi, flips=[]):

    new_couplings = [1 - p if cnt in flips else p for cnt, p in enumerate(couplings)]
    for f in flips:
        delay_lengths_adapted = [d if f <= cnt else -d for cnt, d in enumerate(delay_lengths)]
        if f > 0:
            delay_lengths_adapted[f - 1] += length_pi
        if f < len(delay_lengths) - 1:
            delay_lengths_adapted[f] -= length_pi

        delay_lengths = delay_lengths_adapted

    return new_couplings, delay_lengths
