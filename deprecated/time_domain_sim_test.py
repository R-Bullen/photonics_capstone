import ipkiss3.all as i3
import numpy as np
from scipy.constants import speed_of_light

class WGModel(i3.CompactModel):
    parameters = [
       'n_eff',
       'n_g',
       'length',
    ]

    terms = [
       i3.OpticalTerm(name='in'),
       i3.OpticalTerm(name='out'),
       i3.ElectricalTerm(name='el_in')
    ]

    states = [
       'temperature',
    ]

    def calculate_smatrix(parameters, env, S):
        # the value of length and n_eff are avalaible through the 'parameters' object.
        phase = 2 * np.pi / env.wavelength * parameters.n_eff * parameters.length
        A = 0.99 # the amplitude is hardcoded, but we could make it a property aswell
        S['in', 'out'] = S['out', 'in'] = A * np.exp(1j * phase)

    def calculate_signals(parameters, env, output_signals, y, t, input_signals):
        A = 0.99
        alpha = 0.1
        beta = 0.1
        # First-order approximation of the delay
        delay = parameters.length / speed_of_light * parameters.n_g
        phase = 2 * np.pi / env.wavelength * parameters.n_eff * parameters.length
        phase += alpha * input_signals['el_in']
        phase += beta * y['temperature']
        output_signals['out'] = A * np.exp(1j * phase) * input_signals['in', t - delay]
        output_signals['in'] = A * np.exp(1j * phase) * input_signals['out', t - delay]

    def calculate_dydt(parameters, env, dydt, y, t, input_signals):
        tau = 1.0
        dydt['temperature'] = -1 / tau * y['temperature'] + 0.1 * input_signals['in']


class MyWaveguide(i3.PCell):

    class Netlist(i3.NetlistView):
        def _generate_netlist(self, nl):
            nl += i3.OpticalTerm(name='in')
            nl += i3.OpticalTerm(name='out')
            nl += i3.ElectricalTerm(name='el_in')
            return nl

    class CircuitModel(i3.CircuitModelView):
        n_eff = i3.PositiveNumberProperty(doc="Effective index", default=2.4)
        n_g = i3.PositiveNumberProperty(doc="Effective index", default=4.3)
        length = i3.PositiveNumberProperty(doc="Waveguide length", default=100)

        def _generate_model(self):
            return WGModel(n_eff=self.n_eff,
                           n_g=self.n_g,
                           length=self.length)

def elec_signal(t):
    if t > 0.2:
       return 1.0
    return 0.0


def opt_signal(t):
    return 1.0


testbench = i3.ConnectComponents(
    child_cells={
        'el_excitation': i3.FunctionExcitation(port_domain=i3.ElectricalDomain,
                                               excitation_function=elec_signal),

        'opt_excitation': i3.FunctionExcitation(port_domain=i3.OpticalDomain,
                                               excitation_function=opt_signal),
        'wg': MyWaveguide(),
        'wg_out': i3.Probe(port_domain=i3.OpticalDomain),
    },
    links=[
        ('el_excitation:out', 'wg:el_in'),
        ('opt_excitation:out', 'wg:in'),
        ('wg:out', 'wg_out:in'),
    ]
)

from pylab import plt
tb_cm = testbench.CircuitModel()
result = tb_cm.get_time_response(t0=0, t1=1, dt=0.1, center_wavelength=1.55)

plt.plot(result.timesteps, result['opt_excitation'], 'g--')
plt.plot(result.timesteps, result['wg_out'])
plt.show()