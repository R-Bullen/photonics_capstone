# Test circuit for LNOI IQ modulator design with electrical pads and grating couplers

import ipkiss3.all as i3
from iq_modulator_design import IQModulator

class IQModulatorTestCircuit(i3.Circuit):
    def _default_insts(self):
        insts = {
            'IQModulator': IQModulator,

        }

        return insts

    def _default_specs(self):
        pass

    def _default_exposed_ports(self):
        pass
