#!/usr/bin/env python3
"""
QSD Syndrome Production Simulation
====================================

Simulates production cross-section and phenomenology of the ~28 GeV
syndrome resonance predicted by QSD.

The syndrome is a scalar (J^P = 0^+) produced via gluon fusion,
with mass E_syn = mu_rad * (1 + 8*sigma) from anchor decoupling (S5).

All constants imported from qsd_constants.py.
No unicode characters.

Author: M. Hubka
Date: February 2026
"""

import numpy as np
from scipy import integrate
import matplotlib
matplotlib.rcParams["text.usetex"] = False
import matplotlib.pyplot as plt
from typing import Dict
import os

from qsd_constants import (
    HB4, SIGMA, MU_RAD, E_SYNDROME_QSD, E_SYNDROME_CMS,
    ALPHA_INV_QSD,
)


# Standard Model constants
M_B = 4.18          # b-quark mass (GeV)
M_C = 1.27          # c-quark mass (GeV)
M_TAU = 1.77686     # tau lepton mass (GeV)
M_MU = 0.10566      # muon mass (GeV)
M_Z = 91.1876       # Z boson mass (GeV)
ALPHA_S_MZ = 0.1179 # strong coupling at M_Z
G_FERMI = 1.1663787e-5  # Fermi constant (GeV^-2)
GEV2_TO_PB = 3.894e8    # conversion factor


class SyndromeResonance:
    """Properties of the syndrome resonance."""

    def __init__(self):
        self.mass = E_SYNDROME_QSD
        self.width = SIGMA * E_SYNDROME_QSD   # narrow: Gamma ~ 0.4 GeV
        self.spin = 0
        self.parity = +1

    def breit_wigner(self, s_values):
        """Breit-Wigner propagator squared: |D(s)|^2."""
        m = self.mass
        gamma = self.width
        return 1.0 / ((s_values - m**2)**2 + (m * gamma)**2)

    def summary(self):
        return {
            "mass_GeV": self.mass,
            "width_GeV": self.width,
            "width_over_mass": self.width / self.mass,
            "J_P": "0+",
        }


class SyndromeProduction:
    """Calculate syndrome production cross-sections at the LHC."""

    def __init__(self):
        self.resonance = SyndromeResonance()

    def alpha_s_running(self, Q):
        """Running strong coupling constant (1-loop)."""
        n_f = 5  # active flavours at Q ~ 28 GeV
        beta_0 = 11.0 - 2.0 * n_f / 3.0
        if Q <= 0:
            return ALPHA_S_MZ
        log_ratio = np.log(Q**2 / M_Z**2)
        return ALPHA_S_MZ / (1.0 + (ALPHA_S_MZ / (2.0 * np.pi))
                             * beta_0 * log_ratio)

    def scalar_triangle_function(self, tau):
        """Scalar loop function f(tau) for gg -> scalar."""
        if tau >= 1.0:
            return np.arcsin(1.0 / np.sqrt(tau))**2
        else:
            beta = np.sqrt(1.0 - tau)
            log_term = np.log((1.0 + beta) / (1.0 - beta)) - 1j * np.pi
            return -0.25 * log_term**2

    def gluon_fusion_amplitude_sq(self, sqrt_s):
        """
        |M|^2 for gg -> syndrome, via b-quark triangle loop.

        The syndrome couples to quarks proportionally to mass
        (like the SM Higgs), with an additional QSD correction
        epsilon_syn = sigma * (m_b / mu_rad)^2.
        """
        tau_b = 4.0 * M_B**2 / sqrt_s**2

        # b-quark triangle amplitude
        f_tau = self.scalar_triangle_function(tau_b)
        A_b = tau_b * (1.0 + (1.0 - tau_b) * f_tau)

        # QSD correction factor
        epsilon_syn = SIGMA * (M_B / MU_RAD)**2
        A_total = A_b * (1.0 + epsilon_syn)

        return np.abs(A_total)**2

    def parton_level_xsec(self, sqrt_s):
        """Parton-level cross section sigma(gg -> syn) in pb."""
        s = sqrt_s**2
        alpha_s = self.alpha_s_running(sqrt_s)
        m_sq = self.gluon_fusion_amplitude_sq(sqrt_s)
        bw = self.resonance.breit_wigner(s)

        return (np.pi * alpha_s**2) / (256.0 * s) * m_sq * bw * GEV2_TO_PB

    def pp_cross_section(self, sqrt_s_pp=13000.0):
        """
        Proton-proton cross section at the LHC.

        Uses a simplified gluon PDF parametrization and
        gluon-gluon luminosity integral.
        """
        m_syn = self.resonance.mass
        tau = (m_syn / sqrt_s_pp)**2

        def gluon_pdf(x, Q):
            """Simplified gluon PDF: proportional to (1-x)^5 / x."""
            if x <= 0 or x >= 1:
                return 0.0
            return 3.0 * (1.0 - x)**5 / x

        def gluon_luminosity(tau_val, Q):
            def integrand(x):
                if x < tau_val or x > 1.0:
                    return 0.0
                return gluon_pdf(x, Q) * gluon_pdf(tau_val / x, Q) / x
            result, _ = integrate.quad(integrand, tau_val, 1.0,
                                       limit=100)
            return result

        L_gg = gluon_luminosity(tau, m_syn)
        sigma_parton = self.parton_level_xsec(m_syn)
        sigma_pp = L_gg * sigma_parton * tau

        # K-factor for higher-order QCD corrections
        K_factor = 2.0

        return {
            "sqrt_s_pp_GeV": sqrt_s_pp,
            "M_syn_GeV": m_syn,
            "tau": tau,
            "gluon_luminosity": L_gg,
            "sigma_parton_pb": sigma_parton,
            "sigma_pp_pb": sigma_pp * K_factor,
            "sigma_pp_fb": sigma_pp * K_factor * 1000.0,
            "K_factor": K_factor,
        }


class SyndromeDecay:
    """Calculate syndrome decay branching ratios."""

    def __init__(self):
        self.m_syn = E_SYNDROME_QSD

    def partial_width_ff(self, m_f, n_c=1):
        """
        Partial width to fermion-antifermion pair.
        Mass-proportional coupling (like SM Higgs).
        """
        if 2.0 * m_f >= self.m_syn:
            return 0.0

        beta = np.sqrt(1.0 - 4.0 * m_f**2 / self.m_syn**2)
        gamma = (n_c * G_FERMI * m_f**2 * self.m_syn) / (
            4.0 * np.pi * np.sqrt(2.0)) * beta**3

        # Enhanced b-quark coupling in QSD
        if abs(m_f - M_B) < 0.01:
            epsilon = 1.0 + SIGMA * (M_B / MU_RAD)**2
            gamma *= epsilon**2

        return gamma

    def branching_ratios(self):
        """Calculate all kinematically allowed branching ratios."""
        widths = {
            "bb":      self.partial_width_ff(M_B, n_c=3),
            "cc":      self.partial_width_ff(M_C, n_c=3),
            "tau_tau": self.partial_width_ff(M_TAU, n_c=1),
            "mu_mu":   self.partial_width_ff(M_MU, n_c=1),
        }
        total = sum(widths.values())
        if total < 1.0e-30:
            return {k: 0.0 for k in widths}
        return {k: v / total for k, v in widths.items()}


class CMSExcessSimulator:
    """Simulate CMS-like 28 GeV dimuon excess."""

    def __init__(self, luminosity_inv_fb=140.0):
        self.luminosity_inv_pb = luminosity_inv_fb * 1000.0
        self.resonance = SyndromeResonance()
        self.production = SyndromeProduction()
        self.decay = SyndromeDecay()

    def expected_events(self):
        """Calculate expected syndrome -> mu mu events at CMS."""
        prod = self.production.pp_cross_section(13000.0)
        sigma_fb = prod["sigma_pp_fb"]
        br = self.decay.branching_ratios()
        br_mu_mu = br["mu_mu"]

        # Detector efficiencies (CMS-like)
        eff_trigger = 0.95
        eff_reco = 0.90
        eff_selection = 0.70
        eff_total = eff_trigger * eff_reco * eff_selection

        n_expected = (sigma_fb * self.luminosity_inv_pb / 1000.0
                      * br_mu_mu * eff_total)

        return {
            "sigma_pp_fb": sigma_fb,
            "BR_mu_mu": br_mu_mu,
            "efficiency": eff_total,
            "N_expected": n_expected,
            "luminosity_inv_fb": self.luminosity_inv_pb / 1000.0,
        }

    def generate_invariant_mass(self, n_events=10000):
        """Generate simulated dimuon invariant mass spectrum."""
        n_signal = int(n_events * 0.01)  # 1% signal fraction

        # Signal: Cauchy (Breit-Wigner)
        signal = np.random.standard_cauchy(n_signal)
        signal = signal * self.resonance.width / 2.0 + self.resonance.mass
        signal = signal[(signal > 20.0) & (signal < 40.0)]

        # Background: exponential
        n_bg = n_events - len(signal)
        background = np.random.exponential(scale=15.0, size=n_bg) + 15.0
        background = background[(background > 20.0) & (background < 40.0)]

        return np.concatenate([signal, background])

    def bump_hunt(self, mass_spectrum, signal_window=(26.0, 30.0)):
        """Simple sideband-subtraction bump hunt."""
        in_signal = ((mass_spectrum >= signal_window[0])
                     & (mass_spectrum <= signal_window[1]))
        n_observed = np.sum(in_signal)

        sideband_low = ((mass_spectrum >= 22.0)
                        & (mass_spectrum < signal_window[0]))
        sideband_high = ((mass_spectrum > signal_window[1])
                         & (mass_spectrum <= 34.0))
        n_sideband = np.sum(sideband_low) + np.sum(sideband_high)

        window_width = signal_window[1] - signal_window[0]
        sideband_width = (signal_window[0] - 22.0) + (34.0 - signal_window[1])
        n_bg_est = n_sideband * (window_width / sideband_width)

        n_excess = n_observed - n_bg_est
        if n_bg_est > 0:
            significance = n_excess / np.sqrt(n_bg_est)
        else:
            significance = 0.0

        return {
            "n_observed": int(n_observed),
            "n_background_est": n_bg_est,
            "n_excess": n_excess,
            "significance_sigma": significance,
        }


# =============================================================================
# PLOTTING
# =============================================================================

def plot_syndrome_spectrum(save_path=None):
    """Plot syndrome resonance line shape and decay channels."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    resonance = SyndromeResonance()

    # Left: Breit-Wigner line shape
    sqrt_s = np.linspace(25.0, 32.0, 1000)
    s = sqrt_s**2
    bw = resonance.breit_wigner(s)
    bw_norm = bw / np.max(bw)

    ax1.plot(sqrt_s, bw_norm, "b-", linewidth=2)
    ax1.axvline(E_SYNDROME_QSD, color="red", linestyle="--",
                label=r"$M = {:.2f}$ GeV".format(E_SYNDROME_QSD))
    ax1.fill_between(sqrt_s, bw_norm, alpha=0.3)
    ax1.set_xlabel(r"$\sqrt{s}$ (GeV)")
    ax1.set_ylabel(r"$|D(s)|^2$ (normalized)")
    ax1.set_title(r"Syndrome Breit-Wigner ($\Gamma = {:.3f}$ GeV)".format(
        resonance.width))
    ax1.legend()
    ax1.set_xlim(25.0, 32.0)

    # Right: branching ratios
    decay = SyndromeDecay()
    br = decay.branching_ratios()
    channels = list(br.keys())
    display_labels = [r"$b\bar{b}$", r"$c\bar{c}$",
                      r"$\tau^+\tau^-$", r"$\mu^+\mu^-$"]
    values = [br[c] * 100.0 for c in channels]
    colors = ["steelblue", "orange", "green", "red"]

    bars = ax2.bar(display_labels, values, color=colors, alpha=0.7,
                   edgecolor="black")
    ax2.set_ylabel("Branching Ratio (%)")
    ax2.set_title("Syndrome Decay Channels")

    for bar, val in zip(bars, values):
        ax2.text(bar.get_x() + bar.get_width() / 2.0,
                 bar.get_height() + 1.0,
                 "{:.2f}%".format(val), ha="center", fontsize=10)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print("Saved: {}".format(save_path))
    return fig


def plot_cms_excess_simulation(save_path=None):
    """Simulate and plot CMS-like dimuon spectrum."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    np.random.seed(42)
    simulator = CMSExcessSimulator(luminosity_inv_fb=140.0)
    mass_spectrum = simulator.generate_invariant_mass(n_events=50000)

    # Left: full spectrum
    bins = np.linspace(20.0, 40.0, 41)
    ax1.hist(mass_spectrum, bins=bins, alpha=0.7, color="steelblue",
             edgecolor="black")
    ax1.axvspan(26, 30, alpha=0.2, color="red", label="Signal region")
    ax1.axvline(E_SYNDROME_QSD, color="red", linestyle="--", linewidth=2,
                label=r"QSD: $E_{{\mathrm{{syn}}}} = {:.2f}$ GeV".format(
                    E_SYNDROME_QSD))
    ax1.set_xlabel(r"$m(\mu^+\mu^-)$ (GeV)")
    ax1.set_ylabel("Events / 0.5 GeV")
    ax1.set_title("Simulated Dimuon Invariant Mass")
    ax1.legend(fontsize=9)

    # Right: zoom on signal region
    mask = (mass_spectrum > 24.0) & (mass_spectrum < 34.0)
    zoom_spectrum = mass_spectrum[mask]
    bins_zoom = np.linspace(24.0, 34.0, 21)
    ax2.hist(zoom_spectrum, bins=bins_zoom, alpha=0.7, color="steelblue",
             edgecolor="black")
    ax2.axvline(E_SYNDROME_QSD, color="red", linestyle="--", linewidth=2)
    ax2.axvspan(26, 30, alpha=0.2, color="red")

    fit = simulator.bump_hunt(mass_spectrum)
    info = ("Observed: {:.0f}\n".format(fit["n_observed"])
            + "Background: {:.0f}\n".format(fit["n_background_est"])
            + "Excess: {:.0f}\n".format(fit["n_excess"])
            + "Significance: {:.1f} sigma".format(
                fit["significance_sigma"]))
    ax2.text(0.98, 0.98, info, transform=ax2.transAxes,
             ha="right", va="top", fontsize=10,
             bbox=dict(boxstyle="round", facecolor="lightyellow"))

    ax2.set_xlabel(r"$m(\mu^+\mu^-)$ (GeV)")
    ax2.set_ylabel("Events / 0.5 GeV")
    ax2.set_title("Signal Region (Zoom)")

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print("Saved: {}".format(save_path))
    return fig


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_syndrome_analysis():
    """Run complete syndrome production analysis."""
    sep = "=" * 72

    print(sep)
    print("QSD SYNDROME PRODUCTION ANALYSIS")
    print(sep)

    resonance = SyndromeResonance()
    props = resonance.summary()
    print("\nSyndrome Resonance Properties:")
    print("  Mass:   {:.4f} GeV".format(props["mass_GeV"]))
    print("  Width:  {:.4f} GeV".format(props["width_GeV"]))
    print("  G/M:    {:.6f}".format(props["width_over_mass"]))
    print("  J^P:    {}".format(props["J_P"]))

    production = SyndromeProduction()
    xsec = production.pp_cross_section(13000.0)
    print("\nProduction Cross Section (pp, sqrt(s) = 13 TeV):")
    print("  sigma(pp -> syn + X): {:.6f} pb".format(xsec["sigma_pp_pb"]))
    print("  sigma(pp -> syn + X): {:.3f} fb".format(xsec["sigma_pp_fb"]))

    decay = SyndromeDecay()
    br = decay.branching_ratios()
    print("\nDecay Branching Ratios:")
    for channel, ratio in br.items():
        print("  {:10s}: {:8.4f}%".format(channel, ratio * 100.0))

    simulator = CMSExcessSimulator(luminosity_inv_fb=140.0)
    expected = simulator.expected_events()
    print("\nCMS Dimuon Analysis (L = 140 fb^-1):")
    print("  sigma * BR(mu mu): {:.6f} fb".format(
        xsec["sigma_pp_fb"] * br["mu_mu"]))
    print("  Expected events:   {:.2f}".format(expected["N_expected"]))

    os.makedirs("figures", exist_ok=True)
    plot_syndrome_spectrum("figures/syndrome_spectrum.png")
    plot_cms_excess_simulation("figures/cms_excess_simulation.png")
    plt.close("all")

    print("\n" + sep)
    print("SYNDROME ANALYSIS COMPLETE")
    print(sep)


if __name__ == "__main__":
    run_syndrome_analysis()
