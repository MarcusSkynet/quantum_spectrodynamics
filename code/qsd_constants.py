#!/usr/bin/env python3
"""
QSD Fundamental Constants -- Single Source of Truth
====================================================

All constants derived algebraically from the QSD triad, each member owned
by one substructure of the [[5,1,3]] code (or their union):

    Hb4   = 1/(4 ln 2)      holographic bit density   <- K4  (stabiliser count)
    sigma = 3/(80 phi^2)    geometric strain          <- K4 u C5 (frustration)
    varpi = pi * phi^2      spectral bond             <- C5  (cycle spectrum)

Every other QSD prediction follows from these three plus M_Planck (the sole
dimensional input; the proton mass enters only the proton-lifetime estimate).

Author: M. Hubka
Date: February 2026; revised July 2026 (v2.0 -- comment corrections,
      proton-lifetime formula aligned with the published S5 theorem)

NOTE: All intermediate computations carried to 15+ significant figures.
      Only final display values are rounded.
"""

import numpy as np


# =============================================================================
# MATHEMATICAL CONSTANTS
# =============================================================================

GOLDEN_RATIO = (1.0 + np.sqrt(5.0)) / 2.0         # phi = 1.6180339887...
GOLDEN_RATIO_SQ = GOLDEN_RATIO ** 2               # phi^2 = 2.6180339887...
LN2 = np.log(2.0)                                 # ln(2) = 0.6931471806...


# =============================================================================
# THE QSD TRIAD  (three fundamental constants from [[5,1,3]] code)
# =============================================================================

# Holographic bit density: information capacity per Planck area per dimension.
# Origin (K4): the code has n-k = 4 stabilisers (2^4 = 16 syndrome outcomes);
# equivalently the 4 faces of the self-dual tetrahedron, each carrying one
# Landauer area quantum ln2 * l_P^2. The Bekenstein-Hawking factor 4 in
# S = A/(4 l_P^2) is a CONSEQUENCE of this count, not an input.
def holographic_bit_density(n_dim):
    """Holographic bit density of an n-cell: Hb_n = 1/(n ln 2)."""
    return 1.0 / (n_dim * LN2)

HB4 = holographic_bit_density(4)                  # 0.3606737602...

# Geometric strain: the K4<->C5 frustration parameter.
# 3   = first Betti number beta_1(K4) = E - V + 1 = 6 - 4 + 1  (K4 cycles)
# 80  = Landauer capacity C_L = 2^(n-k) * n = 16 syndromes x 5 qubits
# phi^2 = C5 spectral class ratio (see VARPI below)
# sigma is the only triad member that irreducibly mixes both subgraphs.
# NB: the historical "K4 route" 3/8 - Hb4 (TN-1) agrees to 175.5 ppm but is
# an SU(5)-premised numerical coincidence -- it is NOT a definition and is
# not used anywhere (errata TN1-2, drift D27).
SIGMA = 3.0 / (80.0 * GOLDEN_RATIO_SQ)            # 0.0143237254...

# Spectral bond: information-geometric content per K4 edge.
# phi^2 = ratio of the two C5 adjacency-eigenvalue classes
#         |2cos(144deg)| / |2cos(72deg)| = phi / (1/phi);
# pi    = per-cycle spinor holonomy of the pentagram clock (candidate
#         mechanism; the value pi*phi^2 is definitional).
VARPI = np.pi * GOLDEN_RATIO_SQ                    # 8.2247963456...


# =============================================================================
# GAUGE COUPLINGS (derived from triad, NO hardcoded values)
# =============================================================================

# --- Fine structure constant: 3-loop topological renormalization ---
# Tree level: 6 edges of K4, each contributing varpi/Hb4
ALPHA_INV_TREE = 6.0 * VARPI / HB4                # 136.8238655...

# 1-loop: information friction (strain through 6 K4 edges)
LOOP_1 = 6.0 * SIGMA / HB4                        # +0.2382828...

# 2-loop: S4 symmetry feedback (24 permutations, strain^2, phi coupling)
LOOP_2 = 24.0 * SIGMA**2 * GOLDEN_RATIO / HB4     # 0.0220900...

# 3-loop: angular screening (same as 2-loop divided by pi)
LOOP_3 = LOOP_2 / np.pi                           # 0.0070315...

# Final QSD prediction
ALPHA_INV_QSD = ALPHA_INV_TREE + LOOP_1 - LOOP_2 - LOOP_3  # 137.0330268...

# --- Strong coupling: spectral bond times strain ---
ALPHA_S_QSD = VARPI * SIGMA                        # = 3*pi/80 = 0.1178097...

# Verification: alpha_s = 3*pi/80 (golden ratio cancels exactly -- the
# union signature: only in the product sigma*varpi does phi^2 drop out)
ALPHA_S_EXACT = 3.0 * np.pi / 80.0                # 0.1178097...

# --- Weak mixing angle: generator counting + strain correction ---
# 3/13 from gauge generators (8+3+1+1 = 13, weak contributes 3)
# sigma/32 from the 2^5 = 32-dimensional Hilbert space of the 5 qubits
SIN2_THETA_TREE = 3.0 / 13.0                      # 0.2307692...
SIN2_THETA_CORRECTION = SIGMA / 32.0              # 0.0004476...
SIN2_THETA_QSD = SIN2_THETA_TREE + SIN2_THETA_CORRECTION  # 0.2312168...


# =============================================================================
# ENERGY SCALE (M_Planck is the sole experimental input)
# =============================================================================

M_PLANCK_GEV = 1.22089e19                         # GeV (CODATA 2018)

# Information reduction: 2^60 = D^N as bits
# D = dim H(K4 bulk) = 2^4 = 16   (4 bulk qubits)
# N = 15 su(4) channels           (16 - 1 traceless generators-per-class)
# total bits = log2(16^15) = 4 * 15 = 60   [constructed form; the counts
# 16 and 15 are structural, the exponential form D^N is the construction]
INFORMATION_EXPONENT = 60
INFORMATION_FACTOR = 2**INFORMATION_EXPONENT      # 1.152921504...e18

# Base energy
E_BASE = M_PLANCK_GEV / INFORMATION_FACTOR        # 10.58953...  GeV

# Radion VEV (dimensionful): the fundamental QSD energy scale
# mu_0 = (M_Pl / 2^60) * phi^2 * (1 - 6*sigma);  6 = K4 edge count
STRAIN_CORRECTION = 1.0 - 6.0 * SIGMA             # 0.9140576...
MU_RAD = E_BASE * GOLDEN_RATIO_SQ * STRAIN_CORRECTION  # 25.34111...  GeV

# Dimensionless VEV -- DEFINITIONAL: nu_0 := Hb4/sigma = 20 phi^2/(3 ln2).
# Triad-only; no path from mu_0 to nu_0 exists in the definition graph.
NU_RAD = HB4 / SIGMA                              # 25.18016...

# Dressing factor -- DEPENDENT ratio, defines nothing downstream:
# xi := mu_0/nu_0 = (3 ln2/20)(1 - 6 sigma) E_base  (closed form)
XI_DRESSING = MU_RAD / NU_RAD                     # 1.00639...  GeV


# =============================================================================
# MASS PREDICTIONS (all from mu_rad with integer/rational coefficients)
# =============================================================================

# Higgs mass: 5 physical qubits of [[5,1,3]]
M_HIGGS_QSD = 5.0 * MU_RAD                        # 126.706...  GeV

# Syndrome (snap) energy: 8 severed intra-node edges, one sigma quantum each
E_SYNDROME_QSD = MU_RAD * (1.0 + 8.0 * SIGMA)     # 28.2449...  GeV

# W boson mass: ratio of bulk Hilbert dimension to code qubits (16/5)
M_W_QSD = (16.0 / 5.0) * MU_RAD                   # 81.0916...  GeV


# =============================================================================
# COSMOLOGICAL CONSTANT (S7 conjecture)
# =============================================================================

# Entropy barrier: thermodynamic cost of syndrome extraction per Planck 4-volume
ENTROPY_BARRIER = 4.0 / SIGMA                      # 279.2570  nats

# Vacuum energy ratio: Boltzmann suppression
LAMBDA_LOG10 = -ENTROPY_BARRIER / np.log(10.0)     # -121.2798
LAMBDA_RATIO = np.exp(-ENTROPY_BARRIER)            # ~5.3e-122


# =============================================================================
# PROTON LIFETIME (S5 prediction)
# =============================================================================

# Mediator (screening) scale for baryon-number violation. NOTE: this is not
# a unification point -- QSD's couplings are code-fixed and never run to
# meet anywhere; M_X feeds ONLY the proton-lifetime estimate below.
M_X_GEV = M_PLANCK_GEV * SIGMA                    # 1.7488e17  GeV

# Proton mass (experimental; used only here)
M_PROTON_GEV = 0.93827

# Proton lifetime, S5 theorem: tau_p = M_X^4 / (alpha_s^2 m_p^5)
# (standard GUT dimensional scaling premise; the 1/alpha_s^2 = 72.05
# coupling suppression is part of the published theorem)
# Conversion: 1 GeV^-1 ~ 6.582e-25 seconds
GEV_INV_TO_SECONDS = 6.582119569e-25
SECONDS_PER_YEAR = 3.15576e7
TAU_P_NATURAL = M_X_GEV**4 / (ALPHA_S_QSD**2 * M_PROTON_GEV**5)  # GeV^-1
TAU_P_SECONDS = TAU_P_NATURAL * GEV_INV_TO_SECONDS
TAU_P_YEARS = TAU_P_SECONDS / SECONDS_PER_YEAR    # 1.93e39 years


# =============================================================================
# EXACT ALGEBRAIC IDENTITIES (self-consistency checks)
# =============================================================================

# Identity 1:  6 * alpha_s = alpha_inv_tree * Hb4 * sigma
IDENTITY_LHS = 6.0 * ALPHA_S_QSD
IDENTITY_RHS = ALPHA_INV_TREE * HB4 * SIGMA

# Identity 2:  Hb_n * ln(2) = 1/n  (for any n)
LANDAUER_IDENTITY = HB4 * LN2                      # should be 0.25 = 1/4

# Identity 3:  alpha_s = 3*pi/80  (golden ratio cancels)
ALPHA_S_CANCELLATION = abs(ALPHA_S_QSD - ALPHA_S_EXACT)


# =============================================================================
# EXPERIMENTAL VALUES (for comparison only -- never used in derivations)
# =============================================================================

ALPHA_INV_EXP = 137.035999084         # CODATA 2018 (21 ppb uncertainty)
ALPHA_S_EXP = 0.1180                  # PDG 2022 (M_Z)
SIN2_THETA_EXP = 0.23122              # PDG 2022
M_HIGGS_EXP = 125.25                  # GeV, PDG 2022 (+-0.17)
E_SYNDROME_CMS = 28.3                 # GeV, CMS dimuon excess
M_W_EXP = 80.377                      # GeV, PDG 2022
LAMBDA_OBS_LOG10 = -121.27            # Planck 2018


# =============================================================================
# VERIFICATION (runs on import)
# =============================================================================

def verify_constants():
    """Run self-consistency checks. Raises AssertionError on failure."""

    # Gauge identity
    assert abs(IDENTITY_LHS - IDENTITY_RHS) < 1.0e-12, (
        "Gauge identity 6*alpha_s = alpha_inv_tree * Hb4 * sigma FAILED: "
        f"LHS={IDENTITY_LHS}, RHS={IDENTITY_RHS}")

    # Golden ratio cancellation in alpha_s
    assert ALPHA_S_CANCELLATION < 1.0e-14, (
        f"alpha_s != 3*pi/80: difference = {ALPHA_S_CANCELLATION}")

    # Landauer identity
    assert abs(LANDAUER_IDENTITY - 0.25) < 1.0e-14, (
        f"Hb4 * ln(2) != 1/4: got {LANDAUER_IDENTITY}")

    # Total states in K4 Heisenberg spectrum
    # degeneracies: S=0 -> 2, S=1 -> 9, S=2 -> 5
    assert 2 + 9 + 5 == 16, "K4 state count mismatch"

    # Proton lifetime carries the S5-theorem coupling suppression (v2.0 fix)
    assert abs(TAU_P_YEARS / 1.933e39 - 1.0) < 1.0e-3, (
        f"tau_p != S5 theorem value 1.933e39 yr: got {TAU_P_YEARS:.4g}")

    return True


# Run verification on import
verify_constants()


# =============================================================================
# DISPLAY FUNCTION
# =============================================================================

def print_all_constants():
    """Print all QSD constants with comparison to experiment."""

    print("=" * 72)
    print("QSD FUNDAMENTAL CONSTANTS (derived from [[5,1,3]] code)")
    print("=" * 72)

    print("\n--- QSD Triad ---")
    print(f"  Hb4   = 1/(4 ln 2)       = {HB4:.12f}   [K4]")
    print(f"  sigma = 3/(80 phi^2)      = {SIGMA:.12f}   [K4 u C5]")
    print(f"  varpi = pi * phi^2        = {VARPI:.12f}   [C5]")

    print("\n--- Fine Structure Constant (3-loop) ---")
    print(f"  Tree:   6*varpi/Hb4       = {ALPHA_INV_TREE:.10f}")
    print(f"  1-loop: +6*sigma/Hb4      = +{LOOP_1:.10f}")
    print(f"  2-loop: -24*sigma^2*phi/Hb4 = -{LOOP_2:.10f}")
    print(f"  3-loop: -loop2/pi         = -{LOOP_3:.10f}")
    print(f"  -----------------------------------------------")
    print(f"  alpha^-1 (QSD)            = {ALPHA_INV_QSD:.10f}")
    print(f"  alpha^-1 (exp)            = {ALPHA_INV_EXP:.9f}")
    err_ppm = abs(ALPHA_INV_QSD - ALPHA_INV_EXP) / ALPHA_INV_EXP * 1.0e6
    print(f"  Error                     = {err_ppm:.1f} ppm")

    print("\n--- Strong Coupling ---")
    print(f"  alpha_s = varpi * sigma   = {ALPHA_S_QSD:.12f}")
    print(f"  alpha_s = 3*pi/80         = {ALPHA_S_EXACT:.12f}")
    print(f"  alpha_s (exp)             = {ALPHA_S_EXP}")
    err_as = abs(ALPHA_S_QSD - ALPHA_S_EXP) / ALPHA_S_EXP * 100.0
    print(f"  Error                     = {err_as:.2f}%")

    print("\n--- Weak Mixing Angle ---")
    print(f"  sin^2(theta_W) = 3/13 + sigma/32 = {SIN2_THETA_QSD:.10f}")
    print(f"  sin^2(theta_W) (exp)              = {SIN2_THETA_EXP}")
    err_sw = abs(SIN2_THETA_QSD - SIN2_THETA_EXP) / SIN2_THETA_EXP * 100.0
    print(f"  Error                             = {err_sw:.3f}%")

    print("\n--- Energy Scale ---")
    print(f"  M_Planck                  = {M_PLANCK_GEV:.5e} GeV")
    print(f"  E_base = M_Pl / 2^60     = {E_BASE:.10f} GeV")
    print(f"  mu_rad (dimensionful VEV) = {MU_RAD:.10f} GeV")
    print(f"  nu_rad (dimensionless)    = {NU_RAD:.10f}")
    print(f"  xi (dressing factor)      = {XI_DRESSING:.10f} GeV")

    print("\n--- Mass Predictions ---")
    print(f"  {'Observable':<20s} {'QSD':>12s} {'Experiment':>12s} {'Error':>10s}")
    print(f"  {'-'*56}")

    for name, qsd, exp, unit in [
        ("alpha^-1",     ALPHA_INV_QSD,   ALPHA_INV_EXP,   ""),
        ("alpha_s",      ALPHA_S_QSD,     ALPHA_S_EXP,     ""),
        ("sin^2(theta)", SIN2_THETA_QSD,  SIN2_THETA_EXP,  ""),
        ("m_H",          M_HIGGS_QSD,     M_HIGGS_EXP,     " GeV"),
        ("E_syn",        E_SYNDROME_QSD,  E_SYNDROME_CMS,  " GeV"),
        ("m_W",          M_W_QSD,         M_W_EXP,         " GeV"),
    ]:
        err_pct = abs(qsd - exp) / exp * 100.0
        print(f"  {name:<20s} {qsd:>12.4f}{unit} {exp:>9.4f}{unit} {err_pct:>8.3f}%")

    print(f"\n--- Cosmological Constant ---")
    print(f"  4/sigma (entropy barrier) = {ENTROPY_BARRIER:.6f} nats")
    print(f"  log10(rho_L/rho_Pl) QSD  = {LAMBDA_LOG10:.4f}")
    print(f"  log10(rho_L/rho_Pl) obs  = {LAMBDA_OBS_LOG10}")

    print(f"\n--- Proton Lifetime (S5 theorem) ---")
    print(f"  M_X = M_Pl * sigma (mediator) = {M_X_GEV:.4e} GeV")
    print(f"  tau_p = M_X^4/(alpha_s^2 m_p^5) ~ {TAU_P_YEARS:.2e} years")

    print(f"\n--- Algebraic Identities ---")
    print(f"  6*alpha_s                 = {IDENTITY_LHS:.12f}")
    print(f"  alpha_inv_tree*Hb4*sigma  = {IDENTITY_RHS:.12f}")
    print(f"  |difference|              = {abs(IDENTITY_LHS - IDENTITY_RHS):.2e}")
    print(f"  Hb4 * ln(2)              = {LANDAUER_IDENTITY:.15f}  (should be 0.25)")

    print("\n" + "=" * 72)
    print("All predictions from M_Planck alone (zero free parameters)")
    print("=" * 72)


if __name__ == "__main__":
    print_all_constants()
