#!/usr/bin/env python3
"""
QSD Monte Carlo Error Propagation
==================================

Rigorous uncertainty quantification for QSD predictions.

Propagates uncertainties in the Planck mass through the QSD derivation
chain. The only experimental input is M_Planck; all other parameters
(phi, ln 2, pi) are mathematical constants with zero uncertainty.

Theory uncertainties at each loop order are estimated from the
topological structure, NOT fitted to experiment.

All constants imported from qsd_constants.py.
No unicode characters. Intermediate precision >= 10 decimal places.

Author: M. Hubka
Date: February 2026
"""

import numpy as np
from scipy import stats
from typing import Tuple, Dict, List
import matplotlib
matplotlib.rcParams["text.usetex"] = False
import matplotlib.pyplot as plt
import os

from qsd_constants import (
    GOLDEN_RATIO, GOLDEN_RATIO_SQ, LN2,
    HB4, SIGMA, VARPI,
    ALPHA_INV_TREE, LOOP_1, LOOP_2, LOOP_3, ALPHA_INV_QSD,
    ALPHA_S_QSD, SIN2_THETA_QSD,
    M_PLANCK_GEV, MU_RAD, M_HIGGS_QSD, E_SYNDROME_QSD, M_W_QSD,
    ALPHA_INV_EXP, ALPHA_S_EXP, SIN2_THETA_EXP,
    M_HIGGS_EXP, E_SYNDROME_CMS, M_W_EXP,
)


class UncertainValue:
    """A value with associated uncertainty."""

    def __init__(self, value, uncertainty, name=""):
        self.value = value
        self.uncertainty = uncertainty
        self.name = name

    def __repr__(self):
        return "{}: {:.10f} +/- {:.10f}".format(
            self.name, self.value, self.uncertainty)

    def relative_error(self):
        if abs(self.value) < 1.0e-30:
            return 0.0
        return self.uncertainty / abs(self.value)


class QSDMonteCarlo:
    """
    Monte Carlo propagation of uncertainties through QSD calculations.

    Input uncertainties:
        M_Planck: +/- 0.00006 * 10^19 GeV (CODATA 2018)
        phi, ln(2), pi: exact (mathematical constants)

    The derivation chain:
        Hb4   = 1/(4 ln 2)          (exact)
        delta = 3/(80 phi^2)         (exact)
        varpi = pi * phi^2           (exact)
        mu_rad = (M_Pl/2^60) * phi^2 * (1 - 6*delta)   (M_Pl dependent)
        m_H = 5 * mu_rad             (M_Pl dependent)
        E_syn = mu_rad * (1 + 8*delta)  (M_Pl dependent)
        m_W = (16/5) * mu_rad        (M_Pl dependent)
        alpha^-1 from 3-loop         (exact + theory uncertainty)
        alpha_s = 3*pi/80            (exact)
        sin^2(theta_W) = 3/13 + delta/32  (exact + theory uncertainty)

    Theory uncertainties for loop corrections are bounded by the
    expansion parameter eta = delta/varpi ~ 1/574.
    """

    def __init__(self, n_samples=100000):
        self.n_samples = n_samples

        # Planck mass: sole experimental input
        self.m_pl_mean = 1.22089e19
        self.m_pl_std = 0.00006e19

        # Exact mathematical constants
        self.phi = GOLDEN_RATIO
        self.phi_sq = GOLDEN_RATIO_SQ
        self.ln2 = LN2

        # Exact derived constants (no uncertainty)
        self.hb4 = HB4
        self.delta = SIGMA
        self.varpi = VARPI

        # Experimental references (for comparison only)
        self.exp_alpha_inv = UncertainValue(137.035999084, 0.000000021,
                                            "alpha^-1 (exp)")
        self.exp_alpha_s = UncertainValue(0.1180, 0.0009, "alpha_s (exp)")
        self.exp_sin2_theta = UncertainValue(0.23122, 0.00003,
                                             "sin^2(theta_W) (exp)")
        self.exp_m_higgs = UncertainValue(125.25, 0.17, "m_H (exp)")
        self.exp_e_syndrome = UncertainValue(28.3, 0.5, "E_syn (CMS)")
        self.exp_m_w = UncertainValue(80.377, 0.012, "m_W (exp)")

    def sample_planck_mass(self):
        """Sample Planck mass from Gaussian."""
        return np.random.normal(self.m_pl_mean, self.m_pl_std,
                                self.n_samples)

    def compute_mass_predictions(self, m_pl_samples):
        """
        Compute energy-scale predictions for each M_Pl sample.
        Only mu_rad and its derivatives carry experimental uncertainty.
        """
        base_energy = m_pl_samples / (2.0**60)
        strain_corr = 1.0 - 6.0 * self.delta
        mu_rad = base_energy * self.phi_sq * strain_corr

        return {
            "mu_rad": mu_rad,
            "m_higgs": 5.0 * mu_rad,
            "e_syndrome": mu_rad * (1.0 + 8.0 * self.delta),
            "m_w": (16.0 / 5.0) * mu_rad,
        }

    def compute_alpha_inverse(self, include_theory_unc=True):
        """
        Compute alpha^-1 with Monte Carlo for theory uncertainty.

        Theory uncertainties estimated from expansion parameter:
            eta = delta/varpi ~ 1.74e-3
            Tree uncertainty: eta * alpha_inv_tree ~ 0.24
            But topological fixing constrains this to about +/- 0.005 per loop.
        """
        if include_theory_unc:
            # Tree level: uncertainty from spectral bond definition
            tree_samples = np.random.normal(
                ALPHA_INV_TREE, 0.005, self.n_samples)
            # 1-loop: uncertainty from friction model
            d1_samples = np.random.normal(LOOP_1, 0.003, self.n_samples)
            # 2-loop: uncertainty from S4 channel counting
            d2_samples = np.random.normal(LOOP_2, 0.002, self.n_samples)
            # 3-loop: uncertainty from angular screening model
            d3_samples = np.random.normal(LOOP_3, 0.001, self.n_samples)

            return tree_samples + d1_samples - d2_samples - d3_samples
        else:
            return np.full(self.n_samples, ALPHA_INV_QSD)

    def compute_sin2_theta(self, include_theory_unc=True):
        """
        Compute sin^2(theta_W) with theory uncertainty.
        """
        central = SIN2_THETA_QSD
        if include_theory_unc:
            # Theory uncertainty from generator-counting assumption
            return np.random.normal(central, 0.0005, self.n_samples)
        return np.full(self.n_samples, central)

    def compute_alpha_s(self, include_theory_unc=True):
        """
        Compute alpha_s. This is exact at tree level (3*pi/80).
        Theory uncertainty from possible loop corrections.
        """
        central = ALPHA_S_QSD
        if include_theory_unc:
            return np.random.normal(central, 0.0002, self.n_samples)
        return np.full(self.n_samples, central)

    def run_full_analysis(self):
        """Run complete Monte Carlo analysis."""
        print("Running Monte Carlo with {:,} samples...".format(
            self.n_samples))

        m_pl_samples = self.sample_planck_mass()
        masses = self.compute_mass_predictions(m_pl_samples)
        alpha_inv = self.compute_alpha_inverse(include_theory_unc=True)
        alpha_s = self.compute_alpha_s(include_theory_unc=True)
        sin2_theta = self.compute_sin2_theta(include_theory_unc=True)

        results = {}
        for name, samples in masses.items():
            results[name] = UncertainValue(
                np.mean(samples), np.std(samples), name)

        results["alpha_inv"] = UncertainValue(
            np.mean(alpha_inv), np.std(alpha_inv), "alpha^-1")
        results["alpha_s"] = UncertainValue(
            np.mean(alpha_s), np.std(alpha_s), "alpha_s")
        results["sin2_theta"] = UncertainValue(
            np.mean(sin2_theta), np.std(sin2_theta), "sin^2(theta_W)")

        return results

    def compute_correlations(self):
        """Compute correlation matrix between QSD predictions."""
        m_pl_samples = self.sample_planck_mass()
        masses = self.compute_mass_predictions(m_pl_samples)
        alpha_inv = self.compute_alpha_inverse()
        alpha_s = self.compute_alpha_s()
        sin2_theta = self.compute_sin2_theta()

        data = np.column_stack([
            masses["mu_rad"], masses["m_higgs"], masses["e_syndrome"],
            masses["m_w"], alpha_inv, alpha_s, sin2_theta,
        ])
        names = [r"$\mu_{\mathrm{rad}}$", r"$m_H$",
                 r"$E_{\mathrm{syn}}$", r"$m_W$",
                 r"$\alpha^{-1}$", r"$\alpha_s$",
                 r"$\sin^2\theta_W$"]
        return np.corrcoef(data.T), names

    def chi_square_test(self):
        """Chi-squared test: QSD predictions vs experiment."""
        results = self.run_full_analysis()

        comparisons = {
            "alpha_inv": (results["alpha_inv"], self.exp_alpha_inv),
            "alpha_s": (results["alpha_s"], self.exp_alpha_s),
            "sin2_theta": (results["sin2_theta"], self.exp_sin2_theta),
            "m_higgs": (results["m_higgs"], self.exp_m_higgs),
            "e_syndrome": (results["e_syndrome"], self.exp_e_syndrome),
            "m_w": (results["m_w"], self.exp_m_w),
        }

        chi2_results = {}
        for name, (qsd, exp) in comparisons.items():
            sigma_combined = np.sqrt(
                qsd.uncertainty**2 + exp.uncertainty**2)
            if sigma_combined < 1.0e-30:
                sigma_combined = max(qsd.uncertainty, exp.uncertainty, 1.0e-10)
            chi2 = ((qsd.value - exp.value) / sigma_combined)**2
            p_value = 1.0 - stats.chi2.cdf(chi2, df=1)
            n_sigma = abs(qsd.value - exp.value) / sigma_combined

            chi2_results[name] = {
                "qsd_val": qsd.value,
                "qsd_unc": qsd.uncertainty,
                "exp_val": exp.value,
                "exp_unc": exp.uncertainty,
                "chi2": chi2,
                "p_value": p_value,
                "n_sigma": n_sigma,
                "consistent_2sigma": n_sigma < 2.0,
            }
        return chi2_results


# =============================================================================
# PLOTTING
# =============================================================================

def plot_monte_carlo_distributions(mc, save_path=None):
    """Plot distributions of Monte Carlo samples."""
    m_pl_samples = mc.sample_planck_mass()
    masses = mc.compute_mass_predictions(m_pl_samples)
    alpha_inv = mc.compute_alpha_inverse()
    alpha_s = mc.compute_alpha_s()
    sin2_theta = mc.compute_sin2_theta()

    fig, axes = plt.subplots(2, 3, figsize=(15, 9))

    # mu_rad
    ax = axes[0, 0]
    ax.hist(masses["mu_rad"], bins=60, density=True, alpha=0.7,
            color="steelblue")
    ax.axvline(np.mean(masses["mu_rad"]), color="red", linestyle="--",
               label="Mean")
    ax.set_xlabel(r"$\mu_{\mathrm{rad}}$ (GeV)")
    ax.set_title(r"Code Scale $\mu_{\mathrm{rad}}$")
    ax.legend(fontsize=8)

    # m_H
    ax = axes[0, 1]
    ax.hist(masses["m_higgs"], bins=60, density=True, alpha=0.7,
            color="steelblue")
    ax.axvline(M_HIGGS_EXP, color="orange", linestyle="--", linewidth=2,
               label="Exp: {:.2f}".format(M_HIGGS_EXP))
    ax.axvline(np.mean(masses["m_higgs"]), color="red", linestyle="--",
               label="QSD mean")
    ax.set_xlabel(r"$m_H$ (GeV)")
    ax.set_title("Higgs Mass")
    ax.legend(fontsize=8)

    # E_syn
    ax = axes[0, 2]
    ax.hist(masses["e_syndrome"], bins=60, density=True, alpha=0.7,
            color="steelblue")
    ax.axvline(E_SYNDROME_CMS, color="orange", linestyle="--", linewidth=2,
               label="CMS: {:.1f}".format(E_SYNDROME_CMS))
    ax.axvline(np.mean(masses["e_syndrome"]), color="red", linestyle="--",
               label="QSD mean")
    ax.set_xlabel(r"$E_{\mathrm{syn}}$ (GeV)")
    ax.set_title("Syndrome Energy")
    ax.legend(fontsize=8)

    # alpha^-1
    ax = axes[1, 0]
    ax.hist(alpha_inv, bins=60, density=True, alpha=0.7, color="purple")
    ax.axvline(ALPHA_INV_EXP, color="orange", linestyle="--", linewidth=2,
               label="Exp: {:.3f}".format(ALPHA_INV_EXP))
    ax.axvline(np.mean(alpha_inv), color="red", linestyle="--",
               label="QSD mean")
    ax.set_xlabel(r"$\alpha^{-1}$")
    ax.set_title(r"Fine Structure Constant $\alpha^{-1}$")
    ax.legend(fontsize=8)

    # alpha_s
    ax = axes[1, 1]
    ax.hist(alpha_s, bins=60, density=True, alpha=0.7, color="purple")
    ax.axvline(ALPHA_S_EXP, color="orange", linestyle="--", linewidth=2,
               label="Exp: {:.4f}".format(ALPHA_S_EXP))
    ax.axvline(np.mean(alpha_s), color="red", linestyle="--",
               label="QSD mean")
    ax.set_xlabel(r"$\alpha_s$")
    ax.set_title(r"Strong Coupling $\alpha_s = 3\pi/80$")
    ax.legend(fontsize=8)

    # Correlation heatmap
    ax = axes[1, 2]
    corr_matrix, names = mc.compute_correlations()
    im = ax.imshow(corr_matrix, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(names)))
    ax.set_yticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(names, fontsize=8)
    ax.set_title("Correlation Matrix")
    plt.colorbar(im, ax=ax, shrink=0.8)
    for i in range(len(names)):
        for j in range(len(names)):
            ax.text(j, i, "{:.2f}".format(corr_matrix[i, j]),
                    ha="center", va="center",
                    color="white" if abs(corr_matrix[i, j]) > 0.5
                    else "black", fontsize=7)

    plt.suptitle("QSD Monte Carlo Analysis ({:,} samples)".format(
        mc.n_samples), fontsize=14, fontweight="bold")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print("Saved: {}".format(save_path))
    return fig


def plot_chi_square_results(chi2_results, save_path=None):
    """Visualize chi-squared test results as pull plot and p-values."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    names = list(chi2_results.keys())
    display_names = {
        "alpha_inv": r"$\alpha^{-1}$",
        "alpha_s": r"$\alpha_s$",
        "sin2_theta": r"$\sin^2\theta_W$",
        "m_higgs": r"$m_H$",
        "e_syndrome": r"$E_{\mathrm{syn}}$",
        "m_w": r"$m_W$",
    }

    pulls = []
    for n in names:
        r = chi2_results[n]
        sign = np.sign(r["qsd_val"] - r["exp_val"])
        pulls.append(r["n_sigma"] * sign)

    colors = ["green" if abs(p) < 2 else
              "orange" if abs(p) < 3 else "red" for p in pulls]

    y = np.arange(len(names))
    ax1.barh(y, pulls, color=colors, alpha=0.7, edgecolor="black")
    ax1.axvline(0, color="black", linewidth=1)
    ax1.axvline(-2, color="orange", linestyle="--", alpha=0.5)
    ax1.axvline(2, color="orange", linestyle="--", alpha=0.5)
    ax1.set_xlabel(r"Pull: (QSD $-$ Exp) / $\sigma_{\mathrm{combined}}$")
    ax1.set_title("Pull Plot")
    ax1.set_yticks(y)
    ax1.set_yticklabels([display_names.get(n, n) for n in names])
    ax1.set_xlim(-5, 5)

    for i, (name, pull) in enumerate(zip(names, pulls)):
        ax1.text(pull + 0.15 * np.sign(pull), i,
                 "{:.2f}s".format(pull), va="center", fontsize=9)

    # p-values
    p_values = [chi2_results[n]["p_value"] for n in names]
    ax2.barh(y, p_values, color="steelblue", alpha=0.7, edgecolor="black")
    ax2.axvline(0.05, color="red", linestyle="--", label="p = 0.05")
    ax2.set_xlabel("p-value")
    ax2.set_title(r"$\chi^2$ Test p-values")
    ax2.set_yticks(y)
    ax2.set_yticklabels([display_names.get(n, n) for n in names])
    ax2.set_xlim(0, 1)
    ax2.legend()

    for i, p in enumerate(zip(names, p_values)):
        status = "ok" if p[1] > 0.05 else "!"
        ax2.text(p[1] + 0.02, i,
                 "{:.3f} [{}]".format(p[1], status),
                 va="center", fontsize=9)

    plt.suptitle("Statistical Consistency: QSD vs Experiment",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print("Saved: {}".format(save_path))
    return fig


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_full_monte_carlo_analysis():
    """Run complete Monte Carlo analysis."""
    sep = "=" * 72
    subsep = "-" * 72

    print(sep)
    print("QSD MONTE CARLO ERROR PROPAGATION ANALYSIS")
    print(sep)

    np.random.seed(42)
    mc = QSDMonteCarlo(n_samples=100000)
    results = mc.run_full_analysis()

    print("\n" + sep)
    print("MONTE CARLO RESULTS (central value +/- 1-sigma)")
    print(sep)
    for name, r in results.items():
        print("  {:18s}: {:14.8f} +/- {:12.8f}  ({:.4f}%)".format(
            r.name, r.value, r.uncertainty,
            r.relative_error() * 100.0))

    print("\n" + subsep)
    print("95% CONFIDENCE INTERVALS")
    print(subsep)

    np.random.seed(42)
    m_pl_samples = mc.sample_planck_mass()
    masses = mc.compute_mass_predictions(m_pl_samples)
    alpha_inv = mc.compute_alpha_inverse()
    alpha_s = mc.compute_alpha_s()
    sin2_theta = mc.compute_sin2_theta()

    all_samples = dict(masses)
    all_samples["alpha_inv"] = alpha_inv
    all_samples["alpha_s"] = alpha_s
    all_samples["sin2_theta"] = sin2_theta

    for name, samples in all_samples.items():
        low = np.percentile(samples, 2.5)
        high = np.percentile(samples, 97.5)
        print("  {:18s}: [{:.8f}, {:.8f}]".format(name, low, high))

    print("\n" + subsep)
    print("CHI-SQUARED CONSISTENCY TESTS")
    print(subsep)

    np.random.seed(42)
    chi2_results = mc.chi_square_test()
    for name, r in chi2_results.items():
        status = "CONSISTENT" if r["consistent_2sigma"] else "TENSION"
        print("  {:18s}: chi2 = {:8.4f}, p = {:.4f}, "
              "{:.2f} sigma  [{}]".format(
                  name, r["chi2"], r["p_value"], r["n_sigma"], status))

    # Generate figures
    os.makedirs("figures", exist_ok=True)

    np.random.seed(42)
    plot_monte_carlo_distributions(mc,
                                   "figures/monte_carlo_distributions.png")
    np.random.seed(42)
    chi2_results = mc.chi_square_test()
    plot_chi_square_results(chi2_results, "figures/chi_square_results.png")

    plt.close("all")
    print("\n" + sep)
    print("MONTE CARLO ANALYSIS COMPLETE")
    print(sep)

    return mc, results, chi2_results


if __name__ == "__main__":
    run_full_monte_carlo_analysis()
