from MEA_Absorption_Column.Parameters import a_p, Clp, Cvp, ϵ, g, R, S
import numpy as np

log = np.log
exp = np.exp


def solve_masstransfer(rho_mass_l, rho_mass_v, mul_mix, muv_mix, sigma, Dl_CO2, Dv_CO2, Dv_H2O, Dv_T, A, Tl, Tv, ul, uv,
                       H_CO2_mix, Cl_MEA_true):

    # Liquid Hold Up from Soares 2018 and Tsai 2010
    h_L = 11.4474 * (ul*ϵ/(g**(2/3)*S**2*a_p)*(mul_mix/rho_mass_l)**(1/3)) ** .6471
    h_V = ϵ - h_L

    if h_V < 0:
        print('Error: Flooding as occurred')
        raise TypeError

    d_h = 4 * ϵ / a_p
    Lp = A * a_p / ϵ

    # Compute interfacial area

    a_e = a_p * 1.42 * (rho_mass_l / sigma * (g**(1/3)) * ((ul/a_p)**(4/3)))**.116

    def f_kl(Dl):
        kl = Clp*(12**(1/6))*((ul/h_L)**.5)*((Dl/d_h)**.5) # m/s
        return kl

    def f_kv(Dv):
        kv = Cvp/R/Tv*np.sqrt(a_p/d_h/h_V)*Dv**(2/3)*(muv_mix/rho_mass_v)**(1/3)*(uv*rho_mass_v/a_p/muv_mix)**(3/4) # m/s
        return kv

    kl_CO2 = f_kl(Dl_CO2)
    kv_CO2 = f_kv(Dv_CO2)
    kv_H2O = f_kv(Dv_H2O)
    kv_T = f_kv(Dv_T) * (R * Tv)

    return kl_CO2, kv_CO2, kv_H2O, kv_T, [kl_CO2, kv_CO2, kv_H2O], uv, a_e, [ul, uv, h_L, a_e]
