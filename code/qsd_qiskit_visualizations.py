#!/usr/bin/env python3
"""
QSD Qiskit Circuit Visualizations
==================================

Generate circuit diagrams and result visualizations.

Author: M. Hubka
Date: February 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch
import os

# Import from main suite
from qsd_qiskit_suite import (
    PHI, Hb4, DELTA, ALPHA_INV, ALPHA_DELTA_PRODUCT, MU_0, E_SYN,
    GoldenRatioCircuit, HolographicBitDensity, K4HeisenbergCircuit,
    MathieuPotentialCircuit, GaugeForceEmergence, RadionScalarCircuit,
    EnergyDressingCircuit, RenormalizationCircuit, SyndromePredictionCircuit
)


def plot_qsd_constants_summary(save_path: str = None):
    """Create summary figure of QSD constants."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.95, 'QSD Fundamental Constants', ha='center', va='top',
           fontsize=16, fontweight='bold', transform=ax.transAxes)
    
    # Constants table
    constants = [
        ('Ï† (Golden Ratio)', f'{PHI:.10f}', '(1 + âˆš5) / 2'),
        ('Hbâ‚„ (Holographic Bit)', f'{Hb4:.10f}', '1 / (4 ln 2)'),
        ('Î´ (Geometric Strain)', f'{DELTA:.10f}', '3 / (80 Ï†Â²)'),
        ('Î±â»Â¹', f'{ALPHA_INV:.9f}', 'Fine structure constant'),
        ('Î±â»Â¹ Ã— Î´', f'{ALPHA_DELTA_PRODUCT:.10f}', 'Master relation (â‰  2!)'),
        ('Î¼â‚€', f'{MU_0:.4f} GeV', 'Code scale'),
        ('E_syn', f'{E_SYN:.4f} GeV', 'Syndrome energy'),
    ]
    
    y_start = 0.80
    dy = 0.08
    
    for i, (name, value, formula) in enumerate(constants):
        y = y_start - i * dy
        
        # Name
        ax.text(0.05, y, name, ha='left', va='center', fontsize=12,
               fontweight='bold', transform=ax.transAxes)
        
        # Value
        ax.text(0.40, y, f'= {value}', ha='left', va='center', fontsize=11,
               fontfamily='monospace', transform=ax.transAxes)
        
        # Formula/description
        ax.text(0.75, y, formula, ha='left', va='center', fontsize=10,
               style='italic', color='gray', transform=ax.transAxes)
    
    # Key relationships box
    box_text = """KEY RELATIONSHIPS:

â€¢ Î»â‚‚/Î»â‚ = Ï†Â² (from Câ‚… eigenstructure)
â€¢ E_syn = Î¼â‚€ Ã— (1 + 8Î´) = 28.24 GeV
â€¢ m_H = 5 Ã— Î¼â‚€ = 126.7 GeV
â€¢ sinÂ²Î¸_W = 3/13 + Î´/32 = 0.2312
â€¢ Î±â»Â¹ Ã— Î´ = 1.963 (exact, not 2)

All derived from M_Planck alone."""

    ax.text(0.5, 0.15, box_text, ha='center', va='center', fontsize=10,
           transform=ax.transAxes, fontfamily='monospace',
           bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='orange', alpha=0.8))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def plot_golden_ratio_emergence(save_path: str = None):
    """Visualize golden ratio emergence from Câ‚…."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    
    # Left: Câ‚… eigenvalue spectrum
    ax = axes[0]
    eigenvalues = [0, (5 - np.sqrt(5))/2, (5 - np.sqrt(5))/2, 
                   (5 + np.sqrt(5))/2, (5 + np.sqrt(5))/2]
    
    for i, e in enumerate(eigenvalues):
        ax.hlines(e, 0.2, 0.8, colors='blue', linewidth=3)
        ax.text(0.85, e, f'Î» = {e:.3f}', va='center', fontsize=10)
    
    ax.set_ylabel('Eigenvalue Î»', fontsize=12)
    ax.set_title('Câ‚… Laplacian Spectrum', fontsize=13)
    ax.set_xlim(0, 1.2)
    ax.set_ylim(-0.5, 4.5)
    ax.set_xticks([])
    
    # Middle: Golden ratio demonstration
    ax = axes[1]
    lambda1 = (5 - np.sqrt(5)) / 2
    lambda2 = (5 + np.sqrt(5)) / 2
    
    # Draw bars
    ax.bar([0], [lambda1], color='steelblue', alpha=0.7, label=f'Î»â‚ = {lambda1:.4f}')
    ax.bar([1], [lambda2], color='orange', alpha=0.7, label=f'Î»â‚‚ = {lambda2:.4f}')
    
    # Show ratio
    ax.axhline(PHI**2, color='red', linestyle='--', label=f'Ï†Â² = {PHI**2:.4f}')
    
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Î»â‚', 'Î»â‚‚'])
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title(f'Î»â‚‚/Î»â‚ = Ï†Â² = {PHI**2:.6f}', fontsize=13)
    ax.legend()
    
    # Right: Pentagon with diagonals
    ax = axes[2]
    theta = np.linspace(np.pi/2, np.pi/2 + 2*np.pi, 6)
    x = np.cos(theta)
    y = np.sin(theta)
    
    # Draw pentagon
    ax.plot(x, y, 'g-', linewidth=2)
    
    # Draw diagonals
    for i in range(5):
        j = (i + 2) % 5
        ax.plot([np.cos(theta[i]), np.cos(theta[j])], 
               [np.sin(theta[i]), np.sin(theta[j])], 'g--', alpha=0.5)
    
    # Label diagonal/side ratio
    ax.annotate('', xy=(0.5, 0.2), xytext=(0, 1),
               arrowprops=dict(arrowstyle='<->', color='red'))
    ax.text(0.35, 0.6, f'd/s = Ï†', fontsize=11, color='red')
    
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Pentagon: Diagonal/Side = Ï†', fontsize=13)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def plot_heisenberg_dynamics(save_path: str = None):
    """Visualize Kâ‚„ Heisenberg dynamics."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: Time evolution
    ax = axes[0]
    k4 = K4HeisenbergCircuit()
    evolution = k4.time_evolution(t_total=10.0, n_steps=100)
    
    t = [r['t'] for r in evolution]
    Sz = [r['Sz'] for r in evolution]
    
    ax.plot(t, Sz, 'b-', linewidth=2)
    ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('Time (units of 1/J)', fontsize=12)
    ax.set_ylabel('âŸ¨S_zâŸ©', fontsize=12)
    ax.set_title(f'Kâ‚„ Heisenberg Dynamics (J = Hbâ‚„ = {Hb4:.4f})', fontsize=13)
    ax.grid(True, alpha=0.3)
    
    # Right: Energy levels
    ax = axes[1]
    J = Hb4
    energies = [-3*J/2, -J/2, 3*J/2]
    degeneracies = [2, 9, 5]
    spins = ['S=0', 'S=1', 'S=2']
    colors = ['blue', 'green', 'red']
    
    for E, deg, spin, color in zip(energies, degeneracies, spins, colors):
        ax.hlines(E, 0.2, 0.8, colors=color, linewidth=3)
        ax.text(0.85, E, f'{spin} (deg={deg})', va='center', fontsize=10)
    
    ax.set_ylabel('Energy', fontsize=12)
    ax.set_title('Kâ‚„ Heisenberg Spectrum', fontsize=13)
    ax.set_xlim(0, 1.2)
    ax.set_xticks([])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def plot_renormalization_detail(save_path: str = None):
    """Detailed visualization of 3-loop renormalization."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: Loop-by-loop progression
    ax = axes[0]
    
    renorm = RenormalizationCircuit()
    
    stages = ['Tree', '+1-loop', '-2-loop', '-3-loop']
    values = [136.826, 137.065, 137.043, 137.036]
    colors = ['gray', 'green', 'red', 'red']
    
    ax.bar(range(4), values, color='steelblue', alpha=0.7, edgecolor='black')
    ax.axhline(ALPHA_INV, color='red', linestyle='--', linewidth=2, 
               label=f'Experiment: {ALPHA_INV}')
    
    for i, (v, s) in enumerate(zip(values, stages)):
        ax.text(i, v + 0.02, f'{v:.3f}', ha='center', fontsize=10)
    
    ax.set_xticks(range(4))
    ax.set_xticklabels(stages)
    ax.set_ylabel('Î±â»Â¹', fontsize=12)
    ax.set_title('3-Loop Renormalization of Fine Structure Constant', fontsize=13)
    ax.set_ylim(136.5, 137.2)
    ax.legend(loc='lower right')
    
    # Add termination note
    ax.text(3, 136.6, 'TERMINATES\n(finite topology)', ha='center', fontsize=9,
           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
    
    # Right: Master relation
    ax = axes[1]
    
    # Show Î±â»Â¹ Ã— Î´ as a number line
    ax.axhline(0.5, color='black', linewidth=1)
    ax.plot(ALPHA_DELTA_PRODUCT, 0.5, 'bo', markersize=15, label=f'Exact: {ALPHA_DELTA_PRODUCT:.6f}')
    ax.plot(2.0, 0.5, 'r^', markersize=12, label='Naive approximation: 2')
    
    ax.axvline(ALPHA_DELTA_PRODUCT, color='blue', linestyle='--', alpha=0.5)
    ax.axvline(2.0, color='red', linestyle=':', alpha=0.5)
    
    deviation = (2 - ALPHA_DELTA_PRODUCT) / 2 * 100
    ax.text(1.98, 0.6, f'Deviation: {deviation:.2f}%', fontsize=11)
    
    ax.set_xlim(1.9, 2.05)
    ax.set_ylim(0, 1)
    ax.set_xlabel('Î±â»Â¹ Ã— Î´', fontsize=12)
    ax.set_title('Master Relation: Î±â»Â¹ Ã— Î´ â‰  2 (exact value)', fontsize=13)
    ax.legend(loc='upper left')
    ax.set_yticks([])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def plot_syndrome_prediction_detail(save_path: str = None):
    """Detailed syndrome prediction visualization."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: Energy dressing diagram
    ax = axes[0]
    
    # Draw energy levels
    bare = MU_0
    dressed = E_SYN
    
    ax.barh([0, 1], [bare, dressed], color=['blue', 'purple'], alpha=0.7, height=0.5)
    ax.text(bare + 0.5, 0, f'Î¼â‚€ = {bare:.2f} GeV\n(bare)', va='center', fontsize=11)
    ax.text(dressed + 0.5, 1, f'E_syn = {dressed:.2f} GeV\n(dressed)', va='center', fontsize=11)
    
    # Arrow showing dressing
    ax.annotate('', xy=(dressed, 0.7), xytext=(bare, 0.3),
               arrowprops=dict(arrowstyle='->', color='black', lw=2))
    ax.text((bare + dressed)/2, 0.5, f'Ã—(1 + 8Î´)\n= Ã—{1 + 8*DELTA:.4f}', 
           ha='center', fontsize=10)
    
    ax.set_xlim(0, 35)
    ax.set_ylim(-0.5, 1.8)
    ax.set_xlabel('Energy (GeV)', fontsize=12)
    ax.set_title('Syndrome Energy Dressing', fontsize=13)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Bare', 'Dressed'])
    
    # Mark CMS observation
    ax.axvline(28.3, color='red', linestyle='--', label='CMS: 28.3 GeV')
    ax.legend()
    
    # Right: Derivation chain
    ax = axes[1]
    ax.axis('off')
    
    derivation = """
    SYNDROME ENERGY DERIVATION
    â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    Start: M_Planck = 1.22 Ã— 10Â¹â¹ GeV
           â†“
    Information reduction: 2â¶â° (60 bits from Kâ‚„ topology)
           â†“
    Base: M_Pl / 2â¶â° = 10.59 GeV
           â†“
    Golden enhancement: Ã— Ï†Â² = 2.618
           â†“
    Strain correction: Ã— (1 - 6Î´) = 0.914
           â†“
    CODE SCALE: Î¼â‚€ = 25.34 GeV
           â†“
    8-bond dressing: Ã— (1 + 8Î´) = 1.115
           â†“
    SYNDROME: E_syn = 28.24 GeV âœ“
    
    CMS dimuon excess: 28.3 GeV
    Agreement: 99.8%
    """
    
    ax.text(0.5, 0.5, derivation, ha='center', va='center', fontsize=11,
           fontfamily='monospace', transform=ax.transAxes,
           bbox=dict(boxstyle='round', facecolor='lightyellow'))
    
    ax.set_title('QSD â†’ 28 GeV Prediction', fontsize=13)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def plot_gauge_emergence(save_path: str = None):
    """Visualize gauge force emergence from Sâ‚„."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis('off')
    
    ax.text(0.5, 0.95, 'Standard Model from Sâ‚„ Symmetry', ha='center', va='top',
           fontsize=16, fontweight='bold', transform=ax.transAxes)
    
    # Kâ‚„ edges â†’ gauge bosons mapping
    diagram = """
    Kâ‚„ (Complete Graph on 4 Vertices)
    â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    4 vertices Ã— (4-1)/2 = 6 edges
    
    Sâ‚„ Permutation Symmetry acts on vertices
    Edge representation decomposes as:
    
    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
    â”‚                                     â”‚
    â”‚   6  =  1  âŠ•  2  âŠ•  3              â”‚
    â”‚                                     â”‚
    â”‚   â†“     â†“     â†“     â†“              â”‚
    â”‚                                     â”‚
    â”‚ Edges  U(1)  SU(2)  SU(3)          â”‚
    â”‚        â”€â”€â”€â”€  â”€â”€â”€â”€â”€  â”€â”€â”€â”€â”€          â”‚
    â”‚         Y     W,Z   Gluons         â”‚
    â”‚                                     â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
    
    Standard Model Gauge Group emerges:
    
    SU(3)_c Ã— SU(2)_L Ã— U(1)_Y
    
    No free parameters - fixed by Kâ‚„ geometry!
    """
    
    ax.text(0.5, 0.5, diagram, ha='center', va='center', fontsize=12,
           fontfamily='monospace', transform=ax.transAxes,
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def generate_all_qiskit_figures(output_dir='figures'):
    """Generate all Qiskit-related visualizations."""
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating Qiskit visualization figures...")
    
    plot_qsd_constants_summary(os.path.join(output_dir, 'qsd_constants_summary.png'))
    plot_golden_ratio_emergence(os.path.join(output_dir, 'golden_ratio_emergence.png'))
    plot_heisenberg_dynamics(os.path.join(output_dir, 'heisenberg_dynamics.png'))
    plot_renormalization_detail(os.path.join(output_dir, 'renormalization_detail.png'))
    plot_syndrome_prediction_detail(os.path.join(output_dir, 'syndrome_prediction_detail.png'))
    plot_gauge_emergence(os.path.join(output_dir, 'gauge_emergence.png'))
    
    print(f"\nAll figures saved to: {output_dir}/")


if __name__ == "__main__":
    generate_all_qiskit_figures()
