import asp_sin_lnoi_photonics.all as pdk
import ipkiss3.all as i3
import pylab as plt
import numpy as np

class Circuit(i3.Circuit):
    mmi = i3.ChildCellProperty()
    mzm1 = i3.ChildCellProperty()
    mzm2 = i3.ChildCellProperty()
    ps = i3.ChildCellProperty()
    mmi2 = i3.ChildCellProperty()
    pad = i3.ChildCellProperty()

    def _default_insts(self):
        insts =\
            {
                "mmi1": self.mmi,
                "mzm1": self.mzm1,
                "mzm2": self.mzm2,
                "ps1": self.ps,
                "mmi2": self.mmi2,
                "pad1": self.pad,
                "pad2": self.pad,
                "pad3": self.pad
            }

        return insts

    def _default_specs(self):
        specs =\
            [
                i3.Place("mmi1", (0, 0)),
                i3.Place("mzm1", (6000, 700)),
                i3.Place("mzm2", (6000, -700)),
                i3.Place("ps1", (10300, -700)),
                i3.Place("mmi2", (11200, 0)),
                i3.Place("pad1", (2000, -1500)),
                i3.Place("pad2", (2400, -1500)),
                i3.Place("pad3", (2800, -1500)),
                i3.ConnectBend("mmi1:out2", "mzm1:in"),
                i3.ConnectBend("mmi1:out1", "mzm2:in"),
                i3.ConnectBend("mzm2:out", "ps1:in"),
                i3.ConnectBend("mzm1:out", "mmi2:in2"),
                i3.ConnectBend("ps1:out", "mmi2:in1"),
                i3.ConnectElectrical("mzm2:m1_1", "pad1:m1", start_angle=0, end_angle=0),
                i3.ConnectElectrical("mzm2:m1_2", "pad2:m1", start_angle=0, end_angle=0),
                i3.ConnectElectrical("pad1:m1", "ps1:m1", start_angle=0, end_angle=0),
                i3.ConnectElectrical("pad3:m1", "ps1:m2", start_angle=0, end_angle=0),
            ]

        return specs

    def _default_exposed_ports(self):
        exposed_ports =\
            {
                "mmi1:in": "in",
                "mmi2:out": "out"
            }

        return exposed_ports