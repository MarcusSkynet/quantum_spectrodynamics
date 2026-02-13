#!/usr/bin/env python3
"""
QSD Visualization Module
========================

Generates publication-quality figures for QSD mechanisms.

Author: M. Hubka
Date: February 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon, FancyArrowPatch, Circle
from matplotlib.collections import LineCollection
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import os

# Style settings
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['figure.dpi'] = 150

# QSD constants
PHI = (1 + np.sqrt(5)) / 2
Hb4 = 1 / (4 * np.log(2))
DELTA = 3 / (80 * PHI**2)


def plot_k4_graph(ax=None, show_labels=True):
    """
    Plot the complete graph Kâ‚„ (tetrahedron skeleton).
    
    Kâ‚„ has 4 nodes and 6 edges.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
    
    # Node positions (regular tetrahedron projection)
    theta = np.array([0, 2*np.pi/3, 4*np.pi/3])
    r = 1.0
    
    # Three outer nodes + one center
    nodes = {
        0: (0, 0),  # Center (anchor)
        1: (r * np.cos(theta[0]), r * np.sin(theta[0])),
        2: (r * np.cos(theta[1]), r * np.sin(theta[1])),
        3: (r * np.cos(theta[2]), r * np.sin(theta[2]))
    }
    
    # Draw edges (all 6 pairs)
    edges = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
    for i, j in edges:
        x = [nodes[i][0], nodes[j][0]]
        y = [nodes[i][1], nodes[j][1]]
        ax.plot(x, y, 'b-', linewidth=2, zorder=1)
    
    # Draw nodes
    colors = ['red', 'blue', 'blue', 'blue']  # Anchor is red
    labels = ['W\n(Anchor)', 'X', 'Y', 'Z'] if show_labels else ['', '', '', '']
    
    for i, (pos, color, label) in enumerate(zip(nodes.values(), colors, labels)):
        circle = Circle(pos, 0.12, facecolor=color, edgecolor='black', 
                       linewidth=2, zorder=2)
        ax.add_patch(circle)
        if show_labels:
            ax.annotate(label, pos, ha='center', va='center', fontsize=10,
                       color='white' if color != 'yellow' else 'black',
                       fontweight='bold')
    
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Kâ‚„: Complete Graph (Anchor + Bulk)', fontsize=14)
    
    return ax


def plot_c5_pentagon(ax=None, show_eigenvalues=True):
    """
    Plot the cycle graph Câ‚… (pentagon) with eigenvalue spectrum.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
    
    # Pentagon vertices
    n = 5
    theta = np.linspace(np.pi/2, np.pi/2 + 2*np.pi, n, endpoint=False)
    r = 1.0
    nodes = [(r * np.cos(t), r * np.sin(t)) for t in theta]
    
    # Draw edges (cycle)
    for i in range(n):
        j = (i + 1) % n
        x = [nodes[i][0], nodes[j][0]]
        y = [nodes[i][1], nodes[j][1]]
        ax.plot(x, y, 'g-', linewidth=2, zorder=1)
    
    # Draw diagonals (showing golden ratio)
    for i in range(n):
        j = (i + 2) % n
        x = [nodes[i][0], nodes[j][0]]
        y = [nodes[i][1], nodes[j][1]]
        ax.plot(x, y, 'g--', linewidth=1, alpha=0.5, zorder=1)
    
    # Draw nodes
    for i, pos in enumerate(nodes):
        circle = Circle(pos, 0.08, facecolor='green', edgecolor='black',
                       linewidth=2, zorder=2)
        ax.add_patch(circle)
        ax.annotate(str(i+1), pos, ha='center', va='center', fontsize=10,
                   color='white', fontweight='bold')
    
    # Show eigenvalue annotation
    if show_eigenvalues:
        lambda1 = (5 - np.sqrt(5)) / 2
        lambda2 = (5 + np.sqrt(5)) / 2
        info = f'Î»â‚ = {lambda1:.4f}\nÎ»â‚‚ = {lambda2:.4f}\nÎ»â‚‚/Î»â‚ = Ï†Â² = {PHI**2:.4f}'
        ax.text(0, -0.3, info, ha='center', va='center', fontsize=10,
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.6, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Câ‚…: Pentagon (Golden Ratio)', fontsize=14)
    
    return ax


def plot_k4_c5_combined(save_path=None):
    """
    Plot Kâ‚„ and Câ‚… side by side showing the fundamental QSD structures.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    plot_k4_graph(ax1)
    plot_c5_pentagon(ax2)
    
    fig.suptitle('QSD Fundamental Structures: Kâ‚„ âˆª Câ‚…', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        print(f"Saved: {save_path}")
    
    return fig


def plot_energy_ladder(save_path=None):
    """
    Plot the QSD energy scale ladder from Planck to syndrome.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Energy scales (in GeV, log scale)
    scales = {
        'M_Planck': 1.22e19,
        'M_Planck/2^60': 1.22e19 / 2**60,
        'Î¼â‚€ (Code Scale)': 25.34,
        'E_syn (Syndrome)': 28.24,
        'm_H (Higgs)': 125.1,
        'M_Z': 91.2,
        'M_W': 80.4,
    }
    
    # Colors
    colors = {
        'M_Planck': 'darkred',
        'M_Planck/2^60': 'red',
        'Î¼â‚€ (Code Scale)': 'blue',
        'E_syn (Syndrome)': 'purple',
        'm_H (Higgs)': 'green',
        'M_Z': 'orange',
        'M_W': 'orange',
    }
    
    # Plot horizontal lines
    y_positions = np.arange(len(scales))
    for i, (name, energy) in enumerate(scales.items()):
        ax.barh(i, np.log10(energy), color=colors[name], alpha=0.7, height=0.6)
        ax.text(np.log10(energy) + 0.3, i, f'{name}\n({energy:.2e} GeV)', 
               va='center', fontsize=10)
    
    # Annotations for key relationships
    ax.annotate('', xy=(np.log10(25.34), 2), xytext=(np.log10(1.22e19/2**60), 1),
               arrowprops=dict(arrowstyle='->', color='black', lw=2))
    ax.text(5, 1.5, 'Ã—Ï†Â²(1-6Î´)', fontsize=10, ha='center')
    
    ax.annotate('', xy=(np.log10(125.1), 4), xytext=(np.log10(25.34), 2),
               arrowprops=dict(arrowstyle='->', color='black', lw=2))
    ax.text(1.8, 3, 'Ã—5', fontsize=10, ha='center')
    
    ax.set_xlabel('logâ‚â‚€(Energy / GeV)', fontsize=12)
    ax.set_ylabel('Energy Scale', fontsize=12)
    ax.set_title('QSD Energy Ladder: From Planck to Electroweak', fontsize=14)
    ax.set_yticks([])
    ax.set_xlim(-1, 22)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        print(f"Saved: {save_path}")
    
    return fig


def plot_renormalization_flow(save_path=None):
    """
    Plot the 3-loop renormalization of Î±â»Â¹.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Values at each loop order
    loops = ['Tree', '1-loop', '2-loop', '3-loop']
    values = [136.826, 136.826 + 0.239, 136.826 + 0.239 - 0.022, 
              136.826 + 0.239 - 0.022 - 0.007]
    
    corrections = [0, +0.239, -0.022, -0.007]
    colors = ['gray', 'green', 'red', 'red']
    
    # Bar plot
    x = np.arange(len(loops))
    bars = ax.bar(x, values, color=['steelblue']*4, alpha=0.7, edgecolor='black')
    
    # Add experimental line
    ax.axhline(y=137.035999, color='red', linestyle='--', linewidth=2, 
               label=f'Experimental: 137.035999')
    
    # Annotations
    for i, (loop, val, corr) in enumerate(zip(loops, values, corrections)):
        ax.text(i, val + 0.02, f'{val:.3f}', ha='center', va='bottom', fontsize=10)
        if corr != 0:
            sign = '+' if corr > 0 else ''
            ax.text(i, val - 0.08, f'({sign}{corr:.3f})', ha='center', va='top', 
                   fontsize=9, color=colors[i])
    
    ax.set_xlabel('Loop Order', fontsize=12)
    ax.set_ylabel('Î±â»Â¹', fontsize=12)
    ax.set_title('QSD 3-Loop Renormalization of Fine Structure Constant', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(loops)
    ax.set_ylim(136.5, 137.2)
    ax.legend(loc='lower right')
    
    # Add text about termination
    ax.text(2.5, 136.6, 'Series TERMINATES at 3-loop\n(finite Kâ‚„âˆªCâ‚… topology)', 
           ha='center', fontsize=10, style='italic',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        print(f"Saved: {save_path}")
    
    return fig


def plot_predictions_comparison(save_path=None):
    """
    Plot QSD predictions vs experimental values.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Data
    quantities = ['Î±â»Â¹', 'sinÂ²Î¸_W', 'm_H (GeV)', 'E_syn (GeV)']
    qsd_values = [137.036, 0.2312, 126.71, 28.24]
    exp_values = [137.035999, 0.23122, 125.10, 28.3]
    errors_pct = [0.00001, 0.01, 1.28, 0.19]  # Approximate
    
    x = np.arange(len(quantities))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, qsd_values, width, label='QSD', color='steelblue', alpha=0.8)
    bars2 = ax.bar(x + width/2, exp_values, width, label='Experiment', color='orange', alpha=0.8)
    
    # Add error annotations
    for i, (q, e) in enumerate(zip(quantities, errors_pct)):
        ax.text(i, max(qsd_values[i], exp_values[i]) * 1.02, 
               f'{e:.2f}%' if e > 0.01 else f'{e*10000:.1f} ppm',
               ha='center', va='bottom', fontsize=9)
    
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title('QSD Predictions vs Experiment', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(quantities)
    ax.legend()
    
    # Use log scale for y-axis to show all values
    ax.set_yscale('log')
    ax.set_ylim(0.1, 200)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        print(f"Saved: {save_path}")
    
    return fig


def plot_code_513_structure(save_path=None):
    """
    Visualize the [[5,1,3]] code structure.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: Pentagon arrangement of 5 physical qubits
    n = 5
    theta = np.linspace(np.pi/2, np.pi/2 + 2*np.pi, n, endpoint=False)
    r = 1.0
    nodes = [(r * np.cos(t), r * np.sin(t)) for t in theta]
    
    # Draw connections (stabilizer structure)
    stabilizers = [
        [0, 1, 2, 3],  # XZZX on qubits 1,2,3,4
        [1, 2, 3, 4],  # IXZZX shifted
        [0, 2, 3, 4],  # XIXZZ
        [0, 1, 3, 4],  # ZXIXZ
    ]
    
    colors_stab = ['red', 'blue', 'green', 'purple']
    
    for stab, color in zip(stabilizers, colors_stab):
        for i in range(len(stab)):
            for j in range(i+1, len(stab)):
                x = [nodes[stab[i]][0], nodes[stab[j]][0]]
                y = [nodes[stab[i]][1], nodes[stab[j]][1]]
                ax1.plot(x, y, color=color, linewidth=1, alpha=0.3)
    
    # Draw qubits
    labels = ['qâ‚', 'qâ‚‚', 'qâ‚ƒ', 'qâ‚„', 'qâ‚…']
    for i, (pos, label) in enumerate(zip(nodes, labels)):
        circle = Circle(pos, 0.12, facecolor='lightblue', edgecolor='black',
                       linewidth=2, zorder=2)
        ax1.add_patch(circle)
        ax1.annotate(label, pos, ha='center', va='center', fontsize=11,
                    fontweight='bold')
    
    ax1.set_xlim(-1.5, 1.5)
    ax1.set_ylim(-1.5, 1.5)
    ax1.set_aspect('equal')
    ax1.axis('off')
    ax1.set_title('[[5,1,3]] Code: 5 Physical Qubits', fontsize=13)
    
    # Right: Stabilizer table
    ax2.axis('off')
    
    table_data = [
        ['Generator', 'qâ‚', 'qâ‚‚', 'qâ‚ƒ', 'qâ‚„', 'qâ‚…'],
        ['gâ‚', 'X', 'Z', 'Z', 'X', 'I'],
        ['gâ‚‚', 'I', 'X', 'Z', 'Z', 'X'],
        ['gâ‚ƒ', 'X', 'I', 'X', 'Z', 'Z'],
        ['gâ‚„', 'Z', 'X', 'I', 'X', 'Z'],
    ]
    
    table = ax2.table(cellText=table_data, loc='center', cellLoc='center',
                      colWidths=[0.15]*6)
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.5, 2)
    
    # Color header row
    for j in range(6):
        table[(0, j)].set_facecolor('lightgray')
    
    ax2.set_title('Stabilizer Generators (Cyclic Structure)', fontsize=13)
    
    # Add info text
    info = 'â€¢ Encodes 1 logical qubit in 5 physical\nâ€¢ Distance 3: corrects any single error\nâ€¢ Perfect code (saturates quantum Hamming bound)'
    ax2.text(0.5, -0.1, info, transform=ax2.transAxes, ha='center', va='top',
            fontsize=10, bbox=dict(boxstyle='round', facecolor='lightyellow'))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        print(f"Saved: {save_path}")
    
    return fig


def plot_heisenberg_spectrum(save_path=None):
    """
    Plot the Kâ‚„ Heisenberg model spectrum.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: Energy levels
    J = Hb4
    energies = [-3*J/2, -J/2, 3*J/2]
    degeneracies = [2, 9, 5]
    spins = ['S=0', 'S=1', 'S=2']
    colors = ['blue', 'green', 'red']
    
    for E, deg, spin, color in zip(energies, degeneracies, spins, colors):
        # Draw energy level
        ax1.hlines(E, 0.2, 0.8, colors=color, linewidth=3)
        # Draw degeneracy lines
        offsets = np.linspace(-0.05, 0.05, deg) if deg > 1 else [0]
        for off in offsets:
            ax1.hlines(E + off * 0.02, 0.3, 0.7, colors=color, linewidth=1, alpha=0.5)
        # Label
        ax1.text(0.85, E, f'{spin}\nE = {E/J:.1f}J\ndeg = {deg}', 
                va='center', fontsize=10)
    
    ax1.set_xlim(0, 1.2)
    ax1.set_ylim(-0.7, 0.7)
    ax1.set_ylabel('Energy (units of J = Hbâ‚„)', fontsize=12)
    ax1.set_xticks([])
    ax1.set_title(f'Kâ‚„ Heisenberg Spectrum (J = {J:.4f})', fontsize=13)
    ax1.axhline(0, color='gray', linestyle='--', alpha=0.5)
    
    # Right: Sâ‚„ representation decomposition
    ax2.axis('off')
    
    # Visual representation of 6 = 1 âŠ• 2 âŠ• 3
    ax2.text(0.5, 0.9, 'Sâ‚„ Edge Representation Decomposition', 
            ha='center', fontsize=13, fontweight='bold', transform=ax2.transAxes)
    
    ax2.text(0.5, 0.7, '6 edges of Kâ‚„  =  1 âŠ• 2 âŠ• 3', 
            ha='center', fontsize=14, transform=ax2.transAxes)
    
    ax2.text(0.5, 0.5, 'â†“', ha='center', fontsize=20, transform=ax2.transAxes)
    
    mapping = 'U(1)_Y  âŠ•  SU(2)_L  âŠ•  SU(3)_c'
    ax2.text(0.5, 0.35, mapping, ha='center', fontsize=13, 
            transform=ax2.transAxes, color='blue')
    
    ax2.text(0.5, 0.15, 'Standard Model Gauge Group!', ha='center', fontsize=12,
            transform=ax2.transAxes, style='italic',
            bbox=dict(boxstyle='round', facecolor='lightyellow'))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        print(f"Saved: {save_path}")
    
    return fig


def generate_all_figures(output_dir='figures'):
    """Generate all QSD visualization figures."""
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating QSD visualization figures...")
    
    plot_k4_c5_combined(os.path.join(output_dir, 'k4_c5_structures.png'))
    plot_energy_ladder(os.path.join(output_dir, 'energy_ladder.png'))
    plot_renormalization_flow(os.path.join(output_dir, 'renormalization_3loop.png'))
    plot_predictions_comparison(os.path.join(output_dir, 'predictions_vs_experiment.png'))
    plot_code_513_structure(os.path.join(output_dir, 'code_513_structure.png'))
    plot_heisenberg_spectrum(os.path.join(output_dir, 'heisenberg_spectrum.png'))
    
    print(f"\nAll figures saved to: {output_dir}/")
    
    plt.close('all')


if __name__ == "__main__":
    generate_all_figures()
