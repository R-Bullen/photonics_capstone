import math

frequency = 10e9

def elec_signal_i(t):
    T = 1.0 / frequency
    n = int(t / T)

    if (t - n * T < T / 2):
        return -1.0
    else:
        return 1.0

def elec_signal_q(t):
    T = 1.0 / frequency
    n = int(t / T)

    #if (t - n * T < T / 2):
    if (t-n*T > T/4 and t-n*T < 3*T/4):
    #if (t-n*T < T/4):
        return 1.0
    else:
        return -1.0

def elec_ground(t):
    return 0.0

def opt_signal(t):
    f = 10e6
    return math.cos(2*math.pi*f*t)