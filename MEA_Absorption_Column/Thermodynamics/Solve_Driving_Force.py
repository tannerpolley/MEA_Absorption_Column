import numpy as np
from MEA_Absorption_Column.Thermodynamics.NRTL import nrtl
from MEA_Absorption_Column.Thermodynamics.Fugacities_Coeff import fugacity_coeff


def solve_driving_force(x, y, x_true, Cl_true, Tl, a0, alpha, H_CO2_mix, P, E, kl_CO2, kv_CO2):

    y_CO2 = y[0]
    y_H2O = y[1]
    x_H2O_true = x_true[2]
    Cl_CO2_true = Cl_true[0]

    # IDAES Parameters for Psat H2O
    Psat_H2O = np.exp(72.55 + -7206.70 / Tl + -7.1385 * np.log(Tl) + 4.05e-6 * Tl ** 2)

    method = 'PC-SAFT'

    if method == 'NRTL':

        # ----------- NRTL Method -------------

        γ_CO2, γ_MEA, γ_H2O = nrtl(x_true[:3], Tl)

        # γ_H2O = 1

        Ψ = E*kl_CO2/kv_CO2
        y_CO2_eq = (y_CO2 + Ψ*Cl_CO2_true/P)/(1 + Ψ/H_CO2_mix)
        y_H2O_eq = x_H2O_true*γ_H2O*Psat_H2O/P

        Pv_CO2 = P*y_CO2
        Pl_CO2 = P*y_CO2_eq

        Pv_H2O = P * y_H2O
        Pl_H2O = P * y_H2O_eq

        DF_CO2 = P * (y_CO2 - y_CO2_eq)
        DF_H2O = P * (y_H2O - y_H2O_eq)

    elif method == 'Surr':

        # -------- Gabrielsen Approximation Method --------------

        # Combined Henry's Law and chemical equilibrium constant for MEA-CO2 Eq. 14 and Table 1
        # From Gabrielsen: A Model for Estimating CO2 Solubility in Aqueous Alkanolamines
        K_CO2 = np.exp(30.96 + -10584 / Tl + -7.187 * a0 * alpha)

        Pv_CO2 = y[0] * P
        # From Gabrielsen: A Model for Estimating CO2 Solubility in Aqueous Alkanolamines Eq. 11
        Pl_CO2 = K_CO2 * x[0] * a0 * alpha / (a0 * (1 - 2 * alpha)) ** 2

        # From Rochelle
        Pl_CO2 = np.exp(39.3 - 12155 / Tl - 19.0 * alpha ** 2 + 1105 * alpha / Tl + 12800 * alpha ** 2 / Tl) / 1e3

        Pv_H2O = y[1] * P
        Pl_H2O = x_true[2]*Psat_H2O

        KH = E * kl_CO2 / kv_CO2 / (E * kl_CO2 / kv_CO2 + H_CO2_mix)

        DF_CO2 = (Pv_CO2 - Pl_CO2)*KH
        DF_H2O = (Pv_H2O - Pl_H2O)

    elif method == 'ePC-SAFT':

        # --------------- PC-SAFT Method ----------------------- #

        φl_CO2, φl_MEA, φl_H2O = fugacity_coeff(x, 'liquid', Tl, P)
        φv_CO2, φv_H2O, φv_Ν2, φv_Ο2 = fugacity_coeff(y, 'vapor', Tl, P)

        KH = E * kl_CO2 / kv_CO2 / (E * kl_CO2 / kv_CO2 + H_CO2_mix)

        fl_CO2, fl_H2O = P * φl_CO2, P * φl_H2O
        fv_CO2, fv_H2O = P * φv_CO2, P * φv_H2O

        Pv_CO2 = fv_CO2
        Pl_CO2 = fl_CO2

        Pv_H2O = fv_H2O
        Pl_H2O = fl_H2O

        DF_CO2 = (Pv_CO2 - Pl_CO2) * KH
        DF_H2O = (Pv_H2O - Pl_H2O)


    return DF_CO2, DF_H2O, [DF_CO2, Pv_CO2, Pl_CO2, H_CO2_mix, DF_H2O, Pv_H2O, Pl_H2O, Psat_H2O]
