
import asp_sin_lnoi_photonics.all as asp
import ipkiss3.all as i3
from iq_modulator_test_circuit import IQModulatorTestCircuit
from simulation.simulate_test_circuit_PAM4 import simulate_modulation_PAM4

test_circuit = IQModulatorTestCircuit()
lv = test_circuit.Layout()
lv.visualize(annotate=True)

cm = test_circuit.CircuitModel()

electrode_length = 8000
# Define modulator characteristics
# Voltage needed for a pi phase shift and half pi shift
# rf_vpi = cm.vpi_l / 2 / (electrode_length / 10000)  # VpiL unit is V.cm; Dividing be 2 is due to push-pull configutation
rf_vpi = 3.125
V_half_pi = rf_vpi / 2
print("Modulator RF electrode Vpi: {} V".format(rf_vpi))

ps_vpi = 0.1 / (200 / 10000)
print("PS Vpi = %f" % ps_vpi)

cm.bandwidth = 50e9  # Modulator bandwidth (in Hz)

num_symbols = 2 ** 9
samples_per_symbol = 2 ** 9
bit_rate = 50e9

results = simulate_modulation_PAM4(
    cell=test_circuit,
    mod_amplitude_i=2.0,
    mod_noise_i=0.2,
    mod_amplitude_q=1.0,
    mod_noise_q=0.1,
    opt_amplitude=1.0,
    opt_noise=0.1,
    v_heater_i=0,
    # v_heater_q=0, # for no-delay
    v_heater_q=5.303030303030303, # quadrature voltage, for with-delay
    # v_mzm_left1=ps_vpi/2, # for no-delay
    v_mzm_left1=0,  # for with-delay
    v_mzm_left2=0.0,
    v_mzm_right1=0.0,
    v_mzm_right2=ps_vpi/2,
    bit_rate=bit_rate,
    n_bytes=num_symbols,
    steps_per_bit=samples_per_symbol,
    # center_wavelength=1.55, # for no-delay
    center_wavelength=1.55195, # for with-delay
)


