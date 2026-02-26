#!/usr/bin/env python3
"""
QSD Simulation Suite
====================
Quantum Spectrodynamics -- Computational Validation

Numerical verification of all core QSD mechanisms:
  1. [[5,1,3]] code structure and error correction
  2. K4 Heisenberg model spectrum
  3. C5 pentagon tight-binding and golden ratio emergence
  4. Geometric strain from K4-C5 incompatibility
  5. 3-loop topological renormalization (derived from triad)
  6. Strong coupling alpha_s = 3*pi/80
  7. Energy scale derivation from Planck mass
  8. Cosmological constant conjecture
  9. Proton lifetime estimate
 10. Master relations and algebraic identities

All constants imported from qsd_constants.py (single source of truth).
No unicode characters. Intermediate precision >= 10 decimal places.

Author: M. Hubka
Date: February 2026
"""

import numpy as np
from scipy import linalg
from typing import Tuple, Dict, List

from qsd_constants import (
    GOLDEN_RATIO, GOLDEN_RATIO_SQ, LN2,
    HB4, SIGMA, VARPI,
    ALPHA_INV_TREE, LOOP_1, LOOP_2, LOOP_3, ALPHA_INV_QSD,
    ALPHA_S_QSD, ALPHA_S_EXACT,
    SIN2_THETA_TREE, SIN2_THETA_CORRECTION, SIN2_THETA_QSD,
    M_PLANCK_GEV, E_BASE, STRAIN_CORRECTION, MU_RAD, NU_RAD, XI_DRESSING,
    M_HIGGS_QSD, E_SYNDROME_QSD, M_W_QSD,
    ENTROPY_BARRIER, LAMBDA_LOG10, LAMBDA_RATIO,
    M_X_GEV, TAU_P_YEARS,
    ALPHA_INV_EXP, ALPHA_S_EXP, SIN2_THETA_EXP,
    M_HIGGS_EXP, E_SYNDROME_CMS, M_W_EXP, LAMBDA_OBS_LOG10,
    holographic_bit_density,
)


# =============================================================================
# 1. [[5,1,3]] QUANTUM ERROR-CORRECTING CODE
# =============================================================================

class Code513:
    """
    The [[5,1,3]] perfect quantum error-correcting code.

    Encodes 1 logical qubit in 5 physical qubits with distance 3.
    Can correct any single-qubit error.

    Stabilizer generators (cyclic Z5 structure):
        g1 = X Z Z X I
        g2 = I X Z Z X
        g3 = X I X Z Z
        g4 = Z X I X Z
    """

    def __init__(self):
        self.pauli_I = np.array([[1, 0], [0, 1]], dtype=complex)
        self.pauli_X = np.array([[0, 1], [1, 0]], dtype=complex)
        self.pauli_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        self.pauli_Z = np.array([[1, 0], [0, -1]], dtype=complex)

        self.stabilizer_patterns = [
            ["X", "Z", "Z", "X", "I"],
            ["I", "X", "Z", "Z", "X"],
            ["X", "I", "X", "Z", "Z"],
            ["Z", "X", "I", "X", "Z"],
        ]

    def _pauli(self, label):
        """Return Pauli matrix by single-character label."""
        table = {
            "I": self.pauli_I, "X": self.pauli_X,
            "Y": self.pauli_Y, "Z": self.pauli_Z,
        }
        return table[label]

    def _tensor_product(self, matrices):
        """Compute tensor (Kronecker) product of a list of matrices."""
        result = matrices[0]
        for m in matrices[1:]:
            result = np.kron(result, m)
        return result

    def stabilizer_generator(self, index):
        """Return the index-th stabilizer generator as 32x32 matrix."""
        pattern = self.stabilizer_patterns[index]
        matrices = [self._pauli(p) for p in pattern]
        return self._tensor_product(matrices)

    def verify_stabilizer_commutation(self):
        """Verify that all stabilizer generators mutually commute."""
        results = {}
        for i in range(4):
            for j in range(i + 1, 4):
                gi = self.stabilizer_generator(i)
                gj = self.stabilizer_generator(j)
                commutator = gi @ gj - gj @ gi
                key = "[g{}, g{}]".format(i + 1, j + 1)
                results[key] = bool(np.allclose(commutator, 0))
        return results

    def code_space_dimension(self):
        """
        Compute dimension of the code space.
        Expected: 2 (encoding 1 logical qubit).
        """
        dim = 32  # 2^5
        projector = np.eye(dim, dtype=complex)
        for i in range(4):
            gi = self.stabilizer_generator(i)
            projector = projector @ (np.eye(dim) + gi) / 2.0
        rank = int(np.round(np.trace(projector).real))
        return rank

    def verify_code_distance(self):
        """
        Verify code distance = 3 by checking that all 15 single-qubit
        errors produce distinct syndromes.
        """
        syndromes = set()
        for qubit in range(5):
            for error_type in ["X", "Y", "Z"]:
                pattern = ["I"] * 5
                pattern[qubit] = error_type
                error_op = self._tensor_product(
                    [self._pauli(p) for p in pattern]
                )
                syndrome = []
                for i in range(4):
                    gi = self.stabilizer_generator(i)
                    anticommutes = np.allclose(error_op @ gi + gi @ error_op, 0)
                    syndrome.append(1 if anticommutes else 0)
                syndromes.add(tuple(syndrome))

        n_distinct = len(syndromes)
        # 15 single-qubit errors -> 15 distinct non-trivial syndromes
        # plus (0,0,0,0) for identity = 16 = 2^4  (perfect code)
        return 3 if n_distinct == 15 else 0

    def verify_hamming_bound(self):
        """
        Verify the quantum Hamming bound: 2^k (1 + 3n) <= 2^n.
        For k=1, d=3: unique solution is n=5.
        """
        results = {}
        for n in range(3, 8):
            lhs = 2 * (1 + 3 * n)
            rhs = 2**n
            results[n] = {"lhs": lhs, "rhs": rhs, "saturates": lhs == rhs}
        return results

    def run_all_tests(self):
        """Run all code verification tests."""
        return {
            "commutation": self.verify_stabilizer_commutation(),
            "code_space_dim": self.code_space_dimension(),
            "code_distance": self.verify_code_distance(),
            "hamming_bound": self.verify_hamming_bound(),
        }


# =============================================================================
# 2. K4 HEISENBERG MODEL
# =============================================================================

class K4Heisenberg:
    """
    Heisenberg antiferromagnet on the complete graph K4.

    H = J * sum_{i<j} S_i . S_j   where J = Hb4

    The spectrum decomposes by total spin:
        S_tot=0:  E = -3J/2,  degeneracy 2
        S_tot=1:  E = -J/2,   degeneracy 9
        S_tot=2:  E = +3J/2,  degeneracy 5
    Total states: 2 + 9 + 5 = 16 = 2^4.
    """

    def __init__(self, exchange_J=None):
        self.J = exchange_J if exchange_J is not None else HB4

        # Spin-1/2 operators
        self.sx = np.array([[0, 1], [1, 0]], dtype=complex) / 2.0
        self.sy = np.array([[0, -1j], [1j, 0]], dtype=complex) / 2.0
        self.sz = np.array([[1, 0], [0, -1]], dtype=complex) / 2.0
        self.id2 = np.eye(2, dtype=complex)

    def spin_operator(self, site, component):
        """Build S_site^component as 16x16 matrix (4 spins on K4 vertices)."""
        ops = [self.id2] * 4
        if component == "x":
            ops[site] = self.sx
        elif component == "y":
            ops[site] = self.sy
        elif component == "z":
            ops[site] = self.sz

        result = ops[0]
        for op in ops[1:]:
            result = np.kron(result, op)
        return result

    def hamiltonian(self):
        """Build the full K4 Heisenberg Hamiltonian (16x16)."""
        dim = 16
        ham = np.zeros((dim, dim), dtype=complex)
        # K4 has 6 edges: all pairs (i,j) with i < j
        for i in range(4):
            for j in range(i + 1, 4):
                for comp in ["x", "y", "z"]:
                    si = self.spin_operator(i, comp)
                    sj = self.spin_operator(j, comp)
                    ham += self.J * si @ sj
        return ham

    def spectrum(self):
        """Diagonalize and return sorted eigenvalues."""
        ham = self.hamiltonian()
        eigenvalues = linalg.eigvalsh(ham)
        return np.sort(eigenvalues)

    def analyze_spectrum(self):
        """
        Analyze spectrum: identify energy levels, degeneracies, and
        verify against analytical predictions.
        """
        eigenvalues = self.spectrum()
        # Round to 10 decimal places to cluster degenerate levels
        rounded = np.round(eigenvalues, 10)
        unique_E, counts = np.unique(rounded, return_counts=True)

        # Analytical predictions
        expected = {
            "S=0": {"energy": -3.0 * self.J / 2.0, "degeneracy": 2},
            "S=1": {"energy": -self.J / 2.0, "degeneracy": 9},
            "S=2": {"energy": 3.0 * self.J / 2.0, "degeneracy": 5},
        }

        return {
            "J": self.J,
            "eigenvalues": unique_E,
            "degeneracies": counts,
            "total_states": int(np.sum(counts)),
            "expected": expected,
        }

    def s4_edge_decomposition(self):
        """
        S4 permutation symmetry decomposes the 6-dim edge representation:
            6 = 1 + 2 + 3  (trivial + standard_2D + standard_3D)
        Maps to the Standard Model gauge group:
            U(1)_Y  +  SU(2)_L  +  SU(3)_c
        """
        return {
            "n_edges": 6,
            "trivial_dim_1": 1,     # -> U(1)_Y
            "standard_dim_2": 2,    # -> SU(2)_L
            "standard_dim_3": 3,    # -> SU(3)_c
            "sum_check": 1 + 2 + 3,
        }


# =============================================================================
# 3. C5 PENTAGON TIGHT-BINDING
# =============================================================================

class C5Pentagon:
    """
    Tight-binding model on the cycle graph C5 (pentagon).

    Laplacian eigenvalues: lambda_k = 2 - 2*cos(2*pi*k/5), k=0..4

    Key result: lambda_2 / lambda_1 = phi^2  (golden ratio squared).
    """

    def __init__(self):
        self.n = 5

    def adjacency_matrix(self):
        """Build adjacency matrix of C5."""
        adj = np.zeros((5, 5))
        for i in range(5):
            adj[i, (i + 1) % 5] = 1.0
            adj[i, (i - 1) % 5] = 1.0
        return adj

    def laplacian(self):
        """Build graph Laplacian L = D - A."""
        adj = self.adjacency_matrix()
        degree = np.diag([2.0] * 5)
        return degree - adj

    def eigenvalues_analytical(self):
        """Exact eigenvalues: lambda_k = 2 - 2*cos(2*pi*k/5)."""
        k = np.arange(5)
        return np.sort(2.0 - 2.0 * np.cos(2.0 * np.pi * k / 5.0))

    def eigenvalues_numerical(self):
        """Numerical eigenvalues from diagonalization."""
        lap = self.laplacian()
        return np.sort(linalg.eigvalsh(lap))

    def verify_golden_ratio(self):
        """
        Verify that lambda_2 / lambda_1 = phi^2.

        Analytical:
            lambda_1 = (5 - sqrt(5)) / 2
            lambda_2 = (5 + sqrt(5)) / 2
            lambda_2 / lambda_1 = phi^2
        """
        eigs = self.eigenvalues_numerical()

        # Non-zero eigenvalues (lambda_0 = 0)
        lambda_1 = eigs[1]
        lambda_2 = eigs[3]
        ratio = lambda_2 / lambda_1

        # Exact values
        lambda_1_exact = (5.0 - np.sqrt(5.0)) / 2.0
        lambda_2_exact = (5.0 + np.sqrt(5.0)) / 2.0

        return {
            "lambda_0": eigs[0],
            "lambda_1_numerical": lambda_1,
            "lambda_1_exact": lambda_1_exact,
            "lambda_2_numerical": lambda_2,
            "lambda_2_exact": lambda_2_exact,
            "ratio": ratio,
            "phi_squared": GOLDEN_RATIO_SQ,
            "match": bool(np.isclose(ratio, GOLDEN_RATIO_SQ, atol=1.0e-12)),
        }

    def mathieu_potential(self, theta):
        """
        Continuum limit gives a 5-fold cosine potential (Mathieu-type).
        V(theta) = lambda_1 * (1 - cos(5*theta))
        """
        lambda_1 = (5.0 - np.sqrt(5.0)) / 2.0
        return lambda_1 * (1.0 - np.cos(5.0 * theta))


# =============================================================================
# 4. GEOMETRIC STRAIN DERIVATION
# =============================================================================

class GeometricStrain:
    """
    Derive the geometric strain sigma from K4-C5 incompatibility.

    sigma = beta_1(K4) / (|Hilbert| * n * phi^2)
          = 3 / (16 * 5 * phi^2)
          = 3 / (80 * phi^2)
          ~ 0.01432

    Components:
        beta_1(K4) = 3          first Betti number of K4
        |Hilbert|  = 2^4 = 16   bulk Hilbert space dimension
        n          = 5           code length
        phi^2      = 2.618...    golden ratio squared (C5 eigenvalue ratio)
    """

    def __init__(self):
        self.betti_1_k4 = 3
        self.hilbert_dim = 16   # 2^4
        self.code_length = 5

    def derive_sigma(self):
        """Derive sigma from graph-theoretic quantities."""
        numerator = float(self.betti_1_k4)
        denominator = float(self.hilbert_dim * self.code_length) * GOLDEN_RATIO_SQ
        return numerator / denominator

    def verify(self):
        """Full verification against QSD constant."""
        sigma_derived = self.derive_sigma()
        sigma_formula = 3.0 / (80.0 * GOLDEN_RATIO_SQ)

        return {
            "betti_1_K4": self.betti_1_k4,
            "hilbert_dim": self.hilbert_dim,
            "code_length": self.code_length,
            "phi_squared": GOLDEN_RATIO_SQ,
            "sigma_derived": sigma_derived,
            "sigma_formula": sigma_formula,
            "sigma_module": SIGMA,
            "all_match": (
                np.isclose(sigma_derived, SIGMA, atol=1.0e-14)
                and np.isclose(sigma_formula, SIGMA, atol=1.0e-14)
            ),
            "nu_rad": HB4 / sigma_derived,
            "alpha_inv_times_sigma": ALPHA_INV_QSD * sigma_derived,
        }


# =============================================================================
# 5. TOPOLOGICAL RENORMALIZATION (3-loop, derived from triad)
# =============================================================================

class TopologicalRenormalization:
    """
    QSD 3-loop renormalization of the fine structure constant.

    The series TERMINATES at 3 loops because K4 has exactly
    beta_1(K4) = 3 independent cycles. A 4th loop would require
    a 4th independent cycle, which does not exist.

    All terms are derived analytically from the triad {Hb4, sigma, varpi}.
    NO hardcoded loop values.

    alpha^-1 = (6*varpi / Hb4)
             + (6*sigma / Hb4)
             - (24*sigma^2*phi / Hb4)
             - (24*sigma^2*phi / (pi*Hb4))
    """

    def compute_all(self):
        """Compute alpha^-1 through the 3-loop series."""
        tree = 6.0 * VARPI / HB4
        d1 = 6.0 * SIGMA / HB4
        d2 = 24.0 * SIGMA**2 * GOLDEN_RATIO / HB4
        d3 = d2 / np.pi

        alpha_inv = tree + d1 - d2 - d3

        # Expansion parameter
        eta = SIGMA / VARPI
        convergence_ratio = 4.0 * SIGMA * GOLDEN_RATIO

        return {
            "tree_level": tree,
            "loop_1_info_friction": d1,
            "loop_2_symmetry_feedback": d2,
            "loop_3_angular_screening": d3,
            "alpha_inv_qsd": alpha_inv,
            "alpha_inv_exp": ALPHA_INV_EXP,
            "error_ppm": abs(alpha_inv - ALPHA_INV_EXP) / ALPHA_INV_EXP * 1.0e6,
            "expansion_parameter_eta": eta,
            "convergence_ratio_4dphi": convergence_ratio,
        }

    def weak_mixing_angle(self):
        """
        Compute sin^2(theta_W) from generator counting.

        Tree: 3/13  (13 = 8+3+1+1 gauge generators, 3 from SU(2)_L)
        Correction: sigma/32  (32 = 2^5, Hilbert space dimension)
        """
        tree = 3.0 / 13.0
        correction = SIGMA / 32.0
        result = tree + correction

        return {
            "tree_level": tree,
            "hilbert_correction": correction,
            "sin2_theta_qsd": result,
            "sin2_theta_exp": SIN2_THETA_EXP,
            "error_percent": abs(result - SIN2_THETA_EXP) / SIN2_THETA_EXP * 100.0,
        }


# =============================================================================
# 6. STRONG COUPLING
# =============================================================================

class StrongCoupling:
    """
    QSD prediction for the strong coupling constant.

    alpha_s = varpi * sigma = pi * phi^2 * sigma = 3*pi/80

    The golden ratio cancels exactly because varpi ~ phi^2
    and sigma ~ 1/phi^2. This makes alpha_s depend only on pi
    and the integers 3 and 80 from the code structure.

    Satisfies the gauge identity: 6*alpha_s = alpha_inv_tree * Hb4 * sigma
    """

    def compute(self):
        """Compute alpha_s and verify identities."""
        alpha_s_from_triad = VARPI * SIGMA
        alpha_s_simplified = 3.0 * np.pi / 80.0

        # Gauge identity
        identity_lhs = 6.0 * alpha_s_from_triad
        identity_rhs = ALPHA_INV_TREE * HB4 * SIGMA

        return {
            "alpha_s_from_triad": alpha_s_from_triad,
            "alpha_s_simplified": alpha_s_simplified,
            "golden_ratio_cancels": abs(alpha_s_from_triad - alpha_s_simplified) < 1.0e-14,
            "alpha_s_exp": ALPHA_S_EXP,
            "error_percent": abs(alpha_s_from_triad - ALPHA_S_EXP) / ALPHA_S_EXP * 100.0,
            "gauge_identity_lhs": identity_lhs,
            "gauge_identity_rhs": identity_rhs,
            "gauge_identity_holds": abs(identity_lhs - identity_rhs) < 1.0e-12,
        }


# =============================================================================
# 7. ENERGY SCALE DERIVATION
# =============================================================================

class EnergyScale:
    """
    Derive the QSD energy scale mu_rad from the Planck mass.

    mu_rad = (M_Pl / 2^60) * phi^2 * (1 - 6*sigma)

    This solves the hierarchy problem: why is m_H << M_Pl?
    The ratio is not fine-tuned but fixed by the information
    content of the [[5,1,3]] code.
    """

    def full_analysis(self):
        """Complete energy scale analysis with consistency check."""
        mu_rad = MU_RAD
        nu_rad = NU_RAD
        xi = XI_DRESSING

        m_higgs = 5.0 * mu_rad
        e_syndrome = mu_rad * (1.0 + 8.0 * SIGMA)
        m_w = (16.0 / 5.0) * mu_rad

        return {
            "M_Planck_GeV": M_PLANCK_GEV,
            "two_to_60": 2**60,
            "base_energy_GeV": E_BASE,
            "phi_squared": GOLDEN_RATIO_SQ,
            "strain_correction_1m6d": STRAIN_CORRECTION,
            "mu_rad_GeV": mu_rad,
            "nu_rad_dimensionless": nu_rad,
            "xi_dressing_GeV": xi,
            "xi_deviation_percent": abs(xi - 1.0) * 100.0,
            "higgs_mass_GeV": m_higgs,
            "higgs_exp_GeV": M_HIGGS_EXP,
            "higgs_error_percent": abs(m_higgs - M_HIGGS_EXP) / M_HIGGS_EXP * 100.0,
            "syndrome_energy_GeV": e_syndrome,
            "syndrome_CMS_GeV": E_SYNDROME_CMS,
            "syndrome_error_percent": abs(e_syndrome - E_SYNDROME_CMS) / E_SYNDROME_CMS * 100.0,
            "w_boson_GeV": m_w,
            "w_boson_exp_GeV": M_W_EXP,
            "w_boson_error_percent": abs(m_w - M_W_EXP) / M_W_EXP * 100.0,
        }


# =============================================================================
# 8. COSMOLOGICAL CONSTANT
# =============================================================================

class CosmologicalConstant:
    """
    QSD conjecture (S7): the vacuum energy density is the Planck density
    suppressed by a Boltzmann factor for computational entropy:

        rho_Lambda = rho_Planck * exp(-4/sigma)

    The entropy barrier 4/sigma ~ 279 nats explains 121 orders of magnitude
    from a single calculable quantity.
    """

    def compute(self):
        """Compute the cosmological constant prediction."""
        barrier = 4.0 / SIGMA
        log10_ratio = -barrier / np.log(10.0)
        ratio = np.exp(-barrier)

        return {
            "entropy_barrier_nats": barrier,
            "log10_rho_ratio_qsd": log10_ratio,
            "log10_rho_ratio_obs": LAMBDA_OBS_LOG10,
            "residual_log10": abs(log10_ratio - LAMBDA_OBS_LOG10),
            "ratio_qsd_over_obs": 10.0**(log10_ratio - LAMBDA_OBS_LOG10),
        }


# =============================================================================
# 9. PROTON LIFETIME
# =============================================================================

class ProtonLifetime:
    """
    QSD proton lifetime from the GUT scale M_X = M_Planck * sigma.

    Standard dimensional scaling:
        tau_p ~ (M_X / m_p)^4 / m_p

    QSD predicts tau_p ~ 10^39 years, well above current bounds
    (~10^34 years from Super-Kamiokande) but potentially testable
    at Hyper-Kamiokande (~10^35 sensitivity).
    """

    def compute(self):
        """Compute proton lifetime estimate."""
        m_p = 0.9382720813  # proton mass in GeV (CODATA)
        m_x = M_PLANCK_GEV * SIGMA

        # tau_p in natural units (GeV^-1)
        tau_natural = (m_x / m_p)**4 / m_p

        # Convert to years
        gev_inv_to_seconds = 6.582119569e-25
        seconds_per_year = 3.15576e7
        tau_seconds = tau_natural * gev_inv_to_seconds
        tau_years = tau_seconds / seconds_per_year

        return {
            "M_X_GeV": m_x,
            "m_proton_GeV": m_p,
            "M_X_over_m_p": m_x / m_p,
            "tau_p_years": tau_years,
            "log10_tau_p": np.log10(tau_years),
            "Super_K_bound_years": 2.4e34,
            "Hyper_K_sensitivity_years": 1.0e35,
            "safe_from_Super_K": tau_years > 2.4e34,
        }


# =============================================================================
# 10. MASTER RELATIONS AND IDENTITIES
# =============================================================================

class MasterRelations:
    """
    Verify the algebraic identities connecting QSD parameters.

    1. Gauge identity:  6*alpha_s = alpha_inv_tree * Hb4 * sigma
    2. Landauer identity:  Hb_n * ln(2) = 1/n  (for any n)
    3. Golden cancellation:  alpha_s = 3*pi/80  (phi^2 cancels)
    4. Dimension universality:  Hb_n = 1/(n*ln(2)) for n = 2,3,4,...
    """

    def verify_all(self):
        """Verify all master relations."""
        results = {}

        # 1. Gauge identity
        lhs_1 = 6.0 * ALPHA_S_QSD
        rhs_1 = ALPHA_INV_TREE * HB4 * SIGMA
        results["gauge_identity"] = {
            "lhs_6_alpha_s": lhs_1,
            "rhs_tree_Hb4_sigma": rhs_1,
            "difference": abs(lhs_1 - rhs_1),
            "verified": abs(lhs_1 - rhs_1) < 1.0e-12,
        }

        # 2. Landauer identity for n=4
        product = HB4 * LN2
        results["landauer_n4"] = {
            "Hb4_times_ln2": product,
            "expected": 0.25,
            "difference": abs(product - 0.25),
            "verified": abs(product - 0.25) < 1.0e-14,
        }

        # 3. Golden cancellation
        diff = abs(ALPHA_S_QSD - 3.0 * np.pi / 80.0)
        results["golden_cancellation"] = {
            "alpha_s_from_varpi_sigma": ALPHA_S_QSD,
            "alpha_s_from_3pi_80": 3.0 * np.pi / 80.0,
            "difference": diff,
            "verified": diff < 1.0e-14,
        }

        # 4. Dimension universality
        dim_results = {}
        for n in [2, 3, 4, 5, 6]:
            hb_n = holographic_bit_density(n)
            check = hb_n * LN2
            dim_results[n] = {
                "Hb_n": hb_n,
                "Hb_n_times_ln2": check,
                "expected_1_over_n": 1.0 / n,
                "verified": abs(check - 1.0 / n) < 1.0e-14,
            }
        results["dimension_universality"] = dim_results

        # 5. alpha^-1 * sigma (approximate relation, NOT exactly 2)
        product_ad = ALPHA_INV_QSD * SIGMA
        results["alpha_sigma_product"] = {
            "alpha_inv_qsd_times_sigma": product_ad,
            "note": "Approximately 2 but NOT exactly 2",
        }

        return results


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_full_simulation_suite():
    """Run all QSD simulations and print results."""

    sep = "=" * 72
    subsep = "-" * 72

    print(sep)
    print("QSD SIMULATION SUITE -- COMPUTATIONAL VALIDATION")
    print(sep)

    # 1. [[5,1,3]] Code
    print("\n" + sep)
    print("1. [[5,1,3]] QUANTUM ERROR-CORRECTING CODE")
    print(sep)
    code = Code513()
    tests = code.run_all_tests()
    comm = tests["commutation"]
    print("  Stabilizer commutation:  {}".format(
        "ALL PASS" if all(comm.values()) else "FAILED"))
    print("  Code space dimension:    {} (expected: 2)".format(
        tests["code_space_dim"]))
    print("  Code distance:           {} (expected: 3)".format(
        tests["code_distance"]))
    hb = tests["hamming_bound"]
    for n_val in sorted(hb.keys()):
        entry = hb[n_val]
        mark = " <-- SATURATES (perfect code)" if entry["saturates"] else ""
        print("    n={}: 2(1+3n)={} vs 2^n={}{}".format(
            n_val, entry["lhs"], entry["rhs"], mark))

    # 2. K4 Heisenberg
    print("\n" + sep)
    print("2. K4 HEISENBERG MODEL (J = Hb4)")
    print(sep)
    k4 = K4Heisenberg()
    spectrum = k4.analyze_spectrum()
    print("  Exchange coupling J = Hb4 = {:.10f}".format(spectrum["J"]))
    for i, (e_val, deg) in enumerate(
            zip(spectrum["eigenvalues"], spectrum["degeneracies"])):
        e_in_j = e_val / spectrum["J"]
        print("  Level {}: E/J = {:+.6f}, degeneracy = {}".format(
            i, e_in_j, deg))
    print("  Total states: {} (expected: 16)".format(spectrum["total_states"]))

    decomp = k4.s4_edge_decomposition()
    print("\n  S4 edge decomposition: 6 = {} + {} + {}".format(
        decomp["trivial_dim_1"], decomp["standard_dim_2"],
        decomp["standard_dim_3"]))
    print("  Maps to: U(1)_Y + SU(2)_L + SU(3)_c")

    # 3. C5 Pentagon
    print("\n" + sep)
    print("3. C5 PENTAGON TIGHT-BINDING")
    print(sep)
    c5 = C5Pentagon()
    gr = c5.verify_golden_ratio()
    print("  lambda_0 = {:.10f} (expected: 0)".format(gr["lambda_0"]))
    print("  lambda_1 = {:.10f} (exact: {:.10f})".format(
        gr["lambda_1_numerical"], gr["lambda_1_exact"]))
    print("  lambda_2 = {:.10f} (exact: {:.10f})".format(
        gr["lambda_2_numerical"], gr["lambda_2_exact"]))
    print("  lambda_2 / lambda_1 = {:.10f}".format(gr["ratio"]))
    print("  phi^2               = {:.10f}".format(gr["phi_squared"]))
    print("  Match: {}".format(gr["match"]))

    # 4. Geometric Strain
    print("\n" + sep)
    print("4. GEOMETRIC STRAIN DERIVATION")
    print(sep)
    strain = GeometricStrain()
    sv = strain.verify()
    print("  beta_1(K4)     = {}".format(sv["betti_1_K4"]))
    print("  |Hilbert|      = {}".format(sv["hilbert_dim"]))
    print("  code length n  = {}".format(sv["code_length"]))
    print("  phi^2          = {:.10f}".format(sv["phi_squared"]))
    print("  sigma derived  = {:.12f}".format(sv["sigma_derived"]))
    print("  sigma formula  = {:.12f}".format(sv["sigma_formula"]))
    print("  sigma module   = {:.12f}".format(sv["sigma_module"]))
    print("  All match:       {}".format(sv["all_match"]))
    print("  nu_rad = Hb4/sigma = {:.10f}".format(sv["nu_rad"]))
    print("  alpha^-1 * sigma   = {:.10f} (approx 2)".format(
        sv["alpha_inv_times_sigma"]))

    # 5. Topological Renormalization
    print("\n" + sep)
    print("5. TOPOLOGICAL RENORMALIZATION (3-loop, from triad)")
    print(sep)
    renorm = TopologicalRenormalization()
    alpha = renorm.compute_all()
    print("  Tree:   6*varpi/Hb4          = {:.10f}".format(
        alpha["tree_level"]))
    print("  1-loop: +6*sigma/Hb4         = +{:.10f}".format(
        alpha["loop_1_info_friction"]))
    print("  2-loop: -24*sigma^2*phi/Hb4  = -{:.10f}".format(
        alpha["loop_2_symmetry_feedback"]))
    print("  3-loop: -loop2/pi            = -{:.10f}".format(
        alpha["loop_3_angular_screening"]))
    print("  " + subsep)
    print("  alpha^-1 (QSD)  = {:.10f}".format(alpha["alpha_inv_qsd"]))
    print("  alpha^-1 (exp)  = {:.9f}".format(alpha["alpha_inv_exp"]))
    print("  Error           = {:.1f} ppm".format(alpha["error_ppm"]))
    print("  Expansion param = {:.6f} (<<1, series converges)".format(
        alpha["expansion_parameter_eta"]))

    theta = renorm.weak_mixing_angle()
    print("\n  sin^2(theta_W):")
    print("    Tree: 3/13      = {:.10f}".format(theta["tree_level"]))
    print("    Correction: d/32= {:.10f}".format(theta["hilbert_correction"]))
    print("    QSD result      = {:.10f}".format(theta["sin2_theta_qsd"]))
    print("    Experiment      = {}".format(theta["sin2_theta_exp"]))
    print("    Error           = {:.3f}%".format(theta["error_percent"]))

    # 6. Strong Coupling
    print("\n" + sep)
    print("6. STRONG COUPLING alpha_s")
    print(sep)
    sc = StrongCoupling()
    scr = sc.compute()
    print("  alpha_s = varpi * sigma  = {:.12f}".format(
        scr["alpha_s_from_triad"]))
    print("  alpha_s = 3*pi/80        = {:.12f}".format(
        scr["alpha_s_simplified"]))
    print("  Golden ratio cancels:      {}".format(
        scr["golden_ratio_cancels"]))
    print("  alpha_s (exp)            = {}".format(scr["alpha_s_exp"]))
    print("  Error                    = {:.2f}%".format(
        scr["error_percent"]))
    print("  Gauge identity: 6*alpha_s = alpha_inv_tree * Hb4 * sigma")
    print("    LHS = {:.12f}".format(scr["gauge_identity_lhs"]))
    print("    RHS = {:.12f}".format(scr["gauge_identity_rhs"]))
    print("    Holds: {}".format(scr["gauge_identity_holds"]))

    # 7. Energy Scale
    print("\n" + sep)
    print("7. ENERGY SCALE DERIVATION")
    print(sep)
    energy = EnergyScale()
    ev = energy.full_analysis()
    print("  M_Planck              = {:.5e} GeV".format(ev["M_Planck_GeV"]))
    print("  2^60                  = {:.5e}".format(float(ev["two_to_60"])))
    print("  Base energy           = {:.10f} GeV".format(
        ev["base_energy_GeV"]))
    print("  phi^2 enhancement     = {:.10f}".format(ev["phi_squared"]))
    print("  Strain corr (1-6d)   = {:.10f}".format(
        ev["strain_correction_1m6d"]))
    print("  " + subsep)
    print("  mu_rad (dimensionful) = {:.10f} GeV".format(ev["mu_rad_GeV"]))
    print("  nu_rad (dimensionless)= {:.10f}".format(
        ev["nu_rad_dimensionless"]))
    print("  xi (dressing factor)  = {:.10f} GeV".format(
        ev["xi_dressing_GeV"]))
    print("  xi deviation from 1   = {:.4f}%".format(
        ev["xi_deviation_percent"]))
    print()
    print("  {:20s} {:>12s} {:>12s} {:>10s}".format(
        "Observable", "QSD", "Experiment", "Error"))
    print("  " + subsep)
    for name, qsd_key, exp_key, err_key in [
        ("m_H (GeV)", "higgs_mass_GeV", "higgs_exp_GeV",
         "higgs_error_percent"),
        ("E_syn (GeV)", "syndrome_energy_GeV", "syndrome_CMS_GeV",
         "syndrome_error_percent"),
        ("m_W (GeV)", "w_boson_GeV", "w_boson_exp_GeV",
         "w_boson_error_percent"),
    ]:
        print("  {:20s} {:>12.4f} {:>12.4f} {:>9.3f}%".format(
            name, ev[qsd_key], ev[exp_key], ev[err_key]))

    # 8. Cosmological Constant
    print("\n" + sep)
    print("8. COSMOLOGICAL CONSTANT (S7 conjecture)")
    print(sep)
    cc = CosmologicalConstant()
    ccr = cc.compute()
    print("  Entropy barrier 4/sigma = {:.6f} nats".format(
        ccr["entropy_barrier_nats"]))
    print("  log10(rho_L/rho_Pl) QSD = {:.4f}".format(
        ccr["log10_rho_ratio_qsd"]))
    print("  log10(rho_L/rho_Pl) obs = {}".format(
        ccr["log10_rho_ratio_obs"]))
    print("  Residual |sigma log10|  = {:.4f}".format(
        ccr["residual_log10"]))
    print("  QSD/obs ratio           = {:.4f}".format(
        ccr["ratio_qsd_over_obs"]))

    # 9. Proton Lifetime
    print("\n" + sep)
    print("9. PROTON LIFETIME (S5 prediction)")
    print(sep)
    pl = ProtonLifetime()
    plr = pl.compute()
    print("  M_X = M_Pl * sigma   = {:.4e} GeV".format(plr["M_X_GeV"]))
    print("  M_X / m_p            = {:.4e}".format(plr["M_X_over_m_p"]))
    print("  tau_p                ~ {:.2e} years".format(plr["tau_p_years"]))
    print("  log10(tau_p/year)    = {:.2f}".format(plr["log10_tau_p"]))
    print("  Super-K bound        > {:.1e} years  [SAFE: {}]".format(
        plr["Super_K_bound_years"], plr["safe_from_Super_K"]))
    print("  Hyper-K sensitivity  ~ {:.1e} years".format(
        plr["Hyper_K_sensitivity_years"]))

    # 10. Master Relations
    print("\n" + sep)
    print("10. MASTER RELATIONS AND IDENTITIES")
    print(sep)
    mr = MasterRelations()
    mrr = mr.verify_all()

    gi = mrr["gauge_identity"]
    print("  Gauge identity: 6*alpha_s = alpha_inv_tree * Hb4 * sigma")
    print("    LHS = {:.12f}".format(gi["lhs_6_alpha_s"]))
    print("    RHS = {:.12f}".format(gi["rhs_tree_Hb4_sigma"]))
    print("    |diff| = {:.2e}  [{}]".format(
        gi["difference"], "PASS" if gi["verified"] else "FAIL"))

    li = mrr["landauer_n4"]
    print("  Landauer identity: Hb4 * ln(2) = 1/4")
    print("    Product = {:.15f}  [{}]".format(
        li["Hb4_times_ln2"], "PASS" if li["verified"] else "FAIL"))

    gc = mrr["golden_cancellation"]
    print("  Golden cancellation: varpi*sigma = 3*pi/80")
    print("    |diff| = {:.2e}  [{}]".format(
        gc["difference"], "PASS" if gc["verified"] else "FAIL"))

    du = mrr["dimension_universality"]
    for n_val in sorted(du.keys()):
        entry = du[n_val]
        print("    n={}: Hb_{} * ln(2) = {:.15f} = 1/{}  [{}]".format(
            n_val, n_val, entry["Hb_n_times_ln2"], n_val,
            "PASS" if entry["verified"] else "FAIL"))

    ad = mrr["alpha_sigma_product"]
    print("  alpha^-1 * sigma = {:.10f}  (approx 2, NOT exact)".format(
        ad["alpha_inv_qsd_times_sigma"]))

    # Summary Table
    print("\n" + sep)
    print("SUMMARY: QSD PREDICTIONS vs EXPERIMENT")
    print(sep)
    print("  {:20s} {:>14s} {:>14s} {:>10s}".format(
        "Quantity", "QSD", "Experiment", "Error"))
    print("  " + subsep)
    summary_data = [
        ("alpha^-1", ALPHA_INV_QSD, ALPHA_INV_EXP, "ppm",
         abs(ALPHA_INV_QSD - ALPHA_INV_EXP) / ALPHA_INV_EXP * 1.0e6),
        ("alpha_s", ALPHA_S_QSD, ALPHA_S_EXP, "%",
         abs(ALPHA_S_QSD - ALPHA_S_EXP) / ALPHA_S_EXP * 100.0),
        ("sin^2(theta_W)", SIN2_THETA_QSD, SIN2_THETA_EXP, "%",
         abs(SIN2_THETA_QSD - SIN2_THETA_EXP) / SIN2_THETA_EXP * 100.0),
        ("m_H (GeV)", M_HIGGS_QSD, M_HIGGS_EXP, "%",
         abs(M_HIGGS_QSD - M_HIGGS_EXP) / M_HIGGS_EXP * 100.0),
        ("E_syn (GeV)", E_SYNDROME_QSD, E_SYNDROME_CMS, "%",
         abs(E_SYNDROME_QSD - E_SYNDROME_CMS) / E_SYNDROME_CMS * 100.0),
        ("m_W (GeV)", M_W_QSD, M_W_EXP, "%",
         abs(M_W_QSD - M_W_EXP) / M_W_EXP * 100.0),
    ]
    for name, qsd_val, exp_val, unit, err in summary_data:
        if unit == "ppm":
            print("  {:20s} {:>14.6f} {:>14.6f} {:>8.1f} ppm".format(
                name, qsd_val, exp_val, err))
        else:
            print("  {:20s} {:>14.6f} {:>14.6f} {:>8.3f} %".format(
                name, qsd_val, exp_val, err))

    print(sep)
    print("All predictions derived from M_Planck alone (zero free parameters)")
    print("Triad: Hb4 = {:.6f}, sigma = {:.10f}, varpi = {:.6f}".format(
        HB4, SIGMA, VARPI))
    print(sep)


if __name__ == "__main__":
    run_full_simulation_suite()
