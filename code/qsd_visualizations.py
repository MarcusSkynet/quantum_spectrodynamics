#!/usr/bin/env python3
"""
QSD Visualization Module
========================

Publication-quality figures for QSD mechanisms.
Uses LaTeX-style labels via matplotlib mathtext (no external LaTeX needed).
All constants imported from qsd_constants.py.
No unicode characters.

Author: M. Hubka
Date: February 2026
"""

import numpy as np
import matplotlib
matplotlib.rcParams["text.usetex"] = False  # use built-in mathtext
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import os

from qsd_constants import (
    GOLDEN_RATIO, GOLDEN_RATIO_SQ, HB4, SIGMA, VARPI,
    ALPHA_INV_TREE, LOOP_1, LOOP_2, LOOP_3, ALPHA_INV_QSD,
    ALPHA_S_QSD, SIN2_THETA_QSD,
    M_PLANCK_GEV, E_BASE, MU_RAD, NU_RAD,
    M_HIGGS_QSD, E_SYNDROME_QSD, M_W_QSD,
    ENTROPY_BARRIER, LAMBDA_LOG10,
    ALPHA_INV_EXP, ALPHA_S_EXP, SIN2_THETA_EXP,
    M_HIGGS_EXP, E_SYNDROME_CMS, M_W_EXP, LAMBDA_OBS_LOG10,
)

# Style settings
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.size"] = 11
plt.rcParams["axes.labelsize"] = 12
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["figure.dpi"] = 150


# =============================================================================
# 1. K4 + C5 FUNDAMENTAL STRUCTURES
# =============================================================================

def plot_k4_graph(ax=None, show_labels=True):
    """Plot the complete graph K4 (tetrahedron skeleton)."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))

    theta = np.array([0, 2 * np.pi / 3, 4 * np.pi / 3])
    r = 1.0
    nodes = {
        0: (0.0, 0.0),
        1: (r * np.cos(theta[0]), r * np.sin(theta[0])),
        2: (r * np.cos(theta[1]), r * np.sin(theta[1])),
        3: (r * np.cos(theta[2]), r * np.sin(theta[2])),
    }

    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    for i, j in edges:
        x = [nodes[i][0], nodes[j][0]]
        y = [nodes[i][1], nodes[j][1]]
        ax.plot(x, y, "b-", linewidth=2, zorder=1)

    colors = ["red", "royalblue", "royalblue", "royalblue"]
    labels = ["W\n(Anchor)", "X", "Y", "Z"] if show_labels else [""] * 4
    for i, (pos, color, label) in enumerate(
            zip(nodes.values(), colors, labels)):
        circle = Circle(pos, 0.12, facecolor=color, edgecolor="black",
                        linewidth=2, zorder=2)
        ax.add_patch(circle)
        if show_labels:
            ax.annotate(label, pos, ha="center", va="center",
                        fontsize=10, color="white", fontweight="bold")

    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(r"$K_4$: Complete Graph (Anchor + Bulk)", fontsize=14)
    return ax


def plot_c5_pentagon(ax=None, show_eigenvalues=True):
    """Plot the cycle graph C5 (pentagon) with eigenvalue annotations."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))

    n = 5
    theta = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, n, endpoint=False)
    r = 1.0
    nodes = [(r * np.cos(t), r * np.sin(t)) for t in theta]

    # Edges (cycle)
    for i in range(n):
        j = (i + 1) % n
        x = [nodes[i][0], nodes[j][0]]
        y = [nodes[i][1], nodes[j][1]]
        ax.plot(x, y, "g-", linewidth=2, zorder=1)

    # Diagonals (showing golden ratio: diagonal/side = phi)
    for i in range(n):
        j = (i + 2) % n
        x = [nodes[i][0], nodes[j][0]]
        y = [nodes[i][1], nodes[j][1]]
        ax.plot(x, y, "g--", linewidth=1, alpha=0.5, zorder=1)

    for i, pos in enumerate(nodes):
        circle = Circle(pos, 0.08, facecolor="green", edgecolor="black",
                        linewidth=2, zorder=2)
        ax.add_patch(circle)
        ax.annotate(str(i + 1), pos, ha="center", va="center",
                    fontsize=10, color="white", fontweight="bold")

    if show_eigenvalues:
        lambda_1 = (5.0 - np.sqrt(5.0)) / 2.0
        lambda_2 = (5.0 + np.sqrt(5.0)) / 2.0
        info = (r"$\lambda_1 = {:.4f}$".format(lambda_1) + "\n"
                + r"$\lambda_2 = {:.4f}$".format(lambda_2) + "\n"
                + r"$\lambda_2 / \lambda_1 = \varphi^2 = {:.4f}$".format(
                    GOLDEN_RATIO_SQ))
        ax.text(0, -0.3, info, ha="center", va="center", fontsize=10,
                bbox=dict(boxstyle="round", facecolor="lightyellow",
                          alpha=0.8))

    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.6, 1.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(r"$C_5$: Pentagon (Golden Ratio)", fontsize=14)
    return ax


def plot_k4_c5_combined(save_path=None):
    """Plot K4 and C5 side by side."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    plot_k4_graph(ax1)
    plot_c5_pentagon(ax2)
    fig.suptitle(r"QSD Fundamental Structures: $K_4 \cup C_5$",
                 fontsize=16, fontweight="bold")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        print("Saved: {}".format(save_path))
    return fig


# =============================================================================
# 2. [[5,1,3]] CODE STRUCTURE
# =============================================================================

def plot_code_513_structure(save_path=None):
    """Visualize the [[5,1,3]] code: pentagon layout + stabilizer table."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: pentagon arrangement of 5 physical qubits
    n = 5
    theta = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, n, endpoint=False)
    r = 1.0
    nodes = [(r * np.cos(t), r * np.sin(t)) for t in theta]

    # Stabilizer generator connections (each touches 4 of 5 qubits)
    stabilizers = [
        [0, 1, 2, 3],
        [1, 2, 3, 4],
        [0, 2, 3, 4],
        [0, 1, 3, 4],
    ]
    stab_colors = ["red", "blue", "green", "purple"]

    for stab, color in zip(stabilizers, stab_colors):
        for i in range(len(stab)):
            for j in range(i + 1, len(stab)):
                x = [nodes[stab[i]][0], nodes[stab[j]][0]]
                y = [nodes[stab[i]][1], nodes[stab[j]][1]]
                ax1.plot(x, y, color=color, linewidth=1, alpha=0.3)

    labels = [r"$q_1$", r"$q_2$", r"$q_3$", r"$q_4$", r"$q_5$"]
    for i, (pos, label) in enumerate(zip(nodes, labels)):
        circle = Circle(pos, 0.12, facecolor="lightblue",
                        edgecolor="black", linewidth=2, zorder=2)
        ax1.add_patch(circle)
        ax1.annotate(label, pos, ha="center", va="center",
                     fontsize=11, fontweight="bold")

    ax1.set_xlim(-1.5, 1.5)
    ax1.set_ylim(-1.5, 1.5)
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.set_title("[[5,1,3]] Code: 5 Physical Qubits", fontsize=13)

    # Right: stabilizer table
    ax2.axis("off")
    table_data = [
        ["Generator", r"$q_1$", r"$q_2$", r"$q_3$", r"$q_4$", r"$q_5$"],
        [r"$g_1$", "X", "Z", "Z", "X", "I"],
        [r"$g_2$", "I", "X", "Z", "Z", "X"],
        [r"$g_3$", "X", "I", "X", "Z", "Z"],
        [r"$g_4$", "Z", "X", "I", "X", "Z"],
    ]
    table = ax2.table(cellText=table_data, loc="center", cellLoc="center",
                      colWidths=[0.15] * 6)
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.5, 2)
    for j in range(6):
        table[(0, j)].set_facecolor("lightgray")

    ax2.set_title("Stabilizer Generators (Cyclic Structure)", fontsize=13)

    info = ("Encodes 1 logical qubit in 5 physical\n"
            "Distance 3: corrects any single error\n"
            "Perfect code (saturates quantum Hamming bound)")
    ax2.text(0.5, -0.1, info, transform=ax2.transAxes, ha="center",
             va="top", fontsize=10,
             bbox=dict(boxstyle="round", facecolor="lightyellow"))

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        print("Saved: {}".format(save_path))
    return fig


# =============================================================================
# 3. HEISENBERG SPECTRUM
# =============================================================================

def plot_heisenberg_spectrum(save_path=None):
    """Plot the K4 Heisenberg model energy levels and S4 decomposition."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    J = HB4
    energies = [-3.0 * J / 2.0, -J / 2.0, 3.0 * J / 2.0]
    degeneracies = [2, 9, 5]
    spins = ["S=0", "S=1", "S=2"]
    colors = ["blue", "green", "red"]

    for E, deg, spin, color in zip(energies, degeneracies, spins, colors):
        ax1.hlines(E, 0.2, 0.8, colors=color, linewidth=3)
        offsets = np.linspace(-0.05, 0.05, deg) if deg > 1 else [0]
        for off in offsets:
            ax1.hlines(E + off * 0.02, 0.3, 0.7, colors=color,
                       linewidth=1, alpha=0.5)
        ax1.text(0.85, E,
                 "{}\n".format(spin)
                 + r"$E = {:.1f}\,J$".format(E / J) + "\n"
                 + "deg = {}".format(deg),
                 va="center", fontsize=10)

    ax1.set_xlim(0, 1.2)
    ax1.set_ylim(-0.7, 0.7)
    ax1.set_ylabel(r"Energy (units of $J = \mathcal{H}_{b,4}$)", fontsize=12)
    ax1.set_xticks([])
    ax1.set_title(r"$K_4$ Heisenberg Spectrum ($J = {:.4f}$)".format(J),
                  fontsize=13)
    ax1.axhline(0, color="gray", linestyle="--", alpha=0.5)

    # Right: S4 decomposition
    ax2.axis("off")
    ax2.text(0.5, 0.9, r"$S_4$ Edge Representation Decomposition",
             ha="center", fontsize=13, fontweight="bold",
             transform=ax2.transAxes)
    ax2.text(0.5, 0.70,
             r"$6\;\mathrm{edges\;of}\;K_4 = \mathbf{1} \oplus "
             r"\mathbf{2} \oplus \mathbf{3}$",
             ha="center", fontsize=14, transform=ax2.transAxes)
    ax2.text(0.5, 0.52, r"$\Downarrow$", ha="center", fontsize=20,
             transform=ax2.transAxes)
    ax2.text(0.5, 0.38,
             r"$U(1)_Y \;\oplus\; SU(2)_L \;\oplus\; SU(3)_c$",
             ha="center", fontsize=13, transform=ax2.transAxes,
             color="blue")
    ax2.text(0.5, 0.18, "Standard Model Gauge Group!", ha="center",
             fontsize=12, transform=ax2.transAxes, style="italic",
             bbox=dict(boxstyle="round", facecolor="lightyellow"))

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        print("Saved: {}".format(save_path))
    return fig


# =============================================================================
# 4. RENORMALIZATION FLOW (3-loop)
# =============================================================================

def plot_renormalization_flow(save_path=None):
    """Plot the 3-loop renormalization of alpha^-1, values from triad."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Cumulative values at each loop order (derived from triad)
    stages = ["Tree", "1-loop", "2-loop", "3-loop"]
    cumulative = [
        ALPHA_INV_TREE,
        ALPHA_INV_TREE + LOOP_1,
        ALPHA_INV_TREE + LOOP_1 - LOOP_2,
        ALPHA_INV_TREE + LOOP_1 - LOOP_2 - LOOP_3,
    ]
    corrections = [0.0, LOOP_1, -LOOP_2, -LOOP_3]

    x = np.arange(len(stages))
    bars = ax.bar(x, cumulative, color="steelblue", alpha=0.7,
                  edgecolor="black")

    # Experimental reference line
    ax.axhline(y=ALPHA_INV_EXP, color="red", linestyle="--", linewidth=2,
               label=r"Experiment: $\alpha^{{-1}} = {:.6f}$".format(
                   ALPHA_INV_EXP))

    # Annotations
    for i, (val, corr) in enumerate(zip(cumulative, corrections)):
        ax.text(i, val + 0.015, "{:.3f}".format(val),
                ha="center", va="bottom", fontsize=10)
        if abs(corr) > 1.0e-10:
            sign = "+" if corr > 0 else ""
            color = "green" if corr > 0 else "red"
            ax.text(i, val - 0.06, "({}{:.4f})".format(sign, corr),
                    ha="center", va="top", fontsize=9, color=color)

    ax.set_xlabel("Loop Order", fontsize=12)
    ax.set_ylabel(r"$\alpha^{-1}$", fontsize=12)
    ax.set_title(r"QSD 3-Loop Renormalization of $\alpha^{-1}$"
                 " (derived from triad)", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(stages)
    ax.set_ylim(136.5, 137.2)
    ax.legend(loc="lower right")

    ax.text(2.5, 136.6,
            r"Series TERMINATES at 3-loop" + "\n"
            + r"($\beta_1(K_4) = 3$ independent cycles)",
            ha="center", fontsize=10, style="italic",
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        print("Saved: {}".format(save_path))
    return fig


# =============================================================================
# 5. ENERGY SCALE LADDER
# =============================================================================

def plot_energy_ladder(save_path=None):
    """Plot the QSD energy scale ladder from Planck to electroweak."""
    fig, ax = plt.subplots(figsize=(10, 8))

    # Energy scales (name, value in GeV, color, is_QSD_prediction)
    scales = [
        (r"$M_{\mathrm{Planck}}$", M_PLANCK_GEV, "darkred", False),
        (r"$M_{\mathrm{Pl}}/2^{60}$", E_BASE, "red", True),
        (r"$\mu_{\mathrm{rad}}$ (code scale)", MU_RAD, "blue", True),
        (r"$E_{\mathrm{syn}}$ (syndrome)", E_SYNDROME_QSD, "purple", True),
        (r"$m_W$ (QSD)", M_W_QSD, "teal", True),
        (r"$m_H$ (QSD)", M_HIGGS_QSD, "green", True),
    ]

    y_positions = np.arange(len(scales))
    for i, (name, energy, color, _) in enumerate(scales):
        log_e = np.log10(energy)
        ax.barh(i, log_e, color=color, alpha=0.7, height=0.6)
        ax.text(log_e + 0.3, i,
                "{}\n({:.3e} GeV)".format(name, energy),
                va="center", fontsize=9)

    # Arrows for key relationships
    ax.annotate("", xy=(np.log10(MU_RAD), 2),
                xytext=(np.log10(E_BASE), 1),
                arrowprops=dict(arrowstyle="->", color="black", lw=2))
    ax.text(5, 1.5, r"$\times\;\varphi^2(1-6\sigma)$",
            fontsize=10, ha="center")

    ax.annotate("", xy=(np.log10(M_HIGGS_QSD), 5),
                xytext=(np.log10(MU_RAD), 2),
                arrowprops=dict(arrowstyle="->", color="black", lw=2))
    ax.text(1.8, 3.5, r"$\times\;5$", fontsize=10, ha="center")

    ax.annotate("", xy=(np.log10(M_W_QSD), 4),
                xytext=(np.log10(MU_RAD), 2),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.5,
                                linestyle="dashed"))
    ax.text(1.5, 2.8, r"$\times\;16/5$", fontsize=9, ha="center",
            color="teal")

    ax.set_xlabel(r"$\log_{10}(\mathrm{Energy\;/\;GeV})$", fontsize=12)
    ax.set_ylabel("Energy Scale", fontsize=12)
    ax.set_title("QSD Energy Ladder: From Planck to Electroweak",
                 fontsize=14)
    ax.set_yticks([])
    ax.set_xlim(-1, 22)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        print("Saved: {}".format(save_path))
    return fig


# =============================================================================
# 6. PREDICTIONS vs EXPERIMENT
# =============================================================================

def plot_predictions_comparison(save_path=None):
    """Plot all QSD predictions vs experimental values."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: ratio plot (QSD/experiment) -- everything near 1.0
    names = [
        r"$\alpha^{-1}$",
        r"$\alpha_s$",
        r"$\sin^2\theta_W$",
        r"$m_H$",
        r"$E_{\mathrm{syn}}$",
        r"$m_W$",
    ]
    qsd_vals = [ALPHA_INV_QSD, ALPHA_S_QSD, SIN2_THETA_QSD,
                M_HIGGS_QSD, E_SYNDROME_QSD, M_W_QSD]
    exp_vals = [ALPHA_INV_EXP, ALPHA_S_EXP, SIN2_THETA_EXP,
                M_HIGGS_EXP, E_SYNDROME_CMS, M_W_EXP]

    ratios = [q / e for q, e in zip(qsd_vals, exp_vals)]

    y = np.arange(len(names))
    colors = ["green" if abs(r - 1.0) < 0.005 else
              "orange" if abs(r - 1.0) < 0.02 else "red" for r in ratios]

    ax1.barh(y, [r - 1.0 for r in ratios], left=1.0, color=colors,
             alpha=0.7, edgecolor="black", height=0.6)
    ax1.axvline(1.0, color="black", linewidth=1)
    ax1.set_yticks(y)
    ax1.set_yticklabels(names)
    ax1.set_xlabel("QSD / Experiment", fontsize=12)
    ax1.set_title("QSD Predictions: Ratio to Experiment", fontsize=13)
    ax1.set_xlim(0.985, 1.015)

    for i, (r, name) in enumerate(zip(ratios, names)):
        pct = (r - 1.0) * 100.0
        ax1.text(r + 0.0005 * np.sign(r - 1.0), i,
                 "{:+.3f}%".format(pct), va="center", fontsize=9)

    # Right: error magnitude on log scale
    errors_pct = [abs(q - e) / e * 100.0
                  for q, e in zip(qsd_vals, exp_vals)]

    ax2.barh(y, errors_pct, color="steelblue", alpha=0.7,
             edgecolor="black", height=0.6)
    ax2.set_xscale("log")
    ax2.set_yticks(y)
    ax2.set_yticklabels(names)
    ax2.set_xlabel("Error (%)", fontsize=12)
    ax2.set_title("Absolute Error (log scale)", fontsize=13)
    ax2.set_xlim(1e-4, 5)

    for i, err in enumerate(errors_pct):
        ax2.text(err * 1.3, i, "{:.4f}%".format(err),
                 va="center", fontsize=9)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        print("Saved: {}".format(save_path))
    return fig


# =============================================================================
# 7. COUPLING TRIANGLE (varpi at centre)
# =============================================================================

def plot_coupling_triangle(save_path=None):
    """
    Plot the gauge coupling triangle showing how all three gauge couplings
    derive from the spectral bond varpi = pi * phi^2.
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.axis("off")
    ax.set_xlim(-2, 2)
    ax.set_ylim(-1.8, 2.2)
    ax.set_aspect("equal")

    # Centre: spectral bond
    ax.text(0, 0,
            r"$\varpi = \pi\varphi^2$" + "\n"
            + "= {:.4f}".format(VARPI),
            ha="center", va="center", fontsize=14, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="gold",
                      edgecolor="black", linewidth=2))

    # Three vertices
    verts = {
        "em": (0.0, 1.8),
        "strong": (-1.6, -1.0),
        "weak": (1.6, -1.0),
    }

    # EM coupling
    ax.annotate("",
                xy=verts["em"], xytext=(0, 0.35),
                arrowprops=dict(arrowstyle="->", lw=2, color="blue"))
    ax.text(verts["em"][0], verts["em"][1],
            r"$\alpha^{-1}_{\mathrm{em}}$" + "\n"
            + r"$= 6\varpi / \mathcal{H}_{b,4}$" + "\n"
            + "= {:.3f}  (tree)".format(ALPHA_INV_TREE),
            ha="center", va="center", fontsize=11,
            bbox=dict(boxstyle="round", facecolor="lightblue"))
    ax.text(-0.6, 1.0, r"$6\;\mathrm{edges}$" + "\n"
            + r"$\div\;\mathcal{H}_{b,4}$",
            fontsize=9, ha="center", color="blue")

    # Strong coupling
    ax.annotate("",
                xy=verts["strong"], xytext=(-0.25, -0.2),
                arrowprops=dict(arrowstyle="->", lw=2, color="red"))
    ax.text(verts["strong"][0], verts["strong"][1],
            r"$\alpha_s$" + "\n"
            + r"$= \varpi \cdot \sigma$" + "\n"
            + r"$= 3\pi/80$" + "\n"
            + "= {:.5f}".format(ALPHA_S_QSD),
            ha="center", va="center", fontsize=11,
            bbox=dict(boxstyle="round", facecolor="lightyellow"))
    ax.text(-1.1, -0.3, r"$\times\;\sigma$",
            fontsize=9, ha="center", color="red")

    # Weak mixing
    ax.annotate("",
                xy=verts["weak"], xytext=(0.25, -0.2),
                arrowprops=dict(arrowstyle="->", lw=2, color="green"))
    ax.text(verts["weak"][0], verts["weak"][1],
            r"$\sin^2\theta_W$" + "\n"
            + r"$= 3/13 + \sigma/32$" + "\n"
            + "= {:.5f}".format(SIN2_THETA_QSD),
            ha="center", va="center", fontsize=11,
            bbox=dict(boxstyle="round", facecolor="lightgreen"))
    ax.text(1.1, -0.3, "generator\ncounting",
            fontsize=9, ha="center", color="green")

    # Identity at bottom
    ax.text(0, -1.65,
            r"Identity: $6\alpha_s = \alpha^{-1}_{\mathrm{tree}}"
            r" \times \mathcal{H}_{b,4} \times \sigma$",
            ha="center", fontsize=11, style="italic",
            bbox=dict(boxstyle="round", facecolor="lightyellow",
                      edgecolor="gray"))

    ax.set_title(r"QSD Coupling Triangle: all from $\varpi = \pi\varphi^2$",
                 fontsize=14, fontweight="bold")

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        print("Saved: {}".format(save_path))
    return fig


# =============================================================================
# 8. COSMOLOGICAL CONSTANT
# =============================================================================

def plot_cosmological_constant(save_path=None):
    """
    Visualize the Boltzmann suppression of the cosmological constant.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Left: energy density vs Boltzmann suppression
    sigma_range = np.linspace(0.005, 0.05, 200)
    barrier = 4.0 / sigma_range
    log10_ratio = -barrier / np.log(10.0)

    ax1.plot(sigma_range, log10_ratio, "b-", linewidth=2)
    ax1.axhline(LAMBDA_OBS_LOG10, color="red", linestyle="--", linewidth=1.5,
                label="Observed: {:.2f}".format(LAMBDA_OBS_LOG10))
    ax1.axvline(SIGMA, color="green", linestyle="--", linewidth=1.5,
                label=r"QSD $\sigma$ = {:.5f}".format(SIGMA))

    # Mark intersection
    ax1.plot(SIGMA, LAMBDA_LOG10, "ko", markersize=8, zorder=5)
    ax1.annotate("QSD: {:.2f}".format(LAMBDA_LOG10),
                 xy=(SIGMA, LAMBDA_LOG10),
                 xytext=(SIGMA + 0.008, LAMBDA_LOG10 + 15),
                 arrowprops=dict(arrowstyle="->"),
                 fontsize=10)

    ax1.set_xlabel(r"$\sigma$", fontsize=12)
    ax1.set_ylabel(r"$\log_{10}(\rho_\Lambda / \rho_{\mathrm{Pl}})$",
                   fontsize=12)
    ax1.set_title(r"Vacuum Energy: $\rho_\Lambda = \rho_{\mathrm{Pl}}"
                  r"\, e^{-4/\sigma}$", fontsize=13)
    ax1.legend(loc="lower right")

    # Right: entropy barrier visualization
    categories = ["Planck\ndensity", "Entropy\nbarrier", "Observed\nvacuum"]
    values = [0, ENTROPY_BARRIER / np.log(10.0), abs(LAMBDA_OBS_LOG10)]
    colors_bar = ["darkred", "steelblue", "green"]

    ax2.bar(categories, values, color=colors_bar, alpha=0.7,
            edgecolor="black")
    ax2.set_ylabel("Orders of magnitude", fontsize=12)
    ax2.set_title(r"121 orders from $4/\sigma = {:.1f}$ nats".format(
        ENTROPY_BARRIER), fontsize=13)

    for i, v in enumerate(values):
        if v > 0:
            ax2.text(i, v + 2, "{:.1f}".format(v),
                     ha="center", fontsize=10)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        print("Saved: {}".format(save_path))
    return fig


# =============================================================================
# GENERATE ALL FIGURES
# =============================================================================

def generate_all_figures(output_dir="figures"):
    """Generate all QSD visualization figures."""
    os.makedirs(output_dir, exist_ok=True)
    print("Generating QSD visualization figures...")

    plot_k4_c5_combined(os.path.join(output_dir, "k4_c5_structures.png"))
    plot_code_513_structure(os.path.join(output_dir, "code_513_structure.png"))
    plot_heisenberg_spectrum(os.path.join(output_dir,
                                          "heisenberg_spectrum.png"))
    plot_renormalization_flow(os.path.join(output_dir,
                                           "renormalization_3loop.png"))
    plot_energy_ladder(os.path.join(output_dir, "energy_ladder.png"))
    plot_predictions_comparison(os.path.join(output_dir,
                                             "predictions_vs_experiment.png"))
    plot_coupling_triangle(os.path.join(output_dir,
                                        "coupling_triangle.png"))
    plot_cosmological_constant(os.path.join(output_dir,
                                            "cosmological_constant.png"))

    print("\nAll figures saved to: {}/".format(output_dir))
    plt.close("all")


if __name__ == "__main__":
    generate_all_figures()
