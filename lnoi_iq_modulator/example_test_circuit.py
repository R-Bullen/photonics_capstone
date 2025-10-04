
"""Simulate an MZ modulator working in OOK modulation format. This is mainly based on Luceda Academy example.

This script generates several outputs:
- visualize the layout in a matplotlib window (this pauses script execution)
- circuit simulation result (time-domain)
- Plot EyeDiagram
- Plot Constellation diagram
"""

import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3
from iq_modulator_design import IQModulator


electrode_length = 8000
iq_mod = IQModulator(with_delays=True, delay_at_input=True)

lv = iq_mod.Layout(electrode_length=electrode_length, hot_width=50, electrode_gap=9)

lv.visualize(annotate=True)
