#!/usr/bin/env python3
"""
QSD Monte Carlo Error Propagation
=================================

Rigorous uncertainty quantification for QSD predictions.

This module propagates uncertainties in fundamental constants through
the QSD derivation chain to establish confidence intervals on predictions.

Author: M. Hubka
Date: February 2026
"""

import numpy as np
from scipy import stats
from dataclasses import dataclass
from typing import Tuple, Dict, List
import matplotlib.pyplot as plt

# Set random seed for reproducibility
np.random.seed(42)


@dataclass
class UncertainValue:
    """A value with associated uncertainty."""
    value: float
    uncertainty: float
    name: str = ""
    
    def __repr__(self):
        return f"{self.name}: {self.value:.6f} Â± {self.uncertainty:.6f}"
    
    def relative_error(self) -> float:
        return self.uncertainty / self.value if self.value != 0 else 0


class QSDMonteCarlo:
    """
    Monte Carlo propagation of uncertainties through QSD calculations.
    
    Input uncertainties:
    - M_Planck: Â±0.00006 Ã— 10^19 GeV (CODATA)
    - Ï†: Exact (mathematical constant)
    - ln(2): Exact (mathematical constant)
    
    Derived uncertainties propagate through:
    - Hbâ‚„ = 1/(4 ln 2)
    - Î´ = 3/(80 Ï†Â²)
    - Î¼â‚€ = (M_Pl/2^60) Ã— Ï†Â² Ã— (1 - 6Î´)
    - m_H = 5 Î¼â‚€
    - E_syn = Î¼â‚€ (1 + 8Î´)
    - Î±â»Â¹ from 3-loop calculation
    """
    
    def __init__(self, n_samples: int = 100000):
        self.n_samples = n_samples
        
        # Fundamental constants with uncertainties
        # M_Planck: 1.22089(6) Ã— 10^19 GeV
        self.M_Pl_mean = 1.22089e19
        self.M_Pl_std = 0.00006e19
        
        # Mathematical constants (exact)
        self.phi = (1 + np.sqrt(5)) / 2
        self.ln2 = np.log(2)
        
        # Experimental values for comparison
        self.alpha_inv_exp = UncertainValue(137.035999084, 0.000000021, "Î±â»Â¹ (exp)")
        self.sin2_theta_exp = UncertainValue(0.23122, 0.00003, "sinÂ²Î¸_W (exp)")
        self.m_H_exp = UncertainValue(125.10, 0.14, "m_H (exp)")
        self.E_syn_exp = UncertainValue(28.3, 0.5, "E_syn (CMS)")
        
    def sample_planck_mass(self) -> np.ndarray:
        """Sample Planck mass from Gaussian distribution."""
        return np.random.normal(self.M_Pl_mean, self.M_Pl_std, self.n_samples)
    
    def compute_derived_constants(self, M_Pl: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Compute all derived constants for each M_Pl sample.
        """
        # Exact derived constants
        Hb4 = 1 / (4 * self.ln2)
        delta = 3 / (80 * self.phi**2)
        
        # Energy scale (M_Pl dependent)
        base_energy = M_Pl / (2**60)
        phi_sq = self.phi**2
        strain_correction = 1 - 6 * delta
        mu_0 = base_energy * phi_sq * strain_correction
        
        # Derived masses/energies
        m_H = 5 * mu_0
        E_syn = mu_0 * (1 + 8 * delta)
        
        # Dimensionless VEV
        nu_0 = Hb4 / delta
        
        return {
            'Hb4': np.full(self.n_samples, Hb4),
            'delta': np.full(self.n_samples, delta),
            'mu_0': mu_0,
            'm_H': m_H,
            'E_syn': E_syn,
            'nu_0': np.full(self.n_samples, nu_0)
        }
    
    def compute_alpha_inverse(self, include_theory_uncertainty: bool = True) -> np.ndarray:
        """
        Compute Î±â»Â¹ with Monte Carlo sampling.
        
        The 3-loop calculation:
        Î±â»Â¹ = 136.826 + 0.239 - 0.022 - 0.007 = 137.036
        
        Theory uncertainties at each loop order:
        - Tree: Â±0.010 (unification scale uncertainty)
        - 1-loop: Â±0.005 (network friction model)
        - 2-loop: Â±0.003 (radion coupling)
        - 3-loop: Â±0.001 (vacuum energy)
        """
        tree = 136.826
        loop1 = 0.239
        loop2 = 0.022
        loop3 = 0.007
        
        if include_theory_uncertainty:
            tree_samples = np.random.normal(tree, 0.010, self.n_samples)
            loop1_samples = np.random.normal(loop1, 0.005, self.n_samples)
            loop2_samples = np.random.normal(loop2, 0.003, self.n_samples)
            loop3_samples = np.random.normal(loop3, 0.001, self.n_samples)
            
            alpha_inv = tree_samples + loop1_samples - loop2_samples - loop3_samples
        else:
            alpha_inv = np.full(self.n_samples, tree + loop1 - loop2 - loop3)
        
        return alpha_inv
    
    def compute_sin2_theta(self, include_theory_uncertainty: bool = True) -> np.ndarray:
        """
        Compute sinÂ²Î¸_W with Monte Carlo sampling.
        
        sinÂ²Î¸_W = 3/13 + Î´/32
        """
        delta = 3 / (80 * self.phi**2)
        tree = 3 / 13
        correction = delta / 32
        
        central = tree + correction
        
        if include_theory_uncertainty:
            return np.random.normal(central, 0.001, self.n_samples)
        else:
            return np.full(self.n_samples, central)
    
    def run_full_analysis(self) -> Dict[str, UncertainValue]:
        """Run complete Monte Carlo analysis."""
        print(f"Running Monte Carlo with {self.n_samples:,} samples...")
        
        M_Pl_samples = self.sample_planck_mass()
        derived = self.compute_derived_constants(M_Pl_samples)
        alpha_inv = self.compute_alpha_inverse(include_theory_uncertainty=True)
        sin2_theta = self.compute_sin2_theta(include_theory_uncertainty=True)
        
        results = {}
        
        for name, samples in derived.items():
            mean = np.mean(samples)
            std = np.std(samples)
            results[name] = UncertainValue(mean, std, name)
        
        results['alpha_inv'] = UncertainValue(np.mean(alpha_inv), np.std(alpha_inv), 'Î±â»Â¹')
        results['sin2_theta'] = UncertainValue(np.mean(sin2_theta), np.std(sin2_theta), 'sinÂ²Î¸_W')
        
        return results
    
    def compute_correlations(self) -> Tuple[np.ndarray, List[str]]:
        """Compute correlation matrix between QSD predictions."""
        M_Pl_samples = self.sample_planck_mass()
        derived = self.compute_derived_constants(M_Pl_samples)
        alpha_inv = self.compute_alpha_inverse()
        sin2_theta = self.compute_sin2_theta()
        
        data = np.column_stack([
            derived['mu_0'],
            derived['m_H'],
            derived['E_syn'],
            alpha_inv,
            sin2_theta
        ])
        
        names = ['Î¼â‚€', 'm_H', 'E_syn', 'Î±â»Â¹', 'sinÂ²Î¸_W']
        corr_matrix = np.corrcoef(data.T)
        
        return corr_matrix, names
    
    def compute_confidence_intervals(self, confidence: float = 0.95) -> Dict[str, Tuple[float, float]]:
        """Compute confidence intervals for all predictions."""
        M_Pl_samples = self.sample_planck_mass()
        derived = self.compute_derived_constants(M_Pl_samples)
        alpha_inv = self.compute_alpha_inverse()
        sin2_theta = self.compute_sin2_theta()
        
        alpha_low = (1 - confidence) / 2
        alpha_high = 1 - alpha_low
        
        intervals = {}
        
        for name, samples in derived.items():
            low = np.percentile(samples, alpha_low * 100)
            high = np.percentile(samples, alpha_high * 100)
            intervals[name] = (low, high)
        
        intervals['alpha_inv'] = (
            np.percentile(alpha_inv, alpha_low * 100),
            np.percentile(alpha_inv, alpha_high * 100)
        )
        intervals['sin2_theta'] = (
            np.percentile(sin2_theta, alpha_low * 100),
            np.percentile(sin2_theta, alpha_high * 100)
        )
        
        return intervals
    
    def chi_square_test(self) -> Dict[str, Dict]:
        """Perform Ï‡Â² test comparing QSD predictions to experiment."""
        results = self.run_full_analysis()
        
        comparisons = {
            'alpha_inv': (results['alpha_inv'], self.alpha_inv_exp),
            'sin2_theta': (results['sin2_theta'], self.sin2_theta_exp),
            'm_H': (results['m_H'], self.m_H_exp),
            'E_syn': (results['E_syn'], self.E_syn_exp)
        }
        
        chi2_results = {}
        
        for name, (qsd, exp) in comparisons.items():
            sigma_combined = np.sqrt(qsd.uncertainty**2 + exp.uncertainty**2)
            chi2 = ((qsd.value - exp.value) / sigma_combined)**2
            p_value = 1 - stats.chi2.cdf(chi2, df=1)
            n_sigma = abs(qsd.value - exp.value) / sigma_combined
            
            chi2_results[name] = {
                'qsd': qsd,
                'exp': exp,
                'chi2': chi2,
                'p_value': p_value,
                'n_sigma': n_sigma,
                'consistent': p_value > 0.05
            }
        
        return chi2_results


def plot_monte_carlo_distributions(mc: QSDMonteCarlo, save_path: str = None):
    """Plot distributions of Monte Carlo samples."""
    M_Pl_samples = mc.sample_planck_mass()
    derived = mc.compute_derived_constants(M_Pl_samples)
    alpha_inv = mc.compute_alpha_inverse()
    sin2_theta = mc.compute_sin2_theta()
    
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    
    # Î¼â‚€ distribution
    ax = axes[0, 0]
    ax.hist(derived['mu_0'], bins=50, density=True, alpha=0.7, color='steelblue')
    ax.axvline(np.mean(derived['mu_0']), color='red', linestyle='--', label='Mean')
    ax.set_xlabel('Î¼â‚€ (GeV)')
    ax.set_ylabel('Probability Density')
    ax.set_title('Code Scale Distribution')
    ax.legend()
    
    # m_H distribution
    ax = axes[0, 1]
    ax.hist(derived['m_H'], bins=50, density=True, alpha=0.7, color='steelblue')
    ax.axvline(125.10, color='orange', linestyle='--', linewidth=2, label='Experiment')
    ax.axvline(np.mean(derived['m_H']), color='red', linestyle='--', label='QSD Mean')
    ax.set_xlabel('m_H (GeV)')
    ax.set_ylabel('Probability Density')
    ax.set_title('Higgs Mass Distribution')
    ax.legend()
    
    # E_syn distribution
    ax = axes[0, 2]
    ax.hist(derived['E_syn'], bins=50, density=True, alpha=0.7, color='steelblue')
    ax.axvline(28.3, color='orange', linestyle='--', linewidth=2, label='CMS')
    ax.axvline(np.mean(derived['E_syn']), color='red', linestyle='--', label='QSD Mean')
    ax.set_xlabel('E_syn (GeV)')
    ax.set_ylabel('Probability Density')
    ax.set_title('Syndrome Energy Distribution')
    ax.legend()
    
    # Î±â»Â¹ distribution
    ax = axes[1, 0]
    ax.hist(alpha_inv, bins=50, density=True, alpha=0.7, color='purple')
    ax.axvline(137.035999, color='orange', linestyle='--', linewidth=2, label='Experiment')
    ax.axvline(np.mean(alpha_inv), color='red', linestyle='--', label='QSD Mean')
    ax.set_xlabel('Î±â»Â¹')
    ax.set_ylabel('Probability Density')
    ax.set_title('Fine Structure Constant Distribution')
    ax.legend()
    
    # sinÂ²Î¸_W distribution
    ax = axes[1, 1]
    ax.hist(sin2_theta, bins=50, density=True, alpha=0.7, color='purple')
    ax.axvline(0.23122, color='orange', linestyle='--', linewidth=2, label='Experiment')
    ax.axvline(np.mean(sin2_theta), color='red', linestyle='--', label='QSD Mean')
    ax.set_xlabel('sinÂ²Î¸_W')
    ax.set_ylabel('Probability Density')
    ax.set_title('Weak Mixing Angle Distribution')
    ax.legend()
    
    # Correlation heatmap
    ax = axes[1, 2]
    corr_matrix, names = mc.compute_correlations()
    im = ax.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1)
    ax.set_xticks(range(len(names)))
    ax.set_yticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha='right')
    ax.set_yticklabels(names)
    ax.set_title('Correlation Matrix')
    plt.colorbar(im, ax=ax, shrink=0.8)
    
    for i in range(len(names)):
        for j in range(len(names)):
            ax.text(j, i, f'{corr_matrix[i,j]:.2f}', ha='center', va='center',
                   color='white' if abs(corr_matrix[i,j]) > 0.5 else 'black', fontsize=9)
    
    plt.suptitle('QSD Monte Carlo Analysis', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def plot_chi_square_results(chi2_results: Dict, save_path: str = None):
    """Visualize Ï‡Â² test results."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    ax = axes[0]
    names = list(chi2_results.keys())
    pulls = [chi2_results[n]['n_sigma'] * np.sign(chi2_results[n]['qsd'].value - chi2_results[n]['exp'].value) 
             for n in names]
    colors = ['green' if abs(p) < 2 else 'orange' if abs(p) < 3 else 'red' for p in pulls]
    
    bars = ax.barh(names, pulls, color=colors, alpha=0.7, edgecolor='black')
    ax.axvline(0, color='black', linewidth=1)
    ax.axvline(-2, color='orange', linestyle='--', alpha=0.5)
    ax.axvline(2, color='orange', linestyle='--', alpha=0.5)
    ax.set_xlabel('Pull: (QSD - Exp) / Ïƒ_combined')
    ax.set_title('QSD vs Experiment: Pull Plot')
    ax.set_xlim(-4, 4)
    
    for i, (name, pull) in enumerate(zip(names, pulls)):
        ax.text(pull + 0.1 * np.sign(pull), i, f'{pull:.2f}Ïƒ', va='center', fontsize=10)
    
    ax = axes[1]
    p_values = [chi2_results[n]['p_value'] for n in names]
    
    bars = ax.barh(names, p_values, color='steelblue', alpha=0.7, edgecolor='black')
    ax.axvline(0.05, color='red', linestyle='--', label='p = 0.05')
    ax.set_xlabel('p-value')
    ax.set_title('Ï‡Â² Test p-values')
    ax.set_xlim(0, 1)
    ax.legend()
    
    for i, (name, p) in enumerate(zip(names, p_values)):
        status = 'âœ“' if p > 0.05 else 'âœ—'
        ax.text(p + 0.02, i, f'{p:.3f} {status}', va='center', fontsize=10)
    
    plt.suptitle('Statistical Consistency: QSD Predictions vs Experiment', 
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def run_full_monte_carlo_analysis():
    """Run complete Monte Carlo analysis."""
    
    print("=" * 70)
    print("QSD MONTE CARLO ERROR PROPAGATION ANALYSIS")
    print("=" * 70)
    
    mc = QSDMonteCarlo(n_samples=100000)
    results = mc.run_full_analysis()
    
    print("\n" + "=" * 70)
    print("MONTE CARLO RESULTS")
    print("=" * 70)
    
    for name, result in results.items():
        print(f"{name:12s}: {result.value:12.6f} Â± {result.uncertainty:.6f} ({result.relative_error()*100:.4f}%)")
    
    print("\n" + "-" * 70)
    print("95% CONFIDENCE INTERVALS")
    print("-" * 70)
    
    ci = mc.compute_confidence_intervals(confidence=0.95)
    for name, (low, high) in ci.items():
        print(f"{name:12s}: [{low:.6f}, {high:.6f}]")
    
    print("\n" + "-" * 70)
    print("Ï‡Â² CONSISTENCY TESTS")
    print("-" * 70)
    
    chi2_results = mc.chi_square_test()
    for name, result in chi2_results.items():
        status = "âœ“ Consistent" if result['consistent'] else "âœ— Tension"
        print(f"{name:12s}: Ï‡Â² = {result['chi2']:.4f}, p = {result['p_value']:.4f}, "
              f"{result['n_sigma']:.2f}Ïƒ  {status}")
    
    import os
    os.makedirs('figures', exist_ok=True)
    
    plot_monte_carlo_distributions(mc, 'figures/monte_carlo_distributions.png')
    plot_chi_square_results(chi2_results, 'figures/chi_square_results.png')
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    
    return mc, results, chi2_results


if __name__ == "__main__":
    run_full_monte_carlo_analysis()
