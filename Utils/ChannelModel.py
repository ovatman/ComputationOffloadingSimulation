import math
import numpy
from SimEngine import SimEngine


def gain2d(theta, phi):
    g_0 = 8
    theta_3 = math.sqrt(31000 * 10 ** (-0.1 * g_0))
    phi_3 = math.sqrt(31000 * 10 ** (-0.1 * g_0))

    theta_rad = theta / 180 * math.pi
    phi_rad = phi / 180 * math.pi

    alpha_rad = math.atan(math.tan(theta_rad) / math.sin(phi_rad))

    alpha = alpha_rad / math.pi * 180
    if alpha < -90:
        print('alpha error')
    elif alpha > 90:
        print('alpha')

    psi_rad = math.acos(math.cos(theta_rad) * math.cos(phi_rad))

    psi = psi_rad / math.pi * 180

    phi_th = phi_3

    phi_3m = 1
    if phi_th > abs(phi) > 0:
        phi_3m = phi_3
    elif (abs(phi) > phi_th) and (abs(phi) < 180):
        phi_3m = (math.cos((abs(phi) - phi_th) / (180 - phi_th) * 90 / phi_3 * math.pi / 180) / phi_3) ** 2
        phi_3m += (math.sin((abs(phi) - phi_th) / (180 - phi_th) * 90 / phi_3 * math.pi / 180) / theta_3) ** 2
        phi_3m = math.sqrt(phi_3m) ** -1

    psi_alpha = 1
    if 90 >= psi >= 0:
        psi_alpha = (math.sqrt((math.cos(alpha_rad) / phi_3) ** 2 + (math.sin(alpha_rad) / theta_3) ** 2)) ** -1
    elif 180 >= psi > 90:
        psi_alpha = (math.sqrt((math.cos(theta_rad) / phi_3m) ** 2 + (math.sin(theta_rad) / theta_3) ** 2)) ** -1

    g = g_0
    if 1.152 >= psi / psi_alpha >= 0:
        g = g_0 - 12 * ((psi / psi_alpha) ** 2)
    else:
        g = g_0 - 15 - 15 * math.log10(psi / psi_alpha)

    return g


def rice_generate(k, omega, n):
    var = (omega / (2 * (k + 1)))
    mu = math.sqrt(2 * k * var)
    theta = math.pi / 8
    h_i = mu * math.cos(theta) + math.sqrt(var) * numpy.random.normal(1, 1, n)
    h_q = mu * math.sin(theta) + math.sqrt(var) * numpy.random.normal(1, 1, n)
    h = h_i + h_q
    return h


def calculate_params(aerial):
    k = aerial.rice_param
    noise_power = get_noise_power(aerial)

    d = aerial.dist
    dx = 1
    dy = 1
    dz = aerial.dist

    phi_point = math.atan(0) / math.pi * 180
    theta_point = math.atan(0) / math.pi * 180
    phi = math.atan(dy / dz) / math.pi * 180 - phi_point
    theta = math.atan(dx / dz) / math.pi * 180 - theta_point

    if aerial.g_3 is None:
        aerial.g_3 = gain2d(theta, phi)

    p_l = 10 * math.log10(SimEngine.the_engine().c ** 2 * (4 * math.pi * aerial.carrierfreq * d) ** -2)

    h = rice_generate(k, 1, 1)
    h_db = 20 * math.log10(abs(h[0]))
    pr = aerial.receive_power + aerial.g_3 + p_l + h_db
    snr = pr - noise_power

    return snr


def get_noise_power(aerial):
    return 10 * math.log10(aerial.noise * aerial.temp * aerial.bandwidth)
