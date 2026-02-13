#!/usr/bin/env python3
"""
QSD Syndrome Production Simulation
==================================

Simulates the production cross-section and phenomenology of the 
28 GeV syndrome resonance predicted by QSD.

Author: M. Hubka
Date: February 2026
"""

import numpy as np
from scipy import integrate, stats
import matplotlib.pyplot as plt
from typing import Tuple, Dict
from dataclasses import dataclass

# QSD Constants
PHI = (1 + np.sqrt(5)) / 2
Hb4 = 1 / (4 * np.log(2))
DELTA = 3 / (80 * PHI**2)
MU_0 = 25.34  # GeV
E_SYN = MU_0 * (1 + 8 * DELTA)  # â‰ˆ 28.24 GeV

# Standard Model Constants
M_B = 4.18  # b-quark mass (GeV)
M_Z = 91.1876  # Z boson mass (GeV)
ALPHA_S_MZ = 0.1179
G_F = 1.1663787e-5  # Fermi constant (GeV^-2)


@dataclass
class SyndromeResonance:
    """Properties of the syndrome resonance."""
    mass: float = E_SYN
    width: float = DELTA * E_SYN
    spin: int = 0
    parity: int = 1
    
    def breit_wigner(self, s: np.ndarray) -> np.ndarray:
        """Breit-Wigner propagator squared."""
        M = self.mass
        Gamma = self.width
        return 1 / ((s - M**2)**2 + (M * Gamma)**2)


class SyndromeProduction:
    """Calculate syndrome production cross-sections."""
    
    def __init__(self):
        self.resonance = SyndromeResonance()
        
    def alpha_s(self, Q: float) -> float:
        """Running strong coupling constant."""
        beta0 = 11 - 2 * 5 / 3
        if Q <= 0:
            return ALPHA_S_MZ
        L = np.log(Q**2 / M_Z**2)
        return ALPHA_S_MZ / (1 + (ALPHA_S_MZ / (2 * np.pi)) * beta0 * L)
    
    def gluon_fusion_amplitude_squared(self, sqrt_s: float) -> float:
        """Matrix element squared for gg â†’ syndrome."""
        def scalar_loop(tau):
            if tau >= 1:
                return np.arcsin(1/np.sqrt(tau))**2
            else:
                beta = np.sqrt(1 - tau)
                return -0.25 * (np.log((1 + beta)/(1 - beta)) - 1j * np.pi)**2
        
        tau_b = 4 * M_B**2 / sqrt_s**2
        A_b = tau_b * (1 + (1 - tau_b) * scalar_loop(tau_b))
        epsilon_syn = DELTA * (M_B / MU_0)**2
        A_total = A_b * (1 + epsilon_syn)
        
        return np.abs(A_total)**2
    
    def parton_level_cross_section(self, sqrt_s: float) -> float:
        """Parton-level cross section in pb."""
        s = sqrt_s**2
        alpha_s = self.alpha_s(sqrt_s)
        M_sq = self.gluon_fusion_amplitude_squared(sqrt_s)
        BW = self.resonance.breit_wigner(s)
        GeV2_to_pb = 3.894e8
        
        sigma = (np.pi * alpha_s**2) / (256 * s) * M_sq * BW * GeV2_to_pb
        return sigma
    
    def pp_cross_section_lhc(self, sqrt_s_pp: float = 13000) -> Dict:
        """Proton-proton cross section at LHC."""
        M_syn = self.resonance.mass
        tau = (M_syn / sqrt_s_pp)**2
        
        def gluon_pdf(x, Q):
            if x <= 0 or x >= 1:
                return 0
            return 3 * (1 - x)**5 / x
        
        def gluon_luminosity(tau, Q):
            def integrand(x):
                if x < tau or x > 1:
                    return 0
                return gluon_pdf(x, Q) * gluon_pdf(tau/x, Q) / x
            result, _ = integrate.quad(integrand, tau, 1)
            return result
        
        L_gg = gluon_luminosity(tau, M_syn)
        sigma_parton = self.parton_level_cross_section(M_syn)
        sigma_pp = L_gg * sigma_parton * tau
        K_factor = 2.0
        
        return {
            'sqrt_s_pp': sqrt_s_pp,
            'M_syn': M_syn,
            'sigma_pp_pb': sigma_pp * K_factor,
            'sigma_pp_fb': sigma_pp * K_factor * 1000,
            'K_factor': K_factor
        }


class SyndromeDecay:
    """Calculate syndrome decay branching ratios."""
    
    def __init__(self):
        self.M_syn = E_SYN
        self.m_b = 4.18
        self.m_c = 1.27
        self.m_tau = 1.777
        self.m_mu = 0.1057
        
    def partial_width_ff(self, m_f: float, N_c: int = 1) -> float:
        """Partial width to fermion pair."""
        if 2 * m_f >= self.M_syn:
            return 0
        
        beta = np.sqrt(1 - 4 * m_f**2 / self.M_syn**2)
        Gamma = (N_c * G_F * m_f**2 * self.M_syn) / (4 * np.pi * np.sqrt(2)) * beta**3
        
        if m_f == self.m_b:
            epsilon = 1 + DELTA * (self.m_b / MU_0)**2
            Gamma *= epsilon**2
        
        return Gamma
    
    def branching_ratios(self) -> Dict[str, float]:
        """Calculate all branching ratios."""
        widths = {
            'bb': self.partial_width_ff(self.m_b, N_c=3),
            'cc': self.partial_width_ff(self.m_c, N_c=3),
            'tautau': self.partial_width_ff(self.m_tau, N_c=1),
            'mumu': self.partial_width_ff(self.m_mu, N_c=1),
        }
        
        total = sum(widths.values())
        return {k: v/total for k, v in widths.items()}


class CMSExcessSimulator:
    """Simulate CMS 28 GeV dimuon excess."""
    
    def __init__(self, luminosity_fb: float = 140):
        self.luminosity = luminosity_fb * 1000
        self.resonance = SyndromeResonance()
        self.production = SyndromeProduction()
        self.decay = SyndromeDecay()
        
    def expected_events(self) -> Dict:
        """Calculate expected syndrome â†’ Î¼Î¼ events."""
        prod = self.production.pp_cross_section_lhc(13000)
        sigma_pp_fb = prod['sigma_pp_fb']
        BR = self.decay.branching_ratios()
        BR_mumu = BR['mumu']
        epsilon_total = 0.95 * 0.90 * 0.70
        N_expected = sigma_pp_fb * self.luminosity * BR_mumu * epsilon_total
        
        return {
            'sigma_pp_fb': sigma_pp_fb,
            'BR_mumu': BR_mumu,
            'epsilon_total': epsilon_total,
            'N_expected': N_expected
        }
    
    def generate_invariant_mass_spectrum(self, n_events: int = 10000) -> np.ndarray:
        """Generate simulated dimuon invariant mass spectrum."""
        n_signal = int(n_events * 0.01)
        
        signal_events = np.random.standard_cauchy(n_signal)
        signal_events = signal_events * self.resonance.width / 2 + self.resonance.mass
        signal_events = signal_events[(signal_events > 20) & (signal_events < 40)]
        
        n_background = n_events - len(signal_events)
        background_events = np.random.exponential(scale=15, size=n_background) + 15
        background_events = background_events[(background_events > 20) & (background_events < 40)]
        
        return np.concatenate([signal_events, background_events])
    
    def fit_bump_hunt(self, mass_spectrum: np.ndarray, 
                      mass_range: Tuple[float, float] = (26, 30)) -> Dict:
        """Perform simple bump-hunt analysis."""
        in_range = (mass_spectrum >= mass_range[0]) & (mass_spectrum <= mass_range[1])
        n_observed = np.sum(in_range)
        
        sideband_low = (mass_spectrum >= 22) & (mass_spectrum < 26)
        sideband_high = (mass_spectrum > 30) & (mass_spectrum <= 34)
        
        n_sideband = np.sum(sideband_low) + np.sum(sideband_high)
        n_background_est = n_sideband * (4 / 8)
        
        n_excess = n_observed - n_background_est
        significance = n_excess / np.sqrt(n_background_est) if n_background_est > 0 else 0
        
        return {
            'n_observed': n_observed,
            'n_background_est': n_background_est,
            'n_excess': n_excess,
            'significance': significance
        }


def plot_syndrome_spectrum(save_path: str = None):
    """Plot syndrome resonance line shape."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    resonance = SyndromeResonance()
    
    ax = axes[0]
    sqrt_s = np.linspace(25, 32, 1000)
    s = sqrt_s**2
    bw = resonance.breit_wigner(s)
    bw_norm = bw / np.max(bw)
    
    ax.plot(sqrt_s, bw_norm, 'b-', linewidth=2)
    ax.axvline(E_SYN, color='red', linestyle='--', label=f'M = {E_SYN:.2f} GeV')
    ax.fill_between(sqrt_s, bw_norm, alpha=0.3)
    ax.set_xlabel('âˆšs (GeV)')
    ax.set_ylabel('|D(s)|Â² (normalized)')
    ax.set_title(f'Syndrome Breit-Wigner (Î“ = {resonance.width:.3f} GeV)')
    ax.legend()
    ax.set_xlim(25, 32)
    
    ax = axes[1]
    decay = SyndromeDecay()
    BR = decay.branching_ratios()
    
    channels = list(BR.keys())
    values = [BR[c] * 100 for c in channels]
    colors = ['steelblue', 'orange', 'green', 'red']
    
    bars = ax.bar(channels, values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylabel('Branching Ratio (%)')
    ax.set_title('Syndrome Decay Channels')
    
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
               f'{val:.1f}%', ha='center', fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def plot_cms_excess_simulation(save_path: str = None):
    """Simulate and plot CMS-like dimuon spectrum."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    simulator = CMSExcessSimulator(luminosity_fb=140)
    mass_spectrum = simulator.generate_invariant_mass_spectrum(n_events=50000)
    
    ax = axes[0]
    bins = np.linspace(20, 40, 41)
    ax.hist(mass_spectrum, bins=bins, alpha=0.7, color='steelblue', edgecolor='black')
    ax.axvspan(26, 30, alpha=0.2, color='red', label='Signal region')
    ax.axvline(E_SYN, color='red', linestyle='--', linewidth=2, 
              label=f'QSD: E_syn = {E_SYN:.2f} GeV')
    ax.set_xlabel('m(Î¼âºÎ¼â») (GeV)')
    ax.set_ylabel('Events / 0.5 GeV')
    ax.set_title('Simulated Dimuon Invariant Mass')
    ax.legend()
    
    ax = axes[1]
    mask = (mass_spectrum > 24) & (mass_spectrum < 34)
    zoom_spectrum = mass_spectrum[mask]
    
    bins_zoom = np.linspace(24, 34, 21)
    ax.hist(zoom_spectrum, bins=bins_zoom, alpha=0.7, color='steelblue', edgecolor='black')
    ax.axvline(E_SYN, color='red', linestyle='--', linewidth=2)
    ax.axvspan(26, 30, alpha=0.2, color='red')
    
    fit = simulator.fit_bump_hunt(mass_spectrum)
    info = f"Observed: {fit['n_observed']:.0f}\n"
    info += f"Background: {fit['n_background_est']:.0f}\n"
    info += f"Excess: {fit['n_excess']:.0f}\n"
    info += f"Significance: {fit['significance']:.1f}Ïƒ"
    
    ax.text(0.98, 0.98, info, transform=ax.transAxes, ha='right', va='top',
           fontsize=10, bbox=dict(boxstyle='round', facecolor='lightyellow'))
    
    ax.set_xlabel('m(Î¼âºÎ¼â») (GeV)')
    ax.set_ylabel('Events / 0.5 GeV')
    ax.set_title('Signal Region (Zoom)')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def run_syndrome_analysis():
    """Run complete syndrome production analysis."""
    
    print("=" * 70)
    print("QSD SYNDROME PRODUCTION ANALYSIS")
    print("=" * 70)
    
    resonance = SyndromeResonance()
    print(f"\nSyndrome Resonance Properties:")
    print(f"  Mass: {resonance.mass:.3f} GeV")
    print(f"  Width: {resonance.width:.3f} GeV")
    
    production = SyndromeProduction()
    xsec = production.pp_cross_section_lhc(13000)
    
    print(f"\nProduction Cross Section (pp, âˆšs = 13 TeV):")
    print(f"  Ïƒ(pp â†’ syn + X): {xsec['sigma_pp_pb']:.4f} pb")
    print(f"  Ïƒ(pp â†’ syn + X): {xsec['sigma_pp_fb']:.1f} fb")
    
    decay = SyndromeDecay()
    BR = decay.branching_ratios()
    
    print(f"\nDecay Branching Ratios:")
    for channel, br in BR.items():
        print(f"  {channel:8s}: {br*100:6.2f}%")
    
    simulator = CMSExcessSimulator(luminosity_fb=140)
    expected = simulator.expected_events()
    
    print(f"\nCMS Dimuon Analysis (L = 140 fbâ»Â¹):")
    print(f"  Ïƒ Ã— BR(Î¼Î¼): {xsec['sigma_pp_fb'] * BR['mumu']:.4f} fb")
    print(f"  Expected events: {expected['N_expected']:.1f}")
    
    import os
    os.makedirs('figures', exist_ok=True)
    
    plot_syndrome_spectrum('figures/syndrome_spectrum.png')
    plot_cms_excess_simulation('figures/cms_excess_simulation.png')
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run_syndrome_analysis()
